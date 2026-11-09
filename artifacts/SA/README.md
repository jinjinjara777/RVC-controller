# RVC Controller Structured Analysis

상태: **인간 검토 전 초안 — 요구사항 미정 사항 있음**. 이번 작업은 SA 범위이며 SD·구현으로의 진행을 승인하는 문서가 아니다.

## 문서

| 산출물 | 내용 |
|---|---|
| [Event List](event_list.md) | 외부 입출력 6개, R1~R7 추적성 및 초기 미정 사항 |
| [Context Diagram](context_diagram.md) | 제어기와 외부 센서·구동장치 경계 |
| [DFD Level 0](DFD/dfd_level_0.md) | Process 0으로 전체 시스템 표현 |
| [DFD Level 1](DFD/dfd_level_1.md) | 센서 관측 구성 / 자동 청소 제어 / 구동 명령 전달 |
| [DFD Level 2](DFD/dfd_level_2.md) | 각 Level 1 프로세스의 기능 분해 |
| [DFD Level 3](DFD/dfd_level_3.md) | 2.1의 조건 구성 / Controller 분리 |
| [Level 4 Controller FSM](DFD/dfd_level_4_fsm.md) | 2.1.2의 상태·전이·미정 조건 |
| [Data Dictionary](data_dictionary.md) | 레벨별로 누적한 데이터·제어 흐름 정의와 경로 |
| [Process Specifications](process_specification.md) | Level 0~3 전체 12개 프로세스 명세 |
| [검사 결과](validation_report.md) | 실행한 구조 검사와 한계 |

## 분해 계층

```text
0 RVC Controller
├─ 1 센서 관측 구성
│  ├─ 1.1 장애물 관측 구성
│  └─ 1.2 먼지 관측 구성
├─ 2 자동 청소 제어
│  ├─ 2.1 동작 판단
│  │  ├─ 2.1.1 제어 조건 구성
│  │  └─ 2.1.2 Controller → Level 4 FSM
│  └─ 2.2 제어 의도 분리
└─ 3 구동 명령 전달
   ├─ 3.1 이동 명령 전달
   └─ 3.2 청소 명령 전달
```

DFD의 화살표는 함수 호출 순서가 아닌 데이터·제어 정보의 전달이다. 영속 데이터 저장소, 사용자 버튼, 배터리, 도킹, 외부 Tick, 장치 완료 피드백은 요구사항에 없어 추가하지 않았다. 물리 하드웨어 상세 제어는 R6에 따라 분석 범위 밖이다.

## 상세화 전에 확인할 요구사항

| ID | 미정 사항 | 영향 |
|---|---|---|
| Q1 | 어떤 장애물 감지 조합이 회피를 시작하는가? | avoid_required_TBD 및 정상 직진 조건 |
| Q2 | 좌우 회전 선택 기준, 회전량 및 완료 판정은 무엇인가? | Turning 전이와 Direction 의미 |
| Q3 | 후진 종료 조건과 후방 장애물 처리는 무엇인가? | Backward 전이 |
| Q4 | 청소 강화 정도·지속시간과 먼지 재감지 시 처리는 무엇인가? | Boost 전이와 내부 시간 의미 |
| Q5 | 장애물 회피와 먼지 감지가 겹치면 청소 출력과 강화 시간을 어떻게 처리하는가? | 직교 영역의 출력 충돌·우선순위 |
| Q6 | 물걸레의 회피 중 동작과 청소 출력 강화의 관계는 무엇인가? | Cleaning Intent 및 Clean 상세 정의 |
| Q7 | 자동 청소 시작·종료, 센서 갱신·유효성 및 동작 중 새 감지 처리 기준은 무엇인가? | FSM 초기/종료 및 입력 처리 정책 |

이 항목은 임의 정책으로 대체하지 않았다. 현재 문서로 요구된 기능과 분해 경계를 검토할 수 있으나, 미정 사항 해소와 인간의 SA 승인을 거쳐야 SD로 진행할 수 있다.

## 검사 재실행

`python artifacts/SA/validate_sa.py`

`build_dfd.py`는 이번 초안의 최초 생성과 레벨별 누적 갱신 기록을 재현하는 보조 소스이며 기존 Dictionary/Specifications가 있으면 중단한다. 후속 수정 시 이를 무조건 재실행하여 기존 정의를 덮어쓰지 않는다. `dfd_model.json`은 구조 검사의 기준 모델이며 DFD 수정 시 함께 검토한다.
