# RVC Controller Event List

## 범위와 근거

- 상태: 검토용 초안. 후속 DFD·Data Dictionary·Process Specifications는 [SA 문서 목록](README.md)에서 확인할 수 있다.
- 원본: [예비 요구사항](../../docs/preliminary_requirement.md). 지침의 `preliminary_requirements.md`에 해당하는 실제 파일은 단수형 이름이다. 원본은 변경하지 않았다.
- 시스템 경계: 자동 청소 기능을 수행하는 RVC Controller. 센서와 이동·청소·물걸레 구동장치는 제어기 외부로 모델링한다. 이는 논리적 인터페이스 구분이며 하드웨어 상세 설계를 의미하지 않는다.
- 요구사항 식별자는 원문 문장에 추적성을 부여하기 위한 문서 내 식별자이다.

| 요구사항 ID | 원문 근거 |
|---|---|
| R1 | An RVC automatically cleans and mops household surface. |
| R2 | It goes straight forward while cleaning. |
| R3 | If its sensors found an obstacle, it stops cleaning, turns aside left or right, and goes forward with cleaning. |
| R4 | If there are obstacles in both front, left and right, it move backward and turn aside left or right, and goes forward. |
| R5 | If it detects dust, power up the cleaning for a while. |
| R6 | We do not consider the detail design and implementation on HW controls. |
| R7 | We only focus on the automatic cleaning function. |

## Event List

| Input/Output Event | Description |
|---|---|
| Front Sensor Input | 입력 / 상태 데이터: 전방 장애물 감지 결과를 센서에서 제어기로 전달한다. 근거: R3, R4. |
| Left Sensor Input | 입력 / 상태 데이터: 좌측 장애물 감지 결과를 센서에서 제어기로 전달한다. 근거: R3, R4. |
| Right Sensor Input | 입력 / 상태 데이터: 우측 장애물 감지 결과를 센서에서 제어기로 전달한다. 근거: R3, R4. |
| Dust Sensor Input | 입력 / 상태 데이터: 먼지 감지 결과를 센서에서 제어기로 전달한다. 근거: R5. |
| Direction | 출력 / 제어 명령: 이동 구동장치에 직진, 좌·우 회전 또는 후진 명령을 전달한다. 근거: R2, R3, R4. |
| Clean | 출력 / 제어 명령: 청소·물걸레 구동장치에 자동 청소·물걸레 수행에 필요한 제어 정보를 전달한다. 요구된 청소 동작에는 수행, 중지, 재개 및 일시적 출력 강화가 포함된다. 근거: R1, R2, R3, R5. |

입력의 감지 주기나 데이터 인코딩은 원문에 없으므로 정하지 않는다. R5의 “for a while”는 시간 조건을 요구하지만, 외부 타이머 입력이나 타이머 장치는 명시하지 않는다. 따라서 별도의 외부 시간 이벤트를 추가하지 않는다. R6과 R7은 분석 범위를 제한하며 별도의 입출력 이벤트를 만들지 않는다.

## 요구사항 미정 사항

- 좌회전과 우회전의 선택 기준 및 회전 완료 조건.
- 장애물 판단 기준과 각 센서 결과의 조합별 동작. 전방·좌측·우측이 모두 막힌 경우의 후진은 명시되어 있다.
- 후진 거리·시간, 후진 종료 조건 및 후방 장애물 처리.
- 먼지 감지 시 출력 강화 정도·지속시간·반복 감지 시 처리.
- 물걸레 구동 방식 및 장애물 회피·출력 강화 중 물걸레 동작.
- 자동 청소의 시작·종료 조건. 사용자 버튼, 배터리, 도킹 및 별도 상태 표시 인터페이스는 원문에 없어 추가하지 않았다.

이 항목들은 상세 동작을 정의하기 전에 확인이 필요하다. 현재 Context Diagram은 해당 값을 정하지 않고 요구된 입출력 경계만 표현한다.
