# Web-Based RVC Simulator Specification

## 1. Overview

로컬 웹 UI에서 실제 C11 제어기의 자동 청소·물걸레, 장애물 회피·후진, 먼지 출력을 관찰한다. [P1 프로파일](../SD/simulation_profile.md)의 기본값은 사용자 확인을 받았다. 시스템 테스트의 판정은 사람이 수행한다.

## 2. Execution Architecture

| 계층 | 구현 | 책임 |
|---|---|---|
| 제어기 | src/main.c, src/rvc.c, src/fsm.c | SD의 모듈 호출, 상태 전이와 이동·청소 결정 |
| 환경 | simulator/model.py | 지도 검증, 센서 생성, C 실행 및 물리 효과, history |
| 로컬 HTTP | simulator/server.py | 세션·시나리오·평가 저장 API, 정적 UI 제공 |
| 화면 | simulator/web/ | 지도 편집·재생·상태 표시·기록 조회 |

통신은 센서 4개를 공백으로 구분한 stdin 한 줄 → 명령과 상태의 stdout JSON 한 줄이다. 백엔드는 최대 100줄 누적 입력을 실행 파일에 재생해 마지막 응답을 사용한다. 세션마다 새 FSM 컨텍스트로 시작한다. Python/JS는 장애물 회피나 청소 강화 결정을 하지 않는다.

| 추상 인터페이스 | 실제 인터페이스 |
|---|---|
| initialize(configuration) | POST /api/new → id, normalized config, tick 0 frame |
| step(sensor_inputs) | POST /api/step, id. 센서는 환경 모델이 지도에서 생성 |
| get_state() | GET /api/trace/{id} → history 마지막 frame 또는 과거 frame |
| reset() | POST /api/new, 동일 initial config. 이전 id 교체 가능 |
| scenario save/load | POST /api/scenarios, GET /api/scenarios |
| evaluation | POST /api/evaluate → 수동 평가 및 전체 trace 저장 |

서버는 127.0.0.1에만 바인딩한다. 포트 기본값은 8765이며 --port로 변경할 수 있다. 검증용 브라우저 테스트는 8766을 사용했다.

## 3. Grid Map

10×10, 좌표 0~9. 기본 시작 (4,4), 방향 북쪽이다. 빈 칸·장애물·먼지를 구분하고, 청소·물걸레 경로를 별도 표시한다. 지도 밖은 장애물이다. 시작점과 장애물, 장애물과 먼지의 중첩은 거부한다. 잘못된 지도는 기존 지도를 바꾸지 않고 오류를 표시한다.

장애물·먼지 추가/제거, 시작점·방향·틱 제한 변경, 지도 비우기, 원본 지도 복원, JSON 저장/불러오기, 사용자 시나리오 저장을 지원한다. 편집 시 실행 기록은 초기 상태로 복원한다. 자동 실행·요청 처리 중에는 지도 변경을 막는다.

## 4. Controls and Visualization

시작, 일시정지, 한 틱, 재설정, 다시 실행, 1×/2×/6× 속도, 시나리오 선택, 이전·다음 기록과 슬라이더를 제공한다. 자동 실행은 설정된 최대 1~100틱에서 멈춘다. UI와 서버 양쪽에서 상한을 유지한다.

재설정은 초기 지도·먼지·위치·방향·제어 상태·타이머·기록을 복원하고 정지한다. 다시 실행은 복원 후 자동 재생한다. 이전 틱은 저장된 snapshot을 조회하며 C 상태를 역실행하지 않는다. 과거에서 재생하면 기존 기록을 따라간 뒤 새로운 틱을 생성한다.

## 5. Tick Semantics

1. 현재 위치와 방향에서 전방·좌측·우측 장애물 및 현재 칸의 먼지를 감지한다.
2. 실제 C 제어기의 입력→판단→출력 호출을 1회 실행한다.
3. 청소·물걸레가 켜져 있으면 **이동 전 현재 칸**에 효과를 적용한다.
4. 모터 명령에 따라 1칸 이동 또는 90도 회전을 적용한다. 목적지가 막혔으면 이동을 차단하고 기록한다.
5. 환경 적용 후 상태와 C 입력·출력·진단값을 snapshot으로 기록한다.

따라서 snapshot의 센서는 **동작 전**, 위치·방향·지도는 **동작 후**의 값이다. 화면에 센서가 관측된 이전 위치·방향을 함께 표시한다. 다음 칸의 먼지는 다음 틱에 감지·청소한다.

## 6. Complete State Inspection

| 변수 | 출처 |
|---|---|
| tick, previous_state, state, state_ticks | C FsmSnapshot |
| front, left, right, dust | 환경 센서 입력과 C가 수신한 값 |
| motor | C Motion Intent → Direction |
| cleaner.enabled, mop, power | C Cleaning Intent → Clean |
| boost_remaining, boost_active, dust_pending, selected_turn | C 내부 상태의 읽기 전용 복사 |
| all_blocked | C 입력에 대한 세 방향 AND 조건 |
| position, direction, dust, cleaned, mopped, collision, changes | 환경 모델 적용 결과 |

고정 1틱 회전/후진에는 별도 countdown 변수를 만들지 않았다. state_ticks가 해당 상태 연속 평가 횟수이다. boost_remaining은 현재 틱 출력 적용 후 남은 **청소 가능 틱** 수이다. 마지막 강화 틱에는 boost_active=true, boost_remaining=0일 수 있다. 틱 0에서는 아직 관측하지 않은 C 상태·센서를 null로 보존한다.

## 7. History and Evaluation

초기 snapshot과 매 틱 전체 상태를 보존하고 과거 지도·먼지·출력을 함께 조회한다. trace JSON에는 P1 식별자, 초기 config, 모든 history, 수동 evaluation을 포함한다. 지도 JSON은 초기 config를 보존한다.

시스템 시나리오 20개는 각각 최소 3개 필수 기능과 요구사항/SA 근거를 가진다. 실제 실행 결과는 [test_results.md](test_results.md), 구성은 [test_scenarios.md](test_scenarios.md), 요구사항 연결은 [requirement_traceability.md](requirement_traceability.md)에 있다.

평가자는 PASS/FAIL/INCONCLUSIVE를 직접 선택하고 이름·관찰·관련 틱을 입력한다. 평가자 없이 저장하거나 실행 전 평가하는 요청은 거부한다. 결과와 trace는 simulator/saved/result-*.json에 기록한다. 자동 검사는 시뮬레이터의 기계적 정합성을 대상으로 하며 시나리오의 사람 판정과 구분한다.

## 8. Validation and Limits

- C 단위 테스트, 환경 모델 테스트, 20개 × 100틱 실행, C 출력 재생 비교와 브라우저 조작 검증을 실행했다.
- 데스크톱 및 390px 모바일 화면을 캡처·확인했다. 지도·기록은 스크롤 가능하며 모바일 페이지 가로 넘침을 검사했다.
- 사람의 요구사항 판정은 대기 중이다. 자동 완주를 PASS로 바꾸지 않았다.
- 실제 HW 완료 피드백·안전 제어·후방 센서는 모델링하지 않았다. 후진 차단은 환경 효과이며 C 입력에 없는 후방 감지를 생성하지 않는다.
- P1은 이산 모델의 구체화이다. 실제 흡입 세기·속도·충전·도킹·최적 경로·전 영역 청소 보장을 검증하지 않는다.
