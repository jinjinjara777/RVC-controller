"""Create incremental SA drafts and check graph/interface consistency. Stdlib only."""
from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parent
DFD = ROOT / 'DFD'
DFD.mkdir(exist_ok=True)
DD = ROOT / 'data_dictionary.md'
PS = ROOT / 'process_specification.md'
if DD.exists() or PS.exists():
    raise SystemExit('Existing dictionary/specifications found; review and update instead of rebuilding.')

# (name, description, logical type, requirement)
definitions = {
    'Front Sensor Input': ('전방 장애물 감지 결과.', '감지 결과; 물리 형식·유효성·갱신 주기 TBD', 'R3, R4'),
    'Left Sensor Input': ('좌측 장애물 감지 결과.', '감지 결과; 물리 형식·유효성·갱신 주기 TBD', 'R3, R4'),
    'Right Sensor Input': ('우측 장애물 감지 결과.', '감지 결과; 물리 형식·유효성·갱신 주기 TBD', 'R3, R4'),
    'Dust Sensor Input': ('먼지 감지 결과.', '감지 결과; 물리 형식·유효성·갱신 주기 TBD', 'R5'),
    'Direction': ('이동 구동장치로 전달하는 직진·좌회전·우회전·후진 제어 명령.', '논리 명령; 인코딩·거리·속도·각도 TBD', 'R2, R3, R4'),
    'Clean': ('청소·물걸레 구동장치로 전달하는 제어 정보. 청소 수행·중지·재개·일시적 출력 강화를 포함한다.', '복합 논리 명령; 출력량·물걸레 상세 제어 TBD', 'R1, R2, R3, R5'),
    'Obstacle Observation': ('전방·좌측·우측 감지 결과를 이름 있는 필드로 묶은 관측값. 회피 정책을 포함하지 않는다.', '{front, left, right}; 각 필드 감지/비감지, 물리 형식 TBD', 'R3, R4'),
    'Dust Observation': ('먼지 감지 결과의 논리적 표현. 감지 임계값을 새로 정하지 않는다.', '먼지 감지/비감지; 물리 형식 TBD', 'R5'),
    'Motion Intent': ('제어기가 결정한 직진·좌회전·우회전·후진 의도.', '논리 명령; Direction과 동일한 의미, 장치 인코딩 전', 'R2, R3, R4'),
    'Cleaning Intent': ('제어기가 결정한 청소·물걸레 제어 의도. 청소 중지·재개·출력 강화 의미를 포함한다.', '복합 논리 명령; Clean과 동일한 의미, 장치 인코딩 전', 'R1, R2, R3, R5'),
    'Control Decision': ('제어기가 생성한 이동 의도와 청소 의도의 묶음. 두 의도의 동시 발생 충돌 정책은 TBD.', '{Motion Intent, Cleaning Intent}', 'R1, R2, R3, R4, R5'),
    'Control Conditions': ('관측값과 전방·좌측·우측 모두 장애물인지 여부를 보존한 제어 판단 자료. 회피 필요 여부의 일반 규칙은 TBD.', '{Obstacle Observation, Dust Observation, all_blocked}; all_blocked = front AND left AND right', 'R3, R4, R5'),
}
external = {
    'FrontSensor': '전방 장애물 센서', 'LeftSensor': '좌측 장애물 센서',
    'RightSensor': '우측 장애물 센서', 'DustSensor': '먼지 센서',
    'MovementActuator': '이동 구동장치', 'CleaningActuator': '청소·물걸레 구동장치',
}
processes = {}
graphs = []

def proc(pid, name, parent, level, purpose, trigger, logic, refs, control=False):
    processes[pid] = dict(id=pid, name=name, parent=parent, level=level,
                          purpose=purpose, trigger=trigger, logic=logic, refs=refs, control=control)
    return pid

def graph(title, parent, ids, edges):
    return dict(title=title, parent=parent, ids=ids, edges=edges)

def node_id(pid):
    return 'P' + pid.replace('.', '_') if pid in processes else pid

def category(flow):
    return 'Control' if flow in {'Direction', 'Clean', 'Motion Intent', 'Cleaning Intent', 'Control Decision'} else 'Data'

def render(g):
    lines = ['```mermaid', 'flowchart LR']
    endpoints = set(x for a,b,f in g['edges'] for x in (a,b))
    for endpoint in sorted(endpoints):
        if endpoint in g['ids']:
            p = processes[endpoint]
            lines.append(f'    {node_id(endpoint)}(("{endpoint} {p["name"]}"))')
        else:
            name = external.get(endpoint, f'{endpoint} {processes[endpoint]["name"]}' if endpoint in processes else endpoint)
            lines.append(f'    {node_id(endpoint)}["{name}"]')
    for a,b,f in g['edges']:
        arrow = '-.->' if category(f) == 'Control' else '-->'
        lines.append(f'    {node_id(a)} {arrow}|{f}| {node_id(b)}')
    control_nodes = [node_id(x) for x in endpoints if x in g['ids'] and processes[x]['control']]
    if control_nodes:
        lines += ['    classDef control stroke-dasharray: 5 5', '    class ' + ','.join(sorted(control_nodes)) + ' control']
    return '\n'.join(lines + ['```'])

def io(g, pid):
    return ([f for a,b,f in g['edges'] if b == pid], [f for a,b,f in g['edges'] if a == pid])

def boundary(g):
    ids = set(g['ids'])
    return sorted((a, f, category(f)) for a,b,f in g['edges'] if a not in ids and b in ids), sorted((b, f, category(f)) for a,b,f in g['edges'] if a in ids and b not in ids)

def verify_balance(g):
    parent = g['parent']
    if parent is None:
        return
    pg = next(x for x in graphs if parent in x['ids'])
    expected_in = sorted((a,f,category(f)) for a,b,f in pg['edges'] if b == parent)
    expected_out = sorted((b,f,category(f)) for a,b,f in pg['edges'] if a == parent)
    assert boundary(g) == (expected_in, expected_out), (g['title'], 'unbalanced')

def add_level(level, new_graphs, intro):
    for g in new_graphs:
        verify_balance(g)
        for a,b,f in g['edges']:
            assert f in definitions
        graphs.append(g)
    body = f'# DFD Level {level}\n\n상태: 검토용 초안. 요구사항의 TBD는 상세 동작 확정을 의미하지 않는다.\n\n{intro}\n\n'
    body += '표기: 원은 데이터 처리, 점선 원은 제어 처리, 사각형은 해당 분해 경계의 외부 엔티티 또는 형제 프로세스이다. 실선은 데이터 흐름, 점선은 제어 명령 흐름이다. 영속 데이터 저장소는 요구되지 않아 추가하지 않았다. FSM의 동작 상태와 시간 경과는 제어 프로세스의 내부 기억이며 DB를 의미하지 않는다.\n\n'
    for g in new_graphs:
        body += f'## {g["title"]}\n\n' + render(g) + '\n\n'
        if g['parent'] is not None:
            ins, outs = boundary(g)
            body += f'부모 {g["parent"]} 경계 입력: ' + ', '.join(f for _,f,_ in ins) + '.\n\n'
            body += '부모 경계 출력: ' + ', '.join(f for _,f,_ in outs) + '. 이름·방향·상대 프로세스·흐름 종류를 그대로 보존한다.\n\n'
    body += '관련 문서: [Data Dictionary](../data_dictionary.md), [Process Specifications](../process_specification.md), [요구사항 및 미정 사항](../event_list.md).\n'
    (DFD / f'dfd_level_{level}.md').write_text(body, encoding='utf-8')

    # Read and append only new definitions/specifications after this level, before the next.
    old_dd = DD.read_text(encoding='utf-8')
    used_old = set(re.findall(r'^### (.+)$', old_dd, re.M))
    new_flows = sorted({f for g in new_graphs for a,b,f in g['edges']} - used_old)
    appendix = f'\n## Level {level} 증분 갱신\n\n'
    for flow in new_flows:
        desc, fmt, refs = definitions[flow]
        appendix += f'### {flow}\n\n| Field | Definition |\n|---|---|\n| Data Name | {flow} |\n| Description | {desc} |\n| Format / Type | {fmt} |\n| Flow Category | {category(flow)} |\n| Requirement Reference | {refs} |\n\n'
    appendix += '| Data Name | Flow Category | Source | Destination | DFD Level | Requirement Reference |\n|---|---|---|---|---|---|\n'
    for g in new_graphs:
        for a,b,f in g['edges']:
            appendix += f'| {f} | {category(f)} | {a} | {b} | {level} | {definitions[f][2]} |\n'
    appendix += '\n기존 정의를 보존했다. 이 레벨에서 추가된 Data Store는 없다.\n'
    DD.write_text(old_dd + appendix, encoding='utf-8')

    old_ps = PS.read_text(encoding='utf-8')
    appendix = f'\n## Level {level}\n\n'
    for g in new_graphs:
        for pid in g['ids']:
            p = processes[pid]
            ins, outs = io(g, pid)
            appendix += f'### {pid} {p["name"]}\n\n| Field | Description |\n|---|---|\n| Process ID | {pid} |\n| Process Name | {p["name"]} |\n| DFD Level | {level} |\n| Parent Process | {p["parent"] if p["parent"] is not None else "없음"} |\n| Purpose | {p["purpose"]} |\n| Inputs | {", ".join(ins)} |\n| Outputs | {", ".join(outs)} |\n| Trigger / Execution Condition | {p["trigger"]} |\n| Relevant Requirements | {p["refs"]} |\n| Data Stores | 없음 |\n\n처리 논리:\n\n'
            for i, step in enumerate(p['logic'], 1):
                appendix += f'{i}. {step}\n'
            appendix += '\n'
    PS.write_text(old_ps + appendix, encoding='utf-8')

# Initialize the dictionary directly from the Event List, preserving its descriptions.
event_text = (ROOT / 'event_list.md').read_text(encoding='utf-8')
events = re.findall(r'^\| ([^|]+) \| ((?:입력|출력)[^\n]+) \|$', event_text, re.M)
assert len(events) == 6
dd = '# Data Dictionary\n\n상태: 검토용 초안. 원본은 [예비 요구사항](../../docs/preliminary_requirement.md). R1~R7은 [Event List](event_list.md)의 식별자를 따른다. 논리 형식은 분석 표현이며 C 타입이나 HW 인코딩을 확정하지 않는다. TBD는 미정이다.\n\n## Event List 기반 초기화\n\n| Input/Output Event | Description | Format / Type |\n|---|---|---|\n'
for name, desc in events:
    dd += f'| {name} | {desc} | {definitions[name][1]} |\n'
dd += '\n아래 증분 항목의 정의 표와 레벨별 경로 표를 함께 읽는다. 경로 표가 각 정의의 Source, Destination, DFD Level을 제공한다. Data Store는 현재 요구사항에서 도출되지 않았다.\n'
DD.write_text(dd, encoding='utf-8')
PS.write_text('# Process Specifications\n\n상태: 검토용 초안. 요구사항 식별자 및 미정 항목은 [Event List](event_list.md)를 따른다. 데이터와 제어 의미는 [Data Dictionary](data_dictionary.md)를 따른다. 각 레벨 이후 기존 명세를 보존하며 하위 명세를 추가한다. Level 4 FSM의 별도 Process Specification은 만들지 않는다.\n', encoding='utf-8')

proc('0', 'RVC Controller', None, 0, '자동 청소·물걸레, 이동, 장애물 회피 및 먼지에 따른 일시적 청소 강화를 제어한다.', '자동 청소 기능이 실행되는 동안 관측값 변화 및 내부 동작 진행.', ['센서 입력을 받아 장애물과 먼지 관측을 구성한다.', '정상 청소 중 직진한다. 장애물 감지 시 청소를 중지하고 좌측 또는 우측으로 회전한 뒤 직진하며 청소를 재개한다.', '전방·좌측·우측이 모두 막히면 후진한 뒤 좌측 또는 우측으로 회전하고 직진한다.', '먼지 감지 시 청소 출력을 일시적으로 강화한다. 시간·회피와의 우선순위·물걸레 세부 동작은 TBD이다.'], 'R1–R7')
e0 = [('FrontSensor','0','Front Sensor Input'), ('LeftSensor','0','Left Sensor Input'), ('RightSensor','0','Right Sensor Input'), ('DustSensor','0','Dust Sensor Input'), ('0','MovementActuator','Direction'), ('0','CleaningActuator','Clean')]
add_level(0, [graph('Process 0 — 시스템 전체', None, ['0'], e0)], 'Context Diagram의 시스템을 Process 0으로 표시한다. 외부 엔티티와 흐름 이름·방향은 동일하다. Direction과 Clean은 제어 명령이므로 점선으로 세분 표기한다. 이는 Context Diagram의 명령 의미를 변경하지 않는다.')

proc('1', '센서 관측 구성', '0', 1, '장애물 및 먼지 센서 입력을 제어에 필요한 관측값으로 구성한다.', '센서 입력 수신; 표본 동기화·주기 TBD.', ['전방·좌측·우측 입력의 의미를 보존하여 Obstacle Observation을 구성한다.', '먼지 입력의 의미를 보존하여 Dust Observation을 구성한다. 오류 처리·필터링·임계값을 새로 정의하지 않는다.'], 'R3, R4, R5')
proc('2', '자동 청소 제어', '0', 1, '장애물과 먼지 관측으로 이동 및 청소 의도를 결정한다.', '관측 수신 또는 내부 동작 진행; 구체 시점 TBD.', ['Obstacle Observation과 Dust Observation으로 제어 조건을 구성한다.', 'R2~R5에 따라 동작 순서와 일시적 출력 강화를 판단한다. 이동 진행 상태와 강화 경과는 내부에서 기억한다.', 'Motion Intent와 Cleaning Intent를 출력한다. 회피 필요 조건의 일반화·회전 선택·완료 조건·동시 이벤트 정책은 TBD이다.'], 'R1, R2, R3, R4, R5', True)
proc('3', '구동 명령 전달', '0', 1, '제어 의도를 장치 경계의 논리 명령으로 전달한다.', '이동 또는 청소 의도 생성.', ['Motion Intent를 Direction으로 전달한다.', 'Cleaning Intent를 Clean으로 전달한다. 별도 정책이나 HW 프로토콜을 추가하지 않는다.'], 'R1, R2, R3, R4, R5, R6')
e1 = [('FrontSensor','1','Front Sensor Input'), ('LeftSensor','1','Left Sensor Input'), ('RightSensor','1','Right Sensor Input'), ('DustSensor','1','Dust Sensor Input'), ('1','2','Obstacle Observation'), ('1','2','Dust Observation'), ('2','3','Motion Intent'), ('2','3','Cleaning Intent'), ('3','MovementActuator','Direction'), ('3','CleaningActuator','Clean')]
add_level(1, [graph('Process 0 분해', '0', ['1','2','3'], e1)], '입력 관측, 상태를 가진 제어, 명령 전달의 세 기능으로 분해한다. 구동장치 피드백이나 외부 Tick은 추가하지 않는다.')

proc('1.1', '장애물 관측 구성', '1', 2, '세 방향의 감지 결과를 묶는다.', '장애물 센서 입력 수신.', ['전방·좌측·우측 결과를 각각 front, left, right 필드로 보존한다.', 'Obstacle Observation으로 전달한다. 세 입력의 동기화와 유효성 정책은 TBD이다.'], 'R3, R4')
proc('1.2', '먼지 관측 구성', '1', 2, '먼지 감지 결과를 논리 관측값으로 전달한다.', '먼지 센서 입력 수신.', ['Dust Sensor Input의 감지 의미를 Dust Observation으로 전달한다.', '주기·필터·임계값을 임의로 정하지 않는다.'], 'R5')
proc('2.1', '동작 판단', '2', 2, '이동과 청소 제어 결정을 생성한다.', '관측 수신 또는 내부 동작·강화 시간의 진행.', ['관측값을 보존하면서 전방·좌측·우측 모두 막힘 조건을 산출한다.', '상태 제어로 직진·회피·후진 및 일시적 청소 강화 의도를 결정한다.', '두 의도를 Control Decision으로 묶어 전달한다. 미정 조건은 확정하지 않는다.'], 'R1, R2, R3, R4, R5', True)
proc('2.2', '제어 의도 분리', '2', 2, '하나의 결정을 이동 의도와 청소 의도로 분리한다.', 'Control Decision 생성.', ['Control Decision의 이동 필드를 Motion Intent로 전달한다.', '청소·물걸레 필드를 Cleaning Intent로 전달한다. 분리 과정에서 정책을 추가하지 않는다.'], 'R1, R2, R3, R4, R5')
proc('3.1', '이동 명령 전달', '3', 2, '이동 의도를 장치 경계에 전달한다.', 'Motion Intent 생성.', ['의도의 직진·좌회전·우회전·후진 의미를 보존하여 Direction으로 전달한다.', 'HW 인코딩·속도·각도·거리의 상세 설계는 하지 않는다.'], 'R2, R3, R4, R6')
proc('3.2', '청소 명령 전달', '3', 2, '청소 및 물걸레 의도를 장치 경계에 전달한다.', 'Cleaning Intent 생성.', ['의도의 청소 수행·중지·재개·출력 강화 의미 및 물걸레 제어 정보를 Clean으로 전달한다.', '강화 정도와 물걸레의 독립 제어 방식은 TBD이다. HW 상세 설계는 하지 않는다.'], 'R1, R2, R3, R5, R6')
g21 = graph('Process 1 분해', '1', ['1.1','1.2'], [('FrontSensor','1.1','Front Sensor Input'), ('LeftSensor','1.1','Left Sensor Input'), ('RightSensor','1.1','Right Sensor Input'), ('DustSensor','1.2','Dust Sensor Input'), ('1.1','2','Obstacle Observation'), ('1.2','2','Dust Observation')])
g22 = graph('Process 2 분해', '2', ['2.1','2.2'], [('1','2.1','Obstacle Observation'), ('1','2.1','Dust Observation'), ('2.1','2.2','Control Decision'), ('2.2','3','Motion Intent'), ('2.2','3','Cleaning Intent')])
g23 = graph('Process 3 분해', '3', ['3.1','3.2'], [('2','3.1','Motion Intent'), ('2','3.2','Cleaning Intent'), ('3.1','MovementActuator','Direction'), ('3.2','CleaningActuator','Clean')])
add_level(2, [g21,g22,g23], '각 Level 1 프로세스를 별도 다이어그램으로 분해한다. 각 다이어그램에 나타나는 형제 프로세스는 해당 분해 경계의 외부 참조이며 새로운 시스템 외부 엔티티가 아니다.')

proc('2.1.1', '제어 조건 구성', '2.1', 3, '상태 제어에 필요한 관측 및 모두 막힘 조건을 구성한다.', 'Obstacle Observation 또는 Dust Observation 수신.', ['전방·좌측·우측 결과를 보존한다.', 'all_blocked = front AND left AND right를 산출한다.', 'Obstacle Observation과 Dust Observation 및 all_blocked를 Control Conditions로 전달한다. 그 밖의 회피 필요 조건은 TBD이다.'], 'R3, R4, R5')
proc('2.1.2', 'Controller', '2.1', 3, '내부 상태를 이용해 제어 결정을 생성한다.', 'Control Conditions 수신 및 동작/시간의 내부 진행. 완료 판정 수단은 TBD.', ['정상 자동 청소 상태에서는 직진 및 청소·물걸레 수행 의도를 구성한다.', '장애물 회피 시 청소 중지 후 회전하고 직진하며 청소를 재개한다. 모두 막힌 경우에는 회전 전에 후진한다.', '먼지 감지 시 한동안 청소 출력을 강화한다. 강화 종료를 위한 내부 시간 의미는 요구되나 지속시간과 시간 구현은 TBD이다.', 'Control Decision을 출력한다. 상태 전이의 세부 초안은 Level 4 FSM을 참조한다. 미정 조건을 실행 가능한 정책으로 대체하지 않는다.'], 'R1, R2, R3, R4, R5', True)
g3 = graph('Process 2.1 분해', '2.1', ['2.1.1','2.1.2'], [('1','2.1.1','Obstacle Observation'), ('1','2.1.1','Dust Observation'), ('2.1.1','2.1.2','Control Conditions'), ('2.1.2','2.2','Control Decision')])
add_level(3, [g3], '상태가 없는 제어 조건 구성과 상태를 가진 Controller를 분리한다. 다른 Level 2 말단은 현재 요구사항에서 더 나눌 근거가 없어 유지한다. Controller 2.1.2만 다음 Level 4 FSM으로 정제한다.')

# Validate every emitted DFD edge and every PS interface against the in-memory graph.
checks = []
for level in range(4):
    text = (DFD / f'dfd_level_{level}.md').read_text(encoding='utf-8')
    labels = re.findall(r'(?:-->|-\.->)\|([^|]+)\|', text)
    expected = [f for g in graphs if processes[g['ids'][0]]['level'] == level for a,b,f in g['edges']]
    assert sorted(labels) == sorted(expected)
    checks.append(f'Level {level}: {len(labels)}개 흐름의 이름·종류·경계 및 프로세스 명세 확인')
for g in graphs:
    verify_balance(g)
    for pid in g['ids']:
        ps_text = PS.read_text(encoding='utf-8')
        section = ps_text.split(f'### {pid} {processes[pid]["name"]}\n', 1)[1].split('\n### ', 1)[0]
        ins, outs = io(g,pid)
        assert f'| Inputs | {", ".join(ins)} |' in section
        assert f'| Outputs | {", ".join(outs)} |' in section
        assert processes[pid]['parent'] == g['parent']
all_flows = {f for g in graphs for a,b,f in g['edges']}
assert all(f'### {f}\n' in DD.read_text(encoding='utf-8') for f in all_flows)
context = (ROOT / 'context_diagram.md').read_text(encoding='utf-8')
assert sorted(re.findall(r'-->\|([^|]+)\|', context)) == sorted(f for a,b,f in e0)
assert set(name for name,desc in events) == set(f for a,b,f in e0)
(ROOT / 'dfd_model.json').write_text(json.dumps(dict(processes=processes,graphs=graphs), ensure_ascii=False, indent=2), encoding='utf-8')
print('\n'.join(checks))
print(f'PASS: {len(processes)} processes, {len(all_flows)} flow definitions, {len(graphs)-1} balanced decompositions. FSM and rendering require separate review.')
