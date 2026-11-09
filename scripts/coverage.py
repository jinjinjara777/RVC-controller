"""Collect GCC line/branch coverage after a clean unit-only CTest run."""
from pathlib import Path
import gzip
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
build=ROOT/'build'
cmake_bin=ROOT/'.tools/python/cmake/data/bin'
ctest=shutil.which('ctest') or str(cmake_bin/'ctest.exe')
out=ROOT/'artifacts/Implementation/coverage';out.mkdir(parents=True,exist_ok=True)
# Delete only matching instrumentation counters inside this verified build directory.
for counter in build.rglob('*.gcda'):
    assert counter.resolve().is_relative_to(build.resolve())
    counter.unlink()
result=subprocess.run([ctest,'--test-dir',str(build),'--output-on-failure'],capture_output=True,text=True)
(ROOT/'artifacts/Implementation/tdd_refactor.log').write_text(result.stdout+result.stderr,encoding='utf-8')
if result.returncode: raise SystemExit(result.stdout+result.stderr)
gcno=[build/'CMakeFiles/rvc_core.dir/src'/f'{name}.c.gcno' for name in ('fsm','rvc')]
gcov=subprocess.run(['gcov','-b','-c','-j',*[str(p) for p in gcno]],cwd=out,capture_output=True,text=True,check=True)
(out/'gcov.log').write_text(gcov.stdout+gcov.stderr,encoding='utf-8')
rows=[];uncovered=[]
for archive in sorted(out.glob('*.gcov.json.gz')):
    with gzip.open(archive,'rt',encoding='utf-8') as stream: data=json.load(stream)
    for file in data['files']:
        lines=file['lines'];branches=[b for line in lines for b in line.get('branches',[])]
        row={'file':Path(file['file']).name,'lines':len(lines),'lines_hit':sum(l['count']>0 for l in lines),
             'branches':len(branches),'branches_hit':sum(b['count']>0 for b in branches)}
        rows.append(row)
        for line in lines:
            if line['count']==0 or any(b['count']==0 for b in line.get('branches',[])):
                uncovered.append({'file':row['file'],'line':line['line_number'],'line_count':line['count'],
                                  'uncovered_branches':sum(b['count']==0 for b in line.get('branches',[]))})
total={key:sum(r[key] for r in rows) for key in ('lines','lines_hit','branches','branches_hit')}
test_count=ET.parse(build/'unit_results.xml').getroot().attrib['tests']
shutil.copyfile(build/'unit_results.xml',ROOT/'artifacts/Implementation/unit_results.xml')
(out/'summary.json').write_text(json.dumps({'files':rows,'total':total,'uncovered':uncovered},indent=2),encoding='utf-8')
text=f'# Unit Test Coverage\n\nGCC/gcov 14.2.0, C11, `--coverage -O0 -g`. 기존 카운터를 지운 뒤 GoogleTest {test_count}개만 CTest로 실행해 측정했다. 시스템 테스트 실행 횟수는 이 측정에 포함하지 않는다. 프로덕션 제어 로직인 `src/fsm.c`, `src/rvc.c`를 대상으로 한다. `src/main.c`는 stdin/stdout 연결 한 줄인 진입점이며 계측 대상에서 제외했다.\n\n| Source | Lines | Line Coverage | Branch Outcomes | Branch Coverage |\n|---|---|---|---|---|\n'
for row in rows+[dict(file='TOTAL',**total)]:
    text+=f'| {row["file"]} | {row["lines_hit"]}/{row["lines"]} | {100*row["lines_hit"]/row["lines"]:.2f}% | {row["branches_hit"]}/{row["branches"]} | {100*row["branches_hit"]/row["branches"]:.2f}% |\n'
text+='\n## 실행되지 않은 분기\n\n분기 커버리지는 각 분기 결과가 적어도 한 번 선택되었는지 기준이다. 실행되지 않은 분기를 성공한 것으로 계산하지 않는다. 상세 원시 자료는 [summary.json](coverage/summary.json), [gcov log](coverage/gcov.log)에 있다.\n\n'
for line in uncovered:
    text+=f'- `{line["file"]}:{line["line"]}`: 미실행 분기 결과 {line["uncovered_branches"]}개, 행 실행 횟수 {line["line_count"]}.\n'
text+='\n메모리 할당 실패 및 일부 포트/입력 경계 분기는 테스트에서 강제로 발생시키지 않는다. 커버리지 수치는 요구사항 완전성이나 HW 검증을 증명하지 않는다.\n'
(ROOT/'artifacts/Implementation/coverage_report.md').write_text(text,encoding='utf-8')
print(json.dumps(total));print(f'LINE {100*total["lines_hit"]/total["lines"]:.2f}% / BRANCH {100*total["branches_hit"]/total["branches"]:.2f}%')
