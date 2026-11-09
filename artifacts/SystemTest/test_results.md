# RVC System Test Execution Results

실행일: 2026-11-06 (Asia/Seoul).

명령: `python scripts/run_system_tests.py`. 실제 GCC C11 실행 파일로 20개 시나리오를 각각 100틱까지 실행했다. 자동 검사는 환경 모델의 위치·센서·기록·틱 제한 및 C 응답 일치에 대한 구현 검사이다. 시스템 시나리오의 PASS/FAIL은 사람이 정하며 **모두 평가 대기**이다.

| Scenario | Ticks | Snapshots | 관찰된 동작의 요구사항 | 이동 차단 | Human Result | Trace |
|---|---|---|---|---|---|---|
| ST-01 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-01.json) |
| ST-02 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-02.json) |
| ST-03 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-03.json) |
| ST-04 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-04.json) |
| ST-05 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-05.json) |
| ST-06 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-06.json) |
| ST-07 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-07.json) |
| ST-08 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-08.json) |
| ST-09 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-09.json) |
| ST-10 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-10.json) |
| ST-11 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-11.json) |
| ST-12 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-12.json) |
| ST-13 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-13.json) |
| ST-14 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-14.json) |
| ST-15 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-15.json) |
| ST-16 | 100 | 101 | R1, R2, R3, R4, R5 | 0 | PENDING | [JSON](traces/ST-16.json) |
| ST-17 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-17.json) |
| ST-18 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-18.json) |
| ST-19 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-19.json) |
| ST-20 | 100 | 101 | R1, R2, R3, R5 | 0 | PENDING | [JSON](traces/ST-20.json) |

전체 2,000틱과 초기 상태를 포함한 2,020개 snapshot을 보존했다. 틱 0의 controller/sensors는 첫 C 업데이트 전이므로 null이며 가상의 센서나 타이머 값을 만들지 않는다.

실제 사람의 평가는 웹 화면에서 PASS/FAIL/INCONCLUSIVE, 평가자, 관련 틱, 관찰 내용을 입력해 기록한다. 저장 결과는 `simulator/saved/result-*.json`에 실행 전체와 함께 보존된다.
