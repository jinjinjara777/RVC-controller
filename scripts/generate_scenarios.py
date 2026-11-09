"""Generate explicit, orientation-varied 10x10 scenario maps and review sheets."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'artifacts/SystemTest';out.mkdir(parents=True,exist_ok=True)
vectors=[(0,-1),(1,0),(0,1),(-1,0)]
names=['먼지 경로와 전방 회피','좌측 막힘과 우회전','세 방향 막힘과 후진','좁은 통로의 강화 청소','연속 벽과 방향 재판단']
patterns=[[(0,2)],[(0,1),(-1,0)],[(0,1),(-1,0),(1,0)],
          [(-1,0),(1,0),(-1,1),(1,1),(-1,2),(1,2),(0,3)],[(0,2),(-1,2),(-2,2),(2,0)]]
cases=[]
for kind,pattern in enumerate(patterns):
 for direction in range(4):
    forward=vectors[direction]; right=vectors[(direction+1)%4]
    def at(lateral,ahead):
        return [4+right[0]*lateral+forward[0]*ahead,4+right[1]*lateral+forward[1]*ahead]
    obstacles=[at(*p) for p in pattern]
    dust=[at(0,0),at(0,-1),at(-2,-1)]
    expected='직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.'
    functions=['자동 청소·물걸레','직진','장애물 회피·청소 재개','먼지 출력 강화']
    requirements=['R1','R2','R3','R5']
    if kind==2:
        expected+=' 세 방향이 막힌 초기 배치에서는 먼저 후진한 뒤 회전하고 전진한다.'
        functions.append('세 방향 막힘 후진');requirements.append('R4')
    cases.append(dict(id=f'ST-{len(cases)+1:02d}',name=names[kind]+' · '+['북','동','남','서'][direction],
                      start=[4,4],direction=direction,obstacles=obstacles,dust=dust,max_ticks=100,
                      requirements=requirements,functions=functions,expected=expected,
                      sa=['Event List','Process Specifications','DFD Level 4 FSM']))
(ROOT/'simulator/scenarios.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
text='# RVC System Test Scenarios\n\n20개 시나리오 모두 10×10 지도와 최대 100틱을 사용한다. 좌표는 [x,y], 방향은 북=0/동=1/남=2/서=3이다. 나열되지 않은 칸은 빈 칸이다. 원본 요구사항의 기대 동작과 승인된 [P1 프로파일](../SD/simulation_profile.md)의 상세 동작을 구분해 검토한다. 템플릿 예시의 15×15 오기는 스킬의 10×10 제약에 맞게 적용했다.\n\n'
for c in cases:
 text+=f'## {c["id"]} {c["name"]}\n\n'
 text+=f'- Grid: 10×10\n- Start: {c["start"]}\n- Initial Direction: {c["direction"]}\n- Obstacles: {c["obstacles"]}\n- Dust: {c["dust"]}\n- Maximum Ticks: {c["max_ticks"]}\n- Essential Functions: '+', '.join(c['functions'])+'\n- Requirement IDs: '+', '.join(c['requirements'])+'\n- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)\n\n'
 text+='Expected Behavior: '+c['expected']+'\n\nHuman Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.\n\n'
(out/'test_scenarios.md').write_text(text,encoding='utf-8')
text='# Requirement Traceability\n\n| Scenario | Essential Functions | Requirements | SA | Human Result |\n|---|---|---|---|---|\n'
for c in cases:
 text+='| '+c['id']+' | '+', '.join(c['functions'])+' | '+', '.join(c['requirements'])+' | Event List / Process Specifications / FSM | PENDING |\n'
text+='\nR6의 HW 제외·R7의 자동 청소 범위는 전체 시나리오의 설계 제약이다. R1~R5는 C GoogleTest와 실행 trace를 함께 검토한다. 20개 지도는 5개 장애물 패턴 × 4개 초기 방향으로 구성하며, 각 지도는 서로 다른 센서 방향·회피 동선을 제공한다.\n'
(out/'requirement_traceability.md').write_text(text,encoding='utf-8')
print(f'Generated {len(cases)} explicit 10x10 scenarios.')
