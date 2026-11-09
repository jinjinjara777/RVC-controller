# Data Dictionary

상태: 검토용 초안. 원본은 [예비 요구사항](../../docs/preliminary_requirement.md). R1~R7은 [Event List](event_list.md)의 식별자를 따른다. 논리 형식은 분석 표현이며 C 타입이나 HW 인코딩을 확정하지 않는다. TBD는 미정이다.

## Event List 기반 초기화

| Input/Output Event | Description | Format / Type |
|---|---|---|
| Front Sensor Input | 입력 / 상태 데이터: 전방 장애물 감지 결과를 센서에서 제어기로 전달한다. 근거: R3, R4. | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Left Sensor Input | 입력 / 상태 데이터: 좌측 장애물 감지 결과를 센서에서 제어기로 전달한다. 근거: R3, R4. | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Right Sensor Input | 입력 / 상태 데이터: 우측 장애물 감지 결과를 센서에서 제어기로 전달한다. 근거: R3, R4. | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Dust Sensor Input | 입력 / 상태 데이터: 먼지 감지 결과를 센서에서 제어기로 전달한다. 근거: R5. | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Direction | 출력 / 제어 명령: 이동 구동장치에 직진, 좌·우 회전 또는 후진 명령을 전달한다. 근거: R2, R3, R4. | 논리 명령; 인코딩·거리·속도·각도 TBD |
| Clean | 출력 / 제어 명령: 청소·물걸레 구동장치에 자동 청소·물걸레 수행에 필요한 제어 정보를 전달한다. 요구된 청소 동작에는 수행, 중지, 재개 및 일시적 출력 강화가 포함된다. 근거: R1, R2, R3, R5. | 복합 논리 명령; 출력량·물걸레 상세 제어 TBD |

아래 증분 항목의 정의 표와 레벨별 경로 표를 함께 읽는다. 경로 표가 각 정의의 Source, Destination, DFD Level을 제공한다. Data Store는 현재 요구사항에서 도출되지 않았다.

## Level 0 증분 갱신

### Clean

| Field | Definition |
|---|---|
| Data Name | Clean |
| Description | 청소·물걸레 구동장치로 전달하는 제어 정보. 청소 수행·중지·재개·일시적 출력 강화를 포함한다. |
| Format / Type | 복합 논리 명령; 출력량·물걸레 상세 제어 TBD |
| Flow Category | Control |
| Requirement Reference | R1, R2, R3, R5 |

### Direction

| Field | Definition |
|---|---|
| Data Name | Direction |
| Description | 이동 구동장치로 전달하는 직진·좌회전·우회전·후진 제어 명령. |
| Format / Type | 논리 명령; 인코딩·거리·속도·각도 TBD |
| Flow Category | Control |
| Requirement Reference | R2, R3, R4 |

### Dust Sensor Input

| Field | Definition |
|---|---|
| Data Name | Dust Sensor Input |
| Description | 먼지 감지 결과. |
| Format / Type | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Flow Category | Data |
| Requirement Reference | R5 |

### Front Sensor Input

| Field | Definition |
|---|---|
| Data Name | Front Sensor Input |
| Description | 전방 장애물 감지 결과. |
| Format / Type | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Flow Category | Data |
| Requirement Reference | R3, R4 |

### Left Sensor Input

| Field | Definition |
|---|---|
| Data Name | Left Sensor Input |
| Description | 좌측 장애물 감지 결과. |
| Format / Type | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Flow Category | Data |
| Requirement Reference | R3, R4 |

### Right Sensor Input

| Field | Definition |
|---|---|
| Data Name | Right Sensor Input |
| Description | 우측 장애물 감지 결과. |
| Format / Type | 감지 결과; 물리 형식·유효성·갱신 주기 TBD |
| Flow Category | Data |
| Requirement Reference | R3, R4 |

| Data Name | Flow Category | Source | Destination | DFD Level | Requirement Reference |
|---|---|---|---|---|---|
| Front Sensor Input | Data | FrontSensor | 0 | 0 | R3, R4 |
| Left Sensor Input | Data | LeftSensor | 0 | 0 | R3, R4 |
| Right Sensor Input | Data | RightSensor | 0 | 0 | R3, R4 |
| Dust Sensor Input | Data | DustSensor | 0 | 0 | R5 |
| Direction | Control | 0 | MovementActuator | 0 | R2, R3, R4 |
| Clean | Control | 0 | CleaningActuator | 0 | R1, R2, R3, R5 |

기존 정의를 보존했다. 이 레벨에서 추가된 Data Store는 없다.

## Level 1 증분 갱신

### Cleaning Intent

| Field | Definition |
|---|---|
| Data Name | Cleaning Intent |
| Description | 제어기가 결정한 청소·물걸레 제어 의도. 청소 중지·재개·출력 강화 의미를 포함한다. |
| Format / Type | 복합 논리 명령; Clean과 동일한 의미, 장치 인코딩 전 |
| Flow Category | Control |
| Requirement Reference | R1, R2, R3, R5 |

### Dust Observation

| Field | Definition |
|---|---|
| Data Name | Dust Observation |
| Description | 먼지 감지 결과의 논리적 표현. 감지 임계값을 새로 정하지 않는다. |
| Format / Type | 먼지 감지/비감지; 물리 형식 TBD |
| Flow Category | Data |
| Requirement Reference | R5 |

### Motion Intent

| Field | Definition |
|---|---|
| Data Name | Motion Intent |
| Description | 제어기가 결정한 직진·좌회전·우회전·후진 의도. |
| Format / Type | 논리 명령; Direction과 동일한 의미, 장치 인코딩 전 |
| Flow Category | Control |
| Requirement Reference | R2, R3, R4 |

### Obstacle Observation

| Field | Definition |
|---|---|
| Data Name | Obstacle Observation |
| Description | 전방·좌측·우측 감지 결과를 이름 있는 필드로 묶은 관측값. 회피 정책을 포함하지 않는다. |
| Format / Type | {front, left, right}; 각 필드 감지/비감지, 물리 형식 TBD |
| Flow Category | Data |
| Requirement Reference | R3, R4 |

| Data Name | Flow Category | Source | Destination | DFD Level | Requirement Reference |
|---|---|---|---|---|---|
| Front Sensor Input | Data | FrontSensor | 1 | 1 | R3, R4 |
| Left Sensor Input | Data | LeftSensor | 1 | 1 | R3, R4 |
| Right Sensor Input | Data | RightSensor | 1 | 1 | R3, R4 |
| Dust Sensor Input | Data | DustSensor | 1 | 1 | R5 |
| Obstacle Observation | Data | 1 | 2 | 1 | R3, R4 |
| Dust Observation | Data | 1 | 2 | 1 | R5 |
| Motion Intent | Control | 2 | 3 | 1 | R2, R3, R4 |
| Cleaning Intent | Control | 2 | 3 | 1 | R1, R2, R3, R5 |
| Direction | Control | 3 | MovementActuator | 1 | R2, R3, R4 |
| Clean | Control | 3 | CleaningActuator | 1 | R1, R2, R3, R5 |

기존 정의를 보존했다. 이 레벨에서 추가된 Data Store는 없다.

## Level 2 증분 갱신

### Control Decision

| Field | Definition |
|---|---|
| Data Name | Control Decision |
| Description | 제어기가 생성한 이동 의도와 청소 의도의 묶음. 두 의도의 동시 발생 충돌 정책은 TBD. |
| Format / Type | {Motion Intent, Cleaning Intent} |
| Flow Category | Control |
| Requirement Reference | R1, R2, R3, R4, R5 |

| Data Name | Flow Category | Source | Destination | DFD Level | Requirement Reference |
|---|---|---|---|---|---|
| Front Sensor Input | Data | FrontSensor | 1.1 | 2 | R3, R4 |
| Left Sensor Input | Data | LeftSensor | 1.1 | 2 | R3, R4 |
| Right Sensor Input | Data | RightSensor | 1.1 | 2 | R3, R4 |
| Dust Sensor Input | Data | DustSensor | 1.2 | 2 | R5 |
| Obstacle Observation | Data | 1.1 | 2 | 2 | R3, R4 |
| Dust Observation | Data | 1.2 | 2 | 2 | R5 |
| Obstacle Observation | Data | 1 | 2.1 | 2 | R3, R4 |
| Dust Observation | Data | 1 | 2.1 | 2 | R5 |
| Control Decision | Control | 2.1 | 2.2 | 2 | R1, R2, R3, R4, R5 |
| Motion Intent | Control | 2.2 | 3 | 2 | R2, R3, R4 |
| Cleaning Intent | Control | 2.2 | 3 | 2 | R1, R2, R3, R5 |
| Motion Intent | Control | 2 | 3.1 | 2 | R2, R3, R4 |
| Cleaning Intent | Control | 2 | 3.2 | 2 | R1, R2, R3, R5 |
| Direction | Control | 3.1 | MovementActuator | 2 | R2, R3, R4 |
| Clean | Control | 3.2 | CleaningActuator | 2 | R1, R2, R3, R5 |

기존 정의를 보존했다. 이 레벨에서 추가된 Data Store는 없다.

## Level 3 증분 갱신

### Control Conditions

| Field | Definition |
|---|---|
| Data Name | Control Conditions |
| Description | 관측값과 전방·좌측·우측 모두 장애물인지 여부를 보존한 제어 판단 자료. 회피 필요 여부의 일반 규칙은 TBD. |
| Format / Type | {Obstacle Observation, Dust Observation, all_blocked}; all_blocked = front AND left AND right |
| Flow Category | Data |
| Requirement Reference | R3, R4, R5 |

| Data Name | Flow Category | Source | Destination | DFD Level | Requirement Reference |
|---|---|---|---|---|---|
| Obstacle Observation | Data | 1 | 2.1.1 | 3 | R3, R4 |
| Dust Observation | Data | 1 | 2.1.1 | 3 | R5 |
| Control Conditions | Data | 2.1.1 | 2.1.2 | 3 | R3, R4, R5 |
| Control Decision | Control | 2.1.2 | 2.2 | 3 | R1, R2, R3, R4, R5 |

기존 정의를 보존했다. 이 레벨에서 추가된 Data Store는 없다.
