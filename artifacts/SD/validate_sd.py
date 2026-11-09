"""Check SD documents against each other and the existing SA model."""
from pathlib import Path
from collections import Counter
import json
import re

root = Path(__file__).resolve().parent
sa = json.loads((root.parent / 'SA/dfd_model.json').read_text(encoding='utf-8'))
ta = (root / 'transform_analysis.md').read_text(encoding='utf-8')
chart = (root / 'structure_chart.md').read_text(encoding='utf-8')
blocks = re.findall(r'```mermaid\s*\n(.*?)```', chart, re.S)
assert len(blocks) == 2 and blocks[0].startswith('flowchart TB\n')
tree = blocks[0]
nodes = dict(re.findall(r'^\s*(\w+)\["([^"\n]+)"\]\s*$', tree, re.M))
edges = re.findall(r'^\s*(\w+) -->\|"CALL[^"\n]*"\| (\w+)\s*$', tree, re.M)
assert len(nodes) == 13 and len(edges) == 12 and len(set(edges)) == 12
assert len(re.findall(r'-->', tree)) == 12
assert all(a in nodes and b in nodes for a,b in edges)
parents = Counter(b for a,b in edges)
assert set(nodes) - set(parents) == {'Main'}
assert all(parents[n] == 1 for n in nodes if n != 'Main')
assert ('Main','Controller') in edges
reached = set()
def visit(n):
    assert n not in reached, 'Cycle or multiple parents'
    reached.add(n)
    for a,b in edges:
        if a == n:
            visit(b)
visit('Main')
assert reached == set(nodes)

interfaces = chart.split('## 5. Module Interfaces',1)[1].split('### 외부 환경 경계',1)[0]
rows = re.findall(r'^\| (\w+) \| (\w+) \| (.+) \| (.+) \| (.+) \|$', interfaces, re.M)
rows = [r for r in rows if r[0] in nodes]
assert Counter((r[0],r[1]) for r in rows) == Counter(edges)
descriptions = chart.split('## 4. Module Descriptions',1)[1].split('## 5.',1)[0]
desc_rows = re.findall(r'^\| (\w+) \| (\w+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$', descriptions, re.M)
desc_rows = [r for r in desc_rows if r[0] in nodes]
assert {r[0] for r in desc_rows} == set(nodes)
for name,func,purpose,called,state in desc_rows:
    assert nodes[name] == f'{name} / {func}'
    children = [] if called.strip() == '없음' else called.strip().split(', ')
    assert set(children) == {b for a,b in edges if a == name}

trace = chart.split('## 6. SA-to-SD Traceability',1)[1].split('## 7.',1)[0]
trace_rows = re.findall(r'^\| (\d+(?:\.\d+)*) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$',trace,re.M)
assert len(trace_rows) == len(sa['processes']) == 12
mapping = {}
for pid,name,modules,reason in trace_rows:
    assert sa['processes'][pid]['name'] == name.strip()
    mapping[pid] = set(modules.strip().split(', '))
    assert mapping[pid] <= set(nodes)
assert set(mapping) == set(sa['processes'])
assert set.union(*mapping.values()) == set(nodes)
for pid,p in sa['processes'].items():
    if p['parent'] is not None:
        assert any(a in mapping[p['parent']] and b in mapping[pid] for a,b in edges)
assert mapping['2.1.2'] == {'StepFSM'}

regions = re.findall(r'^\| (\d+(?:\.\d+)*) \| ([^|]+) \|',ta,re.M)
assert len(regions) == len(sa['processes'])-1
assert {pid for pid,name in regions} == set(sa['processes'])-{'0'}
for pid,name in regions:
    assert name.strip() == sa['processes'][pid]['name']
dictionary = (root.parent / 'SA/data_dictionary.md').read_text(encoding='utf-8')
flows = set(re.findall(r'^### (.+)$',dictionary,re.M))
ta_block = re.findall(r'```mermaid\s*\n(.*?)```',ta,re.S)[0]
ta_flows = re.findall(r'(?:-->|-\.->)\|([^|]+)\|',ta_block)
assert len(ta_flows) == 6 and set(ta_flows) <= flows
assert all(flow in chart for flow in flows)
for condition in ['all_blocked','avoid_required_TBD','back_complete_TBD','turn_complete_TBD','boost_elapsed_TBD']:
    assert condition in chart
assert '우선순위는 정하지 않았다' in chart

for path in root.glob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if '://' not in link and not link.startswith('#'):
            assert (path.parent / link.split('#')[0]).exists(), (path.name,link)

report = '''# Structured Design 검사 결과

실행일: 2026-11-06 (Asia/Seoul 기준 작업일).

실행 명령: `python artifacts/SD/validate_sd.py`

결과: **문서 구조 검사 PASS**.

- Transform Analysis에 Process 0을 제외한 SA 프로세스 11개를 중복 없이 분류했고 기존 프로세스 이름과 번호가 일치한다.
- Transform 흐름 6개가 기존 Data Dictionary에 정의되어 있다.
- Structure Chart의 모듈 13개와 CALL 12개는 Main을 루트로 하는 연결된 비순환 계층을 이룬다. Main → Controller 관계를 확인했다.
- CALL 12개와 인터페이스 표 12행이 일치하며 모듈 책임 표의 호출 목록과도 일치한다.
- SA의 전체 12개 프로세스가 SD 모듈에 대응하고, 모든 SD 모듈에 SA 근거가 있다. 부모·자식 분해가 예정 호출 계층과 일치한다.
- SA 2.1.2는 StepFSM에 대응한다. 미정 가드·강화 경과 조건 및 동시 이벤트의 미정 우선순위가 유지되었다.
- 외부 입출력과 내부 흐름 이름 12개가 설계 문서에 나타나며 문서의 상대 링크가 존재한다.

## 검증 한계

검사는 문서 구조·추적성·호출 계층을 대상으로 실행했다. Mermaid 엔진 렌더링, C 컴파일, 단위 테스트, FSM 실행 검증 및 커버리지 측정은 수행하지 않았다. 동작 의미의 완전한 검증, 시간 및 명령 동시성 검증을 통과했다는 의미가 아니다.

SA의 Q1~Q7은 미정이다. 특히 종료 판정과 회피/강화의 출력 합성 규칙이 확정되지 않았다. 설계는 검토용 초안이며, 구현 전에 미정 사항과 SD를 인간이 검토·승인해야 한다.
'''
(root / 'validation_report.md').write_text(report,encoding='utf-8')
print('PASS: 11 transform process classifications; 13 modules; 12 calls and interfaces; all 12 SA processes mapped; links resolved.')
print('LIMIT: Mermaid rendering, C execution and complete FSM behavior were not verified.')
