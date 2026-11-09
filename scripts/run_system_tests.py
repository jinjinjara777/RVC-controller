"""Execute real C-backed traces; verify simulator mechanics, leave human oracle pending."""
from pathlib import Path
import json
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'simulator'))
from model import Simulation, CLI, VECTORS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/SystemTest';(OUT/'traces').mkdir(parents=True,exist_ok=True)
cases=json.loads((ROOT/'simulator/scenarios.json').read_text(encoding='utf-8'))
assert len(cases)>=20
assert len({json.dumps([c['start'],c['direction'],c['obstacles'],c['dust']]) for c in cases})==len(cases)
summary=[]
for case in cases:
    assert len(case['functions'])>=3 and len(case['requirements'])>=3
    sim=Simulation(case);observed=set();collisions=0
    for tick in range(1,case['max_ticks']+1):
        before=sim.history[-1];sensors=sim.sensors()
        frame=sim.step();c=frame['controller'];motor=c['motor']
        assert frame['tick']==c['tick']==tick
        assert frame['sensors']==c['sensors']==sensors
        assert len(sim.history)==tick+1
        position=tuple(frame['position']);assert not sim.blocked(position)
        direction=before['direction'];expected=tuple(before['position'])
        if motor in ('FORWARD','BACKWARD'):
            dx,dy=VECTORS[direction];sign=1 if motor=='FORWARD' else -1
            target=(expected[0]+sign*dx,expected[1]+sign*dy)
            if not sim.blocked(target): expected=target
            assert frame['direction']==direction
        else:
            assert frame['direction']==(direction+(-1 if motor=='TURN_LEFT' else 1))%4
        assert position==expected
        if c['cleaner']['enabled']:
            assert before['position'] in frame['cleaned']
            assert before['position'] not in frame['dust']
            observed.add('R1')
        if c['cleaner']['mop']: assert before['position'] in frame['mopped']
        if motor=='FORWARD' and c['cleaner']['enabled']: observed.add('R2')
        if motor.startswith('TURN_') and not c['cleaner']['enabled']: observed.add('R3')
        if motor=='BACKWARD': observed.add('R4')
        if c['cleaner']['power']==2: observed.add('R5')
        assert 0<=c['boost_remaining']<=2
        assert c['cleaner']['enabled']==c['cleaner']['mop']
        assert c['cleaner']['enabled'] or c['cleaner']['power']==0
        collisions+=int(frame['collision'])
    old=len(sim.history)
    try: sim.step()
    except ValueError: pass
    else: raise AssertionError('Tick limit was not enforced')
    assert len(sim.history)==old
    # One-shot C execution must equal every recorded C response from replayed stepping.
    replay=subprocess.run([str(CLI)],input=''.join(sim.inputs),text=True,capture_output=True,check=True,timeout=5)
    assert [json.loads(line) for line in replay.stdout.splitlines()]==[f['controller'] for f in sim.history[1:]]
    assert len(observed)>=3
    assert sim.evaluation['result']=='PENDING'
    (OUT/'traces'/f'{case["id"]}.json').write_text(json.dumps(sim.export(),ensure_ascii=False,indent=2),encoding='utf-8')
    summary.append({'id':case['id'],'ticks':len(sim.inputs),'snapshots':len(sim.history),
                    'observed_requirements':sorted(observed),'blocked_moves':collisions,'human_result':'PENDING'})
    print(f'{case["id"]}: {len(sim.inputs)} ticks, {len(sim.history)} snapshots, human=PENDING',flush=True)
(OUT/'execution_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
text='# RVC System Test Execution Results\n\n実行日: 2026-11-06 (Asia/Seoul).\n\n'
text=text.replace('実行日','실행일')
text+='명령: `python scripts/run_system_tests.py`. 실제 GCC C11 실행 파일로 20개 시나리오를 각각 100틱까지 실행했다. 자동 검사는 환경 모델의 위치·센서·기록·틱 제한 및 C 응답 일치에 대한 구현 검사이다. 시스템 시나리오의 PASS/FAIL은 사람이 정하며 **모두 평가 대기**이다.\n\n| Scenario | Ticks | Snapshots | 관찰된 동작의 요구사항 | 이동 차단 | Human Result | Trace |\n|---|---|---|---|---|---|---|\n'
for row in summary:
 text+=f'| {row["id"]} | {row["ticks"]} | {row["snapshots"]} | {", ".join(row["observed_requirements"])} | {row["blocked_moves"]} | PENDING | [JSON](traces/{row["id"]}.json) |\n'
text+='\n전체 2,000틱과 초기 상태를 포함한 2,020개 snapshot을 보존했다. 틱 0의 controller/sensors는 첫 C 업데이트 전이므로 null이며 가상의 센서나 타이머 값을 만들지 않는다.\n\n실제 사람의 평가는 웹 화면에서 PASS/FAIL/INCONCLUSIVE, 평가자, 관련 틱, 관찰 내용을 입력해 기록한다. 저장 결과는 `simulator/saved/result-*.json`에 실행 전체와 함께 보존된다.\n'
(OUT/'test_results.md').write_text(text,encoding='utf-8')
print('Simulator mechanics checks completed; scenario verdicts remain PENDING.',flush=True)
