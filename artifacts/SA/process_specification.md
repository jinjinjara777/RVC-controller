# Process Specifications

상태: 검토용 초안. 요구사항 식별자 및 미정 항목은 [Event List](event_list.md)를 따른다. 데이터와 제어 의미는 [Data Dictionary](data_dictionary.md)를 따른다. 각 레벨 이후 기존 명세를 보존하며 하위 명세를 추가한다. Level 4 FSM의 별도 Process Specification은 만들지 않는다.

## Level 0

### 0 RVC Controller

| Field | Description |
|---|---|
| Process ID | 0 |
| Process Name | RVC Controller |
| DFD Level | 0 |
| Parent Process | 없음 |
| Purpose | 자동 청소·물걸레, 이동, 장애물 회피 및 먼지에 따른 일시적 청소 강화를 제어한다. |
| Inputs | Front Sensor Input, Left Sensor Input, Right Sensor Input, Dust Sensor Input |
| Outputs | Direction, Clean |
| Trigger / Execution Condition | 자동 청소 기능이 실행되는 동안 관측값 변화 및 내부 동작 진행. |
| Relevant Requirements | R1–R7 |
| Data Stores | 없음 |

처리 논리:

1. 센서 입력을 받아 장애물과 먼지 관측을 구성한다.
2. 정상 청소 중 직진한다. 장애물 감지 시 청소를 중지하고 좌측 또는 우측으로 회전한 뒤 직진하며 청소를 재개한다.
3. 전방·좌측·우측이 모두 막히면 후진한 뒤 좌측 또는 우측으로 회전하고 직진한다.
4. 먼지 감지 시 청소 출력을 일시적으로 강화한다. 시간·회피와의 우선순위·물걸레 세부 동작은 TBD이다.


## Level 1

### 1 센서 관측 구성

| Field | Description |
|---|---|
| Process ID | 1 |
| Process Name | 센서 관측 구성 |
| DFD Level | 1 |
| Parent Process | 0 |
| Purpose | 장애물 및 먼지 센서 입력을 제어에 필요한 관측값으로 구성한다. |
| Inputs | Front Sensor Input, Left Sensor Input, Right Sensor Input, Dust Sensor Input |
| Outputs | Obstacle Observation, Dust Observation |
| Trigger / Execution Condition | 센서 입력 수신; 표본 동기화·주기 TBD. |
| Relevant Requirements | R3, R4, R5 |
| Data Stores | 없음 |

처리 논리:

1. 전방·좌측·우측 입력의 의미를 보존하여 Obstacle Observation을 구성한다.
2. 먼지 입력의 의미를 보존하여 Dust Observation을 구성한다. 오류 처리·필터링·임계값을 새로 정의하지 않는다.

### 2 자동 청소 제어

| Field | Description |
|---|---|
| Process ID | 2 |
| Process Name | 자동 청소 제어 |
| DFD Level | 1 |
| Parent Process | 0 |
| Purpose | 장애물과 먼지 관측으로 이동 및 청소 의도를 결정한다. |
| Inputs | Obstacle Observation, Dust Observation |
| Outputs | Motion Intent, Cleaning Intent |
| Trigger / Execution Condition | 관측 수신 또는 내부 동작 진행; 구체 시점 TBD. |
| Relevant Requirements | R1, R2, R3, R4, R5 |
| Data Stores | 없음 |

처리 논리:

1. Obstacle Observation과 Dust Observation으로 제어 조건을 구성한다.
2. R2~R5에 따라 동작 순서와 일시적 출력 강화를 판단한다. 이동 진행 상태와 강화 경과는 내부에서 기억한다.
3. Motion Intent와 Cleaning Intent를 출력한다. 회피 필요 조건의 일반화·회전 선택·완료 조건·동시 이벤트 정책은 TBD이다.

### 3 구동 명령 전달

| Field | Description |
|---|---|
| Process ID | 3 |
| Process Name | 구동 명령 전달 |
| DFD Level | 1 |
| Parent Process | 0 |
| Purpose | 제어 의도를 장치 경계의 논리 명령으로 전달한다. |
| Inputs | Motion Intent, Cleaning Intent |
| Outputs | Direction, Clean |
| Trigger / Execution Condition | 이동 또는 청소 의도 생성. |
| Relevant Requirements | R1, R2, R3, R4, R5, R6 |
| Data Stores | 없음 |

처리 논리:

1. Motion Intent를 Direction으로 전달한다.
2. Cleaning Intent를 Clean으로 전달한다. 별도 정책이나 HW 프로토콜을 추가하지 않는다.


## Level 2

### 1.1 장애물 관측 구성

| Field | Description |
|---|---|
| Process ID | 1.1 |
| Process Name | 장애물 관측 구성 |
| DFD Level | 2 |
| Parent Process | 1 |
| Purpose | 세 방향의 감지 결과를 묶는다. |
| Inputs | Front Sensor Input, Left Sensor Input, Right Sensor Input |
| Outputs | Obstacle Observation |
| Trigger / Execution Condition | 장애물 센서 입력 수신. |
| Relevant Requirements | R3, R4 |
| Data Stores | 없음 |

처리 논리:

1. 전방·좌측·우측 결과를 각각 front, left, right 필드로 보존한다.
2. Obstacle Observation으로 전달한다. 세 입력의 동기화와 유효성 정책은 TBD이다.

### 1.2 먼지 관측 구성

| Field | Description |
|---|---|
| Process ID | 1.2 |
| Process Name | 먼지 관측 구성 |
| DFD Level | 2 |
| Parent Process | 1 |
| Purpose | 먼지 감지 결과를 논리 관측값으로 전달한다. |
| Inputs | Dust Sensor Input |
| Outputs | Dust Observation |
| Trigger / Execution Condition | 먼지 센서 입력 수신. |
| Relevant Requirements | R5 |
| Data Stores | 없음 |

처리 논리:

1. Dust Sensor Input의 감지 의미를 Dust Observation으로 전달한다.
2. 주기·필터·임계값을 임의로 정하지 않는다.

### 2.1 동작 판단

| Field | Description |
|---|---|
| Process ID | 2.1 |
| Process Name | 동작 판단 |
| DFD Level | 2 |
| Parent Process | 2 |
| Purpose | 이동과 청소 제어 결정을 생성한다. |
| Inputs | Obstacle Observation, Dust Observation |
| Outputs | Control Decision |
| Trigger / Execution Condition | 관측 수신 또는 내부 동작·강화 시간의 진행. |
| Relevant Requirements | R1, R2, R3, R4, R5 |
| Data Stores | 없음 |

처리 논리:

1. 관측값을 보존하면서 전방·좌측·우측 모두 막힘 조건을 산출한다.
2. 상태 제어로 직진·회피·후진 및 일시적 청소 강화 의도를 결정한다.
3. 두 의도를 Control Decision으로 묶어 전달한다. 미정 조건은 확정하지 않는다.

### 2.2 제어 의도 분리

| Field | Description |
|---|---|
| Process ID | 2.2 |
| Process Name | 제어 의도 분리 |
| DFD Level | 2 |
| Parent Process | 2 |
| Purpose | 하나의 결정을 이동 의도와 청소 의도로 분리한다. |
| Inputs | Control Decision |
| Outputs | Motion Intent, Cleaning Intent |
| Trigger / Execution Condition | Control Decision 생성. |
| Relevant Requirements | R1, R2, R3, R4, R5 |
| Data Stores | 없음 |

처리 논리:

1. Control Decision의 이동 필드를 Motion Intent로 전달한다.
2. 청소·물걸레 필드를 Cleaning Intent로 전달한다. 분리 과정에서 정책을 추가하지 않는다.

### 3.1 이동 명령 전달

| Field | Description |
|---|---|
| Process ID | 3.1 |
| Process Name | 이동 명령 전달 |
| DFD Level | 2 |
| Parent Process | 3 |
| Purpose | 이동 의도를 장치 경계에 전달한다. |
| Inputs | Motion Intent |
| Outputs | Direction |
| Trigger / Execution Condition | Motion Intent 생성. |
| Relevant Requirements | R2, R3, R4, R6 |
| Data Stores | 없음 |

처리 논리:

1. 의도의 직진·좌회전·우회전·후진 의미를 보존하여 Direction으로 전달한다.
2. HW 인코딩·속도·각도·거리의 상세 설계는 하지 않는다.

### 3.2 청소 명령 전달

| Field | Description |
|---|---|
| Process ID | 3.2 |
| Process Name | 청소 명령 전달 |
| DFD Level | 2 |
| Parent Process | 3 |
| Purpose | 청소 및 물걸레 의도를 장치 경계에 전달한다. |
| Inputs | Cleaning Intent |
| Outputs | Clean |
| Trigger / Execution Condition | Cleaning Intent 생성. |
| Relevant Requirements | R1, R2, R3, R5, R6 |
| Data Stores | 없음 |

처리 논리:

1. 의도의 청소 수행·중지·재개·출력 강화 의미 및 물걸레 제어 정보를 Clean으로 전달한다.
2. 강화 정도와 물걸레의 독립 제어 방식은 TBD이다. HW 상세 설계는 하지 않는다.


## Level 3

### 2.1.1 제어 조건 구성

| Field | Description |
|---|---|
| Process ID | 2.1.1 |
| Process Name | 제어 조건 구성 |
| DFD Level | 3 |
| Parent Process | 2.1 |
| Purpose | 상태 제어에 필요한 관측 및 모두 막힘 조건을 구성한다. |
| Inputs | Obstacle Observation, Dust Observation |
| Outputs | Control Conditions |
| Trigger / Execution Condition | Obstacle Observation 또는 Dust Observation 수신. |
| Relevant Requirements | R3, R4, R5 |
| Data Stores | 없음 |

처리 논리:

1. 전방·좌측·우측 결과를 보존한다.
2. all_blocked = front AND left AND right를 산출한다.
3. Obstacle Observation과 Dust Observation 및 all_blocked를 Control Conditions로 전달한다. 그 밖의 회피 필요 조건은 TBD이다.

### 2.1.2 Controller

| Field | Description |
|---|---|
| Process ID | 2.1.2 |
| Process Name | Controller |
| DFD Level | 3 |
| Parent Process | 2.1 |
| Purpose | 내부 상태를 이용해 제어 결정을 생성한다. |
| Inputs | Control Conditions |
| Outputs | Control Decision |
| Trigger / Execution Condition | Control Conditions 수신 및 동작/시간의 내부 진행. 완료 판정 수단은 TBD. |
| Relevant Requirements | R1, R2, R3, R4, R5 |
| Data Stores | 없음 |

처리 논리:

1. 정상 자동 청소 상태에서는 직진 및 청소·물걸레 수행 의도를 구성한다.
2. 장애물 회피 시 청소 중지 후 회전하고 직진하며 청소를 재개한다. 모두 막힌 경우에는 회전 전에 후진한다.
3. 먼지 감지 시 한동안 청소 출력을 강화한다. 강화 종료를 위한 내부 시간 의미는 요구되나 지속시간과 시간 구현은 TBD이다.
4. Control Decision을 출력한다. 상태 전이의 세부 초안은 Level 4 FSM을 참조한다. 미정 조건을 실행 가능한 정책으로 대체하지 않는다.

