"""Local-only web server. Run: python simulator/server.py"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import RLock
from urllib.parse import urlsplit
import argparse
import json
import time
import uuid
from model import Simulation, validate, CLI

HERE=Path(__file__).resolve().parent
SAVED=HERE/'saved'
sessions={}; lock=RLock()

def scenarios():
    configs=json.loads((HERE/'scenarios.json').read_text(encoding='utf-8'))
    if SAVED.exists():
        for path in sorted(SAVED.glob('map-*.json')):
            configs.append(json.loads(path.read_text(encoding='utf-8')))
    return configs

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(HERE/'web'),**kwargs)
    def log_message(self,format,*args): pass
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def reply(self,data,status=200):
        body=json.dumps(data,ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=='/api/scenarios': return self.reply(scenarios())
        if path=='/api/health': return self.reply({'controller':str(CLI),'ready':CLI.exists(),'profile':'P1'})
        if path.startswith('/api/trace/'):
            with lock:
                session=sessions.get(path.rsplit('/',1)[-1])
                return self.reply(session['sim'].export() if session else {'error':'세션 없음'},200 if session else 404)
        if path.startswith('/api/'): return self.reply({'error':'지원하지 않는 API'},404)
        return super().do_GET()
    def do_POST(self):
        try:
            if self.headers.get('Origin') and self.headers['Origin']!=f'http://{self.headers.get("Host")}':
                raise ValueError('같은 로컬 화면에서 요청하세요.')
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=65536: raise ValueError('요청 크기는 1~65536 바이트여야 합니다.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError('JSON 객체가 필요합니다.')
            with lock:
                path=urlsplit(self.path).path
                if path=='/api/new':
                    sim=Simulation(data['config']); sid=uuid.uuid4().hex
                    # Bound abandoned browser sessions without affecting recent activity.
                    for old in list(sessions):
                        if time.monotonic()-sessions[old]['used']>3600: del sessions[old]
                    if len(sessions)>=128: raise ValueError('열린 세션이 많습니다. 서버를 재시작하세요.')
                    sessions[sid]={'sim':sim,'used':time.monotonic()}
                    previous=data.get('replace')
                    if isinstance(previous,str) and previous!=sid: sessions.pop(previous,None)
                    return self.reply({'id':sid,'frame':sim.history[0],'config':sim.config})
                if path=='/api/scenarios':
                    config=validate(data['config']); config['id']='CUSTOM-'+uuid.uuid4().hex[:8]
                    SAVED.mkdir(exist_ok=True)
                    (SAVED/f'map-{config["id"]}.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
                    return self.reply(config)
                sid=data.get('id'); session=sessions.get(sid)
                if not session: raise ValueError('실행 세션이 없습니다. 재설정하세요.')
                session['used']=time.monotonic(); sim=session['sim']
                if path=='/api/step': return self.reply(sim.step())
                if path=='/api/evaluate':
                    evaluation=data.get('evaluation',{})
                    if evaluation.get('result') not in ('PASS','FAIL','INCONCLUSIVE'): raise ValueError('평가 결과를 선택하세요.')
                    if not str(evaluation.get('evaluator','')).strip(): raise ValueError('평가자를 입력하세요.')
                    if not sim.inputs: raise ValueError('최소 1틱을 실행한 뒤 평가하세요.')
                    sim.evaluation={k:str(evaluation.get(k,''))[:4000] for k in ('result','evaluator','notes','ticks')}
                    SAVED.mkdir(exist_ok=True)
                    (SAVED/f'result-{sid}.json').write_text(json.dumps(sim.export(),ensure_ascii=False,indent=2),encoding='utf-8')
                    return self.reply(sim.evaluation)
                return self.reply({'error':'지원하지 않는 API'},404)
        except (ValueError,KeyError,TypeError) as exc: self.reply({'error':str(exc)},400)
        except Exception as exc: self.reply({'error':str(exc)},500)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); args=parser.parse_args()
    if not CLI.exists(): raise SystemExit('C 제어기를 먼저 빌드하세요. README.md를 참고하세요.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'RVC Simulator: http://127.0.0.1:{args.port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
