# SD-to-Implementation Module Traceability

검사 명령: `python scripts/check_traceability.py`. SD의 13개 모듈이 C 함수에 존재하고 모듈 간 12개 직접 호출 관계가 일치함을 소스에서 검사했다. 생명주기, 직렬화 및 모듈 내부 보조 함수는 구조도상의 기능 모듈과 구분한다.

| SD Module | C Function | Source |
|---|---|---|
| Main | main | [src/main.c](../../src/main.c) |
| Controller | rvc_controller | [src/rvc.c](../../src/rvc.c) |
| AcquireSensors | acquire_sensors | [src/rvc.c](../../src/rvc.c) |
| ObserveObstacles | observe_obstacles | [src/rvc.c](../../src/rvc.c) |
| ObserveDust | observe_dust | [src/rvc.c](../../src/rvc.c) |
| ComputeControl | compute_control | [src/rvc.c](../../src/rvc.c) |
| EvaluateBehavior | evaluate_behavior | [src/rvc.c](../../src/rvc.c) |
| BuildConditions | build_conditions | [src/rvc.c](../../src/rvc.c) |
| StepFSM | step_fsm | [src/fsm.c](../../src/fsm.c) |
| SplitIntents | split_intents | [src/rvc.c](../../src/rvc.c) |
| DeliverCommands | deliver_commands | [src/rvc.c](../../src/rvc.c) |
| SendMotion | send_motion | [src/rvc.c](../../src/rvc.c) |
| SendCleaning | send_cleaning | [src/rvc.c](../../src/rvc.c) |

## 확인 결과

- 모듈 13개 / 기능 모듈 간 직접 호출 12개 일치. DFD의 정보 흐름을 함수 호출로 복사하지 않았다.
- 저장된 20개 × 100틱의 센서 입력을 최종 C 실행 파일에 다시 재생하여 기존 전체 C 출력과 일치함을 확인했다. 입력 파서 수정·회전 선택 리팩터링 이후에도 저장된 제어 동작은 동일하다.
- 상태는 `fsm.c`의 불투명 컨텍스트가 소유하며 다른 모듈은 읽기 전용 복사본만 받는다.
- FILE 포트, 컨텍스트 생명주기, 진단 상태와 오류 반환의 구체화는 [승인된 시뮬레이션 프로파일](../SD/simulation_profile.md)에 기록했다.
- R1~R5의 상세 기대값은 [단위 테스트](unit_test_cases.md), [시스템 시나리오](../SystemTest/test_scenarios.md)에서 추적한다.
