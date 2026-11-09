# Unit Test Cases

소스: [tests/controller_test.cpp](../../tests/controller_test.cpp). 요구사항은 [Event List](../SA/event_list.md)의 R1~R7을 따른다. 좌우 선택·틱 시간·우선순위의 상세 기대값은 사용자 확인을 받은 [P1](../SD/simulation_profile.md)에서 도출했다.

| ID | GoogleTest | 근거 | Expected | Actual |
|---|---|---|---|---|
| UT-01 | ControllerTest.R1_R2_ForwardCleansAndMops | R1, R2 | 직진 명령, 청소·물걸레 활성, 통상 출력 1, 첫 틱 1 | PASS |
| UT-02 | ControllerTest.R3_LeftPreferredAndCleaningStops | R3 | 전방 장애물에서 좌회전, 청소·물걸레 중지, 출력 0 | PASS |
| UT-03 | ControllerTest.R3_RightWhenLeftBlocked | R3 | 전방·좌측이 막히면 우회전 | PASS |
| UT-04 | ControllerTest.R3_LeftWhenRightBlocked | R3 | 전방·우측이 막히면 좌회전 | PASS |
| UT-05 | ControllerTest.R3_ResumesAfterTurn | R3 | 회전 다음 틱에 전방이 비면 직진 및 청소 재개 | PASS |
| UT-06 | ControllerTest.R4_BackThenTurnThenResume | R4 | 세 방향이 막히면 후진→회전→직진·청소 재개 | PASS |
| UT-07 | ControllerTest.R3_RechecksFrontAfterTurn | R3 | 회전 후 새 전방 장애물이 있으면 다시 회피하며 청소 중지 | PASS |
| UT-08 | ControllerTest.Profile_SideOnlyDoesNotInterruptForward | P1 / 전송·수명주기 검증 | 측면만 막힌 경우 전방 직진 유지 | PASS |
| UT-09 | ControllerTest.R5_ThreeActiveTicksThenNormal | R5 | 먼지 감지부터 청소 가능 3틱은 출력 2, 다음은 출력 1 | PASS |
| UT-10 | ControllerTest.R5_RepeatedDustRefreshesDuration | R5 | 강화 중 재감지 시 3틱으로 갱신 | PASS |
| UT-11 | ControllerTest.R3_R5_AvoidanceOverridesAndPausesBoost | R3, R5 | 회피 시 출력 0, 남은 강화 시간 보존, 재개 후 강화 | PASS |
| UT-12 | ControllerTest.R3_R5_DustDuringAvoidanceIsPending | R3, R5 | 회피 중 먼지를 pending으로 보존하고 재개 시 강화 | PASS |
| UT-13 | ControllerTest.R4_R5_PendingSurvivesBackwardAndTurn | R4, R5 | 후진·회전 동안 pending 유지, 직진 재개 때 강화 | PASS |
| UT-14 | ControllerTest.Profile_BackwardUsesCurrentOpenRight | P1 / 전송·수명주기 검증 | 후진 후 좌측이 막히고 우측이 비면 우회전 | PASS |
| UT-15 | ControllerTest.R4_RepeatedEnclosureRemainsStopped | R4 | 후진·회전 후에도 세 방향이 막히면 다시 후진, 청소 중지 유지 | PASS |
| UT-16 | ControllerTest.Profile_StateTickCountsAndIndependentContexts | P1 / 전송·수명주기 검증 | 상태 연속 횟수 증가, 독립 컨텍스트의 틱·상태 초기화 | PASS |
| UT-17 | Conditions.R3_R4_AllSensorCombinationsPreserveValues | R3, R4 | 16개 센서 조합을 보존하고 전방·좌측·우측 AND로 all_blocked 계산 | PASS |
| UT-18 | Pipeline.R1_R5_ActualOutputAndReset | R1, R5 | 통합 파이프라인의 강화·회전 JSON, 새 실행 시 틱 1로 초기화 | PASS |
| UT-19 | Pipeline.InvalidInputIsRejectedWithoutCommand | P1 / 전송·수명주기 검증 | 잘못된 센서 값·토큰은 명령 없이 오류, 빈 입력은 정상 EOF | PASS |
| UT-20 | Pipeline.NullPortsAndNullSnapshot | P1 / 전송·수명주기 검증 | null 포트/스냅샷과 잘못된 모터 값의 방어 처리 | PASS |
| UT-21 | Pipeline.FinalLineValidationDistinguishesMalformedInputFromEof | P1 / 전송·수명주기 검증 | 줄바꿈 없는 잘못된 입력은 오류, 올바른 마지막 행은 정상 처리 | PASS |
| UT-22 | Pipeline.LongRecordIsRejectedAndAllBooleanEncodingsArePreserved | P1 / 전송·수명주기 검증 | 긴 레코드·범위 밖 값 거부, 후진·우회전·센서 true/false 직렬화 보존 | PASS |

R6은 HW 상세 구현 제외, R7은 자동 청소 범위라는 비기능 범위 제약으로 [모듈 추적성](module_traceability.md)과 [P1](../SD/simulation_profile.md)에서 검토했다. 이 두 제약을 물리 장치 테스트로 검증했다고 주장하지 않는다.
