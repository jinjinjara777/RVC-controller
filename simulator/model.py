"""Grid environment only. All control decisions come from the compiled C CLI."""
from copy import deepcopy
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'build' / ('rvc_cli.exe' if os.name == 'nt' else 'rvc_cli')
VECTORS = [(0,-1),(1,0),(0,1),(-1,0)]

def cell(value):
    if not isinstance(value,list) or len(value)!=2 or any(type(v) is not int or not 0<=v<10 for v in value):
        raise ValueError('좌표는 0~9 사이의 정수 [x,y]여야 합니다.')
    return tuple(value)

def validate(config):
    if not isinstance(config,dict): raise ValueError('지도를 JSON 객체로 지정하세요.')
    start=cell(config.get('start',[4,4]))
    direction=config.get('direction',0)
    limit=config.get('max_ticks',100)
    if type(direction) is not int or direction not in range(4): raise ValueError('방향은 0~3이어야 합니다.')
    if type(limit) is not int or not 1<=limit<=100: raise ValueError('틱 제한은 1~100이어야 합니다.')
    obstacles=config.get('obstacles',[]); dust=config.get('dust',[])
    if not isinstance(obstacles,list) or not isinstance(dust,list) or len(obstacles)>100 or len(dust)>100:
        raise ValueError('장애물·먼지 목록은 최대 100칸입니다.')
    obstacles={cell(p) for p in obstacles}; dust={cell(p) for p in dust}
    if start in obstacles: raise ValueError('시작 위치에 장애물을 놓을 수 없습니다.')
    if obstacles & dust: raise ValueError('장애물과 먼지가 같은 칸에 있습니다.')
    name=config.get('name','사용자 지도')
    if not isinstance(name,str) or not name.strip() or len(name)>100: raise ValueError('지도 이름을 1~100자로 지정하세요.')
    result={'name':name.strip(),'start':list(start),'direction':direction,'max_ticks':limit,
            'obstacles':[list(p) for p in sorted(obstacles)],'dust':[list(p) for p in sorted(dust)]}
    for key in ('id','requirements','functions','expected','sa'):
        if key in config:
            value=config[key]
            if key in ('requirements','functions','sa'):
                if not isinstance(value,list) or len(value)>20 or any(not isinstance(v,str) or len(v)>200 for v in value):
                    raise ValueError(f'{key}는 문자열 목록이어야 합니다.')
            elif not isinstance(value,str) or len(value)>2000:
                raise ValueError(f'{key}는 문자열이어야 합니다.')
            result[key]=deepcopy(value)
    return result

class Simulation:
    def __init__(self,config):
        self.config=validate(config)
        self.position=tuple(self.config['start']); self.direction=self.config['direction']
        self.obstacles={tuple(p) for p in self.config['obstacles']}
        self.dust={tuple(p) for p in self.config['dust']}
        self.cleaned=set(); self.mopped=set(); self.inputs=[]
        self.evaluation={'result':'PENDING','evaluator':'','notes':'','ticks':''}
        self.history=[self.snapshot(None,None,False,[])]

    def blocked(self,p):
        return not (0<=p[0]<10 and 0<=p[1]<10) or p in self.obstacles

    def sensors(self):
        def adjacent(direction):
            dx,dy=VECTORS[direction%4]
            return self.blocked((self.position[0]+dx,self.position[1]+dy))
        return {'front':int(adjacent(self.direction)), 'left':int(adjacent(self.direction-1)),
                'right':int(adjacent(self.direction+1)), 'dust':int(self.position in self.dust)}

    def snapshot(self,controller,sensors,collision,changes):
        return {'tick':len(self.inputs),'position':list(self.position),'direction':self.direction,
                'controller':controller,'sensors':sensors,'collision':collision,'changes':changes,
                'dust':[list(p) for p in sorted(self.dust)],'cleaned':[list(p) for p in sorted(self.cleaned)],
                'mopped':[list(p) for p in sorted(self.mopped)]}

    def step(self):
        if len(self.inputs)>=self.config['max_ticks']: raise ValueError('최대 틱에 도달했습니다. 재설정 후 실행하세요.')
        sensed=self.sensors()
        row=' '.join(str(sensed[k]) for k in ('front','left','right','dust'))+'\n'
        script=''.join(self.inputs)+row
        result=subprocess.run([str(CLI)],input=script,text=True,capture_output=True,timeout=5,
                              creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode: raise RuntimeError(f'C 제어기 오류 ({result.returncode}): {result.stderr[:300]}')
        lines=result.stdout.splitlines()
        if len(lines)!=len(self.inputs)+1: raise RuntimeError('C 제어기 응답 틱 수가 일치하지 않습니다.')
        control=json.loads(lines[-1]); changes=[]; collision=False
        if control['cleaner']['enabled']:
            self.cleaned.add(self.position)
            if self.position in self.dust:
                self.dust.remove(self.position); changes.append('먼지 제거')
        if control['cleaner']['mop']: self.mopped.add(self.position)
        motor=control['motor']
        if motor in ('FORWARD','BACKWARD'):
            dx,dy=VECTORS[self.direction]; sign=1 if motor=='FORWARD' else -1
            destination=(self.position[0]+sign*dx,self.position[1]+sign*dy)
            if self.blocked(destination): collision=True; changes.append('환경이 이동 차단')
            else: self.position=destination; changes.append('전진' if sign==1 else '후진')
        elif motor in ('TURN_LEFT','TURN_RIGHT'):
            self.direction=(self.direction+(-1 if motor=='TURN_LEFT' else 1))%4
            changes.append('좌회전' if motor=='TURN_LEFT' else '우회전')
        else: raise RuntimeError('알 수 없는 C 이동 명령')
        self.inputs.append(row)
        frame=self.snapshot(control,sensed,collision,changes)
        self.history.append(frame)
        return deepcopy(frame)

    def export(self):
        return {'profile':'P1','config':deepcopy(self.config),'history':deepcopy(self.history),
                'evaluation':deepcopy(self.evaluation)}
