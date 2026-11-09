# DFD Level 3

상태: 검토용 초안. 요구사항의 TBD는 상세 동작 확정을 의미하지 않는다.

상태가 없는 제어 조건 구성과 상태를 가진 Controller를 분리한다. 다른 Level 2 말단은 현재 요구사항에서 더 나눌 근거가 없어 유지한다. Controller 2.1.2만 다음 Level 4 FSM으로 정제한다.

표기: 원은 데이터 처리, 점선 원은 제어 처리, 사각형은 해당 분해 경계의 외부 엔티티 또는 형제 프로세스이다. 실선은 데이터 흐름, 점선은 제어 명령 흐름이다. 영속 데이터 저장소는 요구되지 않아 추가하지 않았다. FSM의 동작 상태와 시간 경과는 제어 프로세스의 내부 기억이며 DB를 의미하지 않는다.

## Process 2.1 분해

```mermaid
flowchart LR
    P1["1 센서 관측 구성"]
    P2_1_1(("2.1.1 제어 조건 구성"))
    P2_1_2(("2.1.2 Controller"))
    P2_2["2.2 제어 의도 분리"]
    P1 -->|Obstacle Observation| P2_1_1
    P1 -->|Dust Observation| P2_1_1
    P2_1_1 -->|Control Conditions| P2_1_2
    P2_1_2 -.->|Control Decision| P2_2
    classDef control stroke-dasharray: 5 5
    class P2_1_2 control
```

부모 2.1 경계 입력: Dust Observation, Obstacle Observation.

부모 경계 출력: Control Decision. 이름·방향·상대 프로세스·흐름 종류를 그대로 보존한다.

관련 문서: [Data Dictionary](../data_dictionary.md), [Process Specifications](../process_specification.md), [요구사항 및 미정 사항](../event_list.md).
