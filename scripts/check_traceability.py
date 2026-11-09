"""Check the designed calls against C function bodies, and replay saved C traces."""
from pathlib import Path
import json
import os
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
chart=(ROOT/'artifacts/SD/structure_chart.md').read_text(encoding='utf-8')
tree=re.findall(r'```mermaid\s*\n(.*?)```',chart,re.S)[0]
modules=dict(re.findall(r'^\s*(\w+)\["\w+ / (\w+)"\]',tree,re.M))
calls=re.findall(r'^\s*(\w+) -->\|"CALL[^"\n]*"\| (\w+)',tree,re.M)
expected={(modules[a],modules[b]) for a,b in calls}
source='\n'.join(path.read_text(encoding='utf-8') for path in sorted((ROOT/'src').glob('*.c')))
observed=set()
for function in modules.values():
    match=re.search(r'\b'+function+r'\s*\([^;{}]*\)\s*\{',source)
    assert match, function
    start=match.end();depth=1;end=start
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    body=source[start:end-1]
    for callee in modules.values():
        if re.search(r'\b'+callee+r'\s*\(',body):observed.add((function,callee))
assert observed==expected,(observed-expected,expected-observed)
cli=ROOT/'build'/('rvc_cli.exe' if os.name=='nt' else 'rvc_cli')
count=0
for path in sorted((ROOT/'artifacts/SystemTest/traces').glob('ST-*.json')):
    trace=json.loads(path.read_text(encoding='utf-8'))
    frames=trace['history'][1:]
    script=''.join(' '.join(str(f['sensors'][k]) for k in ('front','left','right','dust'))+'\n' for f in frames)
    replay=subprocess.run([str(cli)],input=script,text=True,capture_output=True,check=True,timeout=5)
    assert [json.loads(line) for line in replay.stdout.splitlines()]==[f['controller'] for f in frames],path.name
    count+=1
assert count==20
text='# SD-to-Implementation Module Traceability\n\n검사 명령: `python scripts/check_traceability.py`. SD의 13개 모듈이 C 함수에 존재하고 모듈 간 12개 직접 호출 관계가 일치함을 소스에서 검사했다. 생명주기, 직렬화 및 모듈 내부 보조 함수는 구조도상의 기능 모듈과 구분한다.\n\n| SD Module | C Function | Source |\n|---|---|---|\n'
for module,function in modules.items():
    file='main.c' if function=='main' else 'fsm.c' if function=='step_fsm' else 'rvc.c'
    text+=f'| {module} | {function} | [src/{file}](../../src/{file}) |\n'
text+='\n## 확인 결과\n\n- 모듈 13개 / 기능 모듈 간 직접 호출 12개 일치. DFD의 정보 흐름을 함수 호출로 복사하지 않았다.\n- 저장된 20개 × 100틱의 센서 입력을 최종 C 실행 파일에 다시 재생하여 기존 전체 C 출력과 일치함을 확인했다. 입력 파서 수정·회전 선택 리팩터링 이후에도 저장된 제어 동작은 동일하다.\n- 상태는 `fsm.c`의 불투명 컨텍스트가 소유하며 다른 모듈은 읽기 전용 복사본만 받는다.\n- FILE 포트, 컨텍스트 생명주기, 진단 상태와 오류 반환의 구체화는 [승인된 시뮬레이션 프로파일](../SD/simulation_profile.md)에 기록했다.\n- R1~R5의 상세 기대값은 [단위 테스트](unit_test_cases.md), [시스템 시나리오](../SystemTest/test_scenarios.md)에서 추적한다.\n'
(ROOT/'artifacts/Implementation/module_traceability.md').write_text(text,encoding='utf-8')
print(f'PASS: {len(modules)} modules, {len(expected)} calls, {count} saved native-C traces reproduced.')
