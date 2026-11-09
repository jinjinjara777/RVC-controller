"""Read-only artifact consistency checks; write the validation report after success."""
from pathlib import Path
from collections import Counter
import json
import re

root = Path(__file__).resolve().parent
model = json.loads((root / 'dfd_model.json').read_text(encoding='utf-8'))
processes, graphs = model['processes'], model['graphs']
dictionary = (root / 'data_dictionary.md').read_text(encoding='utf-8')
specs = (root / 'process_specification.md').read_text(encoding='utf-8')
checks = []

def mermaid_blocks(text):
    return re.findall(r'```mermaid\s*\n(.*?)```', text, re.S)

def nid(pid):
    return 'P' + pid.replace('.', '_') if pid in processes else pid

def category(flow):
    return '-.->' if flow in {'Direction', 'Clean', 'Motion Intent', 'Cleaning Intent', 'Control Decision'} else '-->'

def parse_edges(block):
    return re.findall(r'^\s*(\w+)\s+(-->|-\.->)\|([^|]+)\|\s+(\w+)\s*$', block, re.M)

for level in range(4):
    text = (root / 'DFD' / f'dfd_level_{level}.md').read_text(encoding='utf-8')
    blocks = mermaid_blocks(text)
    level_graphs = [g for g in graphs if processes[g['ids'][0]]['level'] == level]
    assert len(blocks) == len(level_graphs)
    for block, graph in zip(blocks, level_graphs):
        assert block.startswith('flowchart LR\n')
        expected = [(nid(a),category(f),f,nid(b)) for a,b,f in graph['edges']]
        actual = parse_edges(block)
        assert Counter(actual) == Counter(expected), graph['title']
        assert len(re.findall(r'-->|-\.->', block)) == len(actual), 'Unlabeled or unparsed edge'
        nodes = dict(re.findall(r'^\s*(\w+)\(\("([^"\n]+)"\)\)\s*$', block, re.M))
        assert len(nodes) == len(graph['ids'])
        declared = set(nodes) | set(re.findall(r'^\s*(\w+)\["[^"\n]+"\]\s*$', block, re.M))
        assert all(a in declared and b in declared for a,_,_,b in actual)
        dashed = re.findall(r'^\s*class ([\w,]+) control\s*$', block, re.M)
        dashed_nodes = set(dashed[0].split(',')) if dashed else set()
        assert dashed_nodes == {nid(pid) for pid in graph['ids'] if processes[pid]['control']}
        for pid in graph['ids']:
            p = processes[pid]
            assert nodes[nid(pid)] == f'{pid} {p["name"]}'
            assert p['parent'] == graph['parent']
            if level > 1:
                assert pid.rsplit('.',1)[0] == graph['parent']
            section = specs.split(f'### {pid} {p["name"]}\n',1)[1].split('\n### ',1)[0]
            ins = ', '.join(f for a,b,f in graph['edges'] if b == pid)
            outs = ', '.join(f for a,b,f in graph['edges'] if a == pid)
            assert f'| Inputs | {ins} |' in section
            assert f'| Outputs | {outs} |' in section
            for field in ['Purpose','Trigger / Execution Condition','Relevant Requirements','Data Stores']:
                assert f'| {field} |' in section
        if graph['parent'] is not None:
            parent = graph['parent']
            pg = next(g for g in graphs if parent in g['ids'])
            expected_in = Counter((a,f,category(f)) for a,b,f in pg['edges'] if b == parent)
            expected_out = Counter((b,f,category(f)) for a,b,f in pg['edges'] if a == parent)
            actual_in = Counter((a,f,category(f)) for a,b,f in graph['edges'] if a not in graph['ids'] and b in graph['ids'])
            actual_out = Counter((b,f,category(f)) for a,b,f in graph['edges'] if a in graph['ids'] and b not in graph['ids'])
            assert (expected_in,expected_out) == (actual_in,actual_out)
    checks.append(f'Level {level}: {len(level_graphs)}개 다이어그램의 선언·흐름명·방향·데이터/제어 표기·프로세스 번호·명세 입출력 일치')

event_text = (root / 'event_list.md').read_text(encoding='utf-8')
event_names = re.findall(r'^\| ([^|]+) \| (?:입력|출력)[^\n]+ \|$', event_text, re.M)
context = mermaid_blocks((root / 'context_diagram.md').read_text(encoding='utf-8'))[0]
context_edges = parse_edges(context)
level0 = graphs[0]['edges']
assert sorted(event_names) == sorted(f for a,b,f in level0)
assert Counter((a,f,b) for a,_,f,b in context_edges) == Counter((nid(a) if a != '0' else 'Controller', f, nid(b) if b != '0' else 'Controller') for a,b,f in level0)
checks.append('Context Diagram ↔ Level 0: 외부 입출력 6개와 연결 엔티티·방향 일치')
all_flows = {f for g in graphs for a,b,f in g['edges']}
defined = re.findall(r'^### (.+)$', dictionary, re.M)
assert len(defined) == len(set(defined))
assert set(defined) == all_flows
for name in defined:
    section = dictionary.split(f'### {name}\n',1)[1].split('\n### ',1)[0]
    for field in ['Data Name','Description','Format / Type','Flow Category','Requirement Reference']:
        assert f'| {field} |' in section
for g in graphs:
    level = processes[g['ids'][0]]['level']
    for a,b,f in g['edges']:
        cat = 'Control' if category(f) == '-.->' else 'Data'
        assert f'| {f} | {cat} | {a} | {b} | {level} |' in dictionary
assert len(re.findall(r'^### [0-9]', specs, re.M)) == len(processes) == 12
assert '## Level 4\n' not in specs
checks.append('Data Dictionary: 12개 흐름 정의·전 경로 수록; Process Specifications: Level 0~3 전체 12개, Level 4 별도 명세 없음')

fsm_doc = (root / 'DFD' / 'dfd_level_4_fsm.md').read_text(encoding='utf-8')
fsm = mermaid_blocks(fsm_doc)[0]
assert fsm.startswith('stateDiagram-v2\n')
states = set(re.findall(r'^\s*state "[^"\n]+" as (\w+)', fsm, re.M))
transitions = re.findall(r'^\s*(\[\*\]|\w+) --> (\[\*\]|\w+) : (.+)$', fsm, re.M)
assert len(transitions) == 9
assert all(a in states or a == '[*]' for a,b,label in transitions)
assert all(b in states or b == '[*]' for a,b,label in transitions)
assert fsm.count('{') == fsm.count('}') == 3
assert 'Control Conditions' in fsm_doc and 'Control Decision' in fsm_doc
assert 'TBD' in fsm_doc and '우선순위는 정해지지 않았다' in fsm_doc
rows = re.findall(r'^\| (?:초기|Movement 초기|Forward|Backward|Turning|Power 초기|Normal|Boost) \|', fsm_doc, re.M)
assert len(rows) == len(transitions)
checks.append('FSM: 선언된 상태 참조·9개 전이와 표의 행 수·내부 영역 괄호 확인; TBD 및 충돌 미해결 명시')

for path in root.rglob('*.md'):
    text = path.read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in link and not link.startswith('#'):
            assert (path.parent / link.split('#')[0]).exists(), (path, link)
checks.append('SA Markdown 문서의 상대 링크 대상 존재 확인')

report = '# SA 구조 검사 결과\n\n검사 실행: 2026-11-06 (Asia/Seoul 기준 작업일). 명령: `python artifacts/SA/validate_sa.py`.\n\n결과: **자동 구조 검사 PASS**. 요구사항의 완전성·FSM의 실행 가능성에 대한 승인을 의미하지 않는다.\n\n'
report += '\n'.join(f'- {c}' for c in checks)
report += '\n\n생성 과정에서는 Level 0 → Dictionary/Specifications → Level 1 → Dictionary/Specifications → Level 2 → Dictionary/Specifications → Level 3 → Dictionary/Specifications 순서로 파일을 누적 갱신했다. 최초 생성 스크립트의 검사도 실행되어 5개 부모/자식 경계의 균형을 확인했다.\n\n## 검증 한계와 후속 검토\n\n- Mermaid 엔진 렌더링은 실행하지 않았다. 검사는 코드 블록의 선언·참조·흐름 구문과 문서 정합성을 대상으로 한다.\n- FSM의 완료 조건·출력 합성·동시 이벤트 우선순위가 미정이다. 전이의 실행 결과, 상태 도달성, 교착 부재 또는 완전성을 검증했다고 주장하지 않는다.\n- 프로덕션 코드가 없는 SA 단계이므로 단위·시스템 테스트 및 커버리지 측정은 수행 대상이 아니다.\n- 요구사항에 근거하지 않은 데이터 저장소나 외부 인터페이스는 도입하지 않았으나, 분해 방식과 명세 의미는 인간 검토가 필요하다.\n- [미정 요구사항](README.md)을 해소하고 SA 승인을 받아야 SD로 진행할 수 있다.\n'
(root / 'validation_report.md').write_text(report,encoding='utf-8')
print('PASS: Levels 0-3, 5 balanced decompositions, 12 processes, 12 flow definitions, 9 FSM transitions; links resolved.')
print('LIMIT: Mermaid rendering and FSM behavioral completeness were not verified.')
