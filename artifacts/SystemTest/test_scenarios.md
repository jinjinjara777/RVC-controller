# RVC System Test Scenarios

20개 시나리오 모두 10×10 지도와 최대 100틱을 사용한다. 좌표는 [x,y], 방향은 북=0/동=1/남=2/서=3이다. 나열되지 않은 칸은 빈 칸이다. 원본 요구사항의 기대 동작과 승인된 [P1 프로파일](../SD/simulation_profile.md)의 상세 동작을 구분해 검토한다. 템플릿 예시의 15×15 오기는 스킬의 10×10 제약에 맞게 적용했다.

## ST-01 먼지 경로와 전방 회피 · 북

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 0
- Obstacles: [[4, 2]]
- Dust: [[4, 4], [4, 5], [2, 5]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-02 먼지 경로와 전방 회피 · 동

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 1
- Obstacles: [[6, 4]]
- Dust: [[4, 4], [3, 4], [3, 2]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-03 먼지 경로와 전방 회피 · 남

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 2
- Obstacles: [[4, 6]]
- Dust: [[4, 4], [4, 3], [6, 3]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-04 먼지 경로와 전방 회피 · 서

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 3
- Obstacles: [[2, 4]]
- Dust: [[4, 4], [5, 4], [5, 6]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-05 좌측 막힘과 우회전 · 북

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 0
- Obstacles: [[4, 3], [3, 4]]
- Dust: [[4, 4], [4, 5], [2, 5]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-06 좌측 막힘과 우회전 · 동

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 1
- Obstacles: [[5, 4], [4, 3]]
- Dust: [[4, 4], [3, 4], [3, 2]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-07 좌측 막힘과 우회전 · 남

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 2
- Obstacles: [[4, 5], [5, 4]]
- Dust: [[4, 4], [4, 3], [6, 3]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-08 좌측 막힘과 우회전 · 서

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 3
- Obstacles: [[3, 4], [4, 5]]
- Dust: [[4, 4], [5, 4], [5, 6]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-09 세 방향 막힘과 후진 · 북

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 0
- Obstacles: [[4, 3], [3, 4], [5, 4]]
- Dust: [[4, 4], [4, 5], [2, 5]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화, 세 방향 막힘 후진
- Requirement IDs: R1, R2, R3, R5, R4
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다. 세 방향이 막힌 초기 배치에서는 먼저 후진한 뒤 회전하고 전진한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-10 세 방향 막힘과 후진 · 동

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 1
- Obstacles: [[5, 4], [4, 3], [4, 5]]
- Dust: [[4, 4], [3, 4], [3, 2]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화, 세 방향 막힘 후진
- Requirement IDs: R1, R2, R3, R5, R4
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다. 세 방향이 막힌 초기 배치에서는 먼저 후진한 뒤 회전하고 전진한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-11 세 방향 막힘과 후진 · 남

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 2
- Obstacles: [[4, 5], [5, 4], [3, 4]]
- Dust: [[4, 4], [4, 3], [6, 3]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화, 세 방향 막힘 후진
- Requirement IDs: R1, R2, R3, R5, R4
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다. 세 방향이 막힌 초기 배치에서는 먼저 후진한 뒤 회전하고 전진한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-12 세 방향 막힘과 후진 · 서

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 3
- Obstacles: [[3, 4], [4, 5], [4, 3]]
- Dust: [[4, 4], [5, 4], [5, 6]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화, 세 방향 막힘 후진
- Requirement IDs: R1, R2, R3, R5, R4
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다. 세 방향이 막힌 초기 배치에서는 먼저 후진한 뒤 회전하고 전진한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-13 좁은 통로의 강화 청소 · 북

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 0
- Obstacles: [[3, 4], [5, 4], [3, 3], [5, 3], [3, 2], [5, 2], [4, 1]]
- Dust: [[4, 4], [4, 5], [2, 5]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-14 좁은 통로의 강화 청소 · 동

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 1
- Obstacles: [[4, 3], [4, 5], [5, 3], [5, 5], [6, 3], [6, 5], [7, 4]]
- Dust: [[4, 4], [3, 4], [3, 2]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-15 좁은 통로의 강화 청소 · 남

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 2
- Obstacles: [[5, 4], [3, 4], [5, 5], [3, 5], [5, 6], [3, 6], [4, 7]]
- Dust: [[4, 4], [4, 3], [6, 3]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-16 좁은 통로의 강화 청소 · 서

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 3
- Obstacles: [[4, 5], [4, 3], [3, 5], [3, 3], [2, 5], [2, 3], [1, 4]]
- Dust: [[4, 4], [5, 4], [5, 6]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-17 연속 벽과 방향 재판단 · 북

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 0
- Obstacles: [[4, 2], [3, 2], [2, 2], [6, 4]]
- Dust: [[4, 4], [4, 5], [2, 5]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-18 연속 벽과 방향 재판단 · 동

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 1
- Obstacles: [[6, 4], [6, 3], [6, 2], [4, 6]]
- Dust: [[4, 4], [3, 4], [3, 2]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-19 연속 벽과 방향 재판단 · 남

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 2
- Obstacles: [[4, 6], [5, 6], [6, 6], [2, 4]]
- Dust: [[4, 4], [4, 3], [6, 3]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

## ST-20 연속 벽과 방향 재판단 · 서

- Grid: 10×10
- Start: [4, 4]
- Initial Direction: 3
- Obstacles: [[2, 4], [2, 5], [2, 6], [4, 2]]
- Dust: [[4, 4], [5, 4], [5, 6]]
- Maximum Ticks: 100
- Essential Functions: 자동 청소·물걸레, 직진, 장애물 회피·청소 재개, 먼지 출력 강화
- Requirement IDs: R1, R2, R3, R5
- SA: [Event List](../SA/event_list.md), [Process Specifications](../SA/process_specification.md), [FSM](../SA/DFD/dfd_level_4_fsm.md)

Expected Behavior: 직진 시 청소와 물걸레를 수행하고, 먼지 감지 시 일시적으로 출력을 강화한다. 장애물 회피 중 청소를 중지하고 회전 후 전진하며 재개한다.

Human Evaluation: **PENDING**. 평가자·결과(PASS/FAIL/INCONCLUSIVE)·관찰·관련 틱은 웹 화면에서 기록한다. 틱 제한 도달로 자동 판정하지 않는다.

