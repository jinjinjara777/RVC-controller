# Unit Test Coverage

GCC/gcov 14.2.0, C11, `--coverage -O0 -g`. 기존 카운터를 지운 뒤 GoogleTest 22개만 CTest로 실행해 측정했다. 시스템 테스트 실행 횟수는 이 측정에 포함하지 않는다. 프로덕션 제어 로직인 `src/fsm.c`, `src/rvc.c`를 대상으로 한다. `src/main.c`는 stdin/stdout 연결 한 줄인 진입점이며 계측 대상에서 제외했다.

| Source | Lines | Line Coverage | Branch Outcomes | Branch Coverage |
|---|---|---|---|---|
| fsm.c | 39/39 | 100.00% | 33/34 | 97.06% |
| rvc.c | 57/57 | 100.00% | 66/68 | 97.06% |
| TOTAL | 96/96 | 100.00% | 99/102 | 97.06% |

## 실행되지 않은 분기

분기 커버리지는 각 분기 결과가 적어도 한 번 선택되었는지 기준이다. 실행되지 않은 분기를 성공한 것으로 계산하지 않는다. 상세 원시 자료는 [summary.json](coverage/summary.json), [gcov log](coverage/gcov.log)에 있다.

- `fsm.c:11`: 미실행 분기 결과 1개, 행 실행 횟수 36.
- `rvc.c:20`: 미실행 분기 결과 1개, 행 실행 횟수 27.
- `rvc.c:85`: 미실행 분기 결과 1개, 행 실행 횟수 18.

메모리 할당 실패 및 일부 포트/입력 경계 분기는 테스트에서 강제로 발생시키지 않는다. 커버리지 수치는 요구사항 완전성이나 HW 검증을 증명하지 않는다.
