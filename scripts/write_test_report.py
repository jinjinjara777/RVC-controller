"""Create readable test evidence from executed GoogleTest XML and saved reports."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/Implementation'
xml=ET.parse(OUT/'unit_results.xml').getroot()
assert int(xml.attrib['tests'])==22 and int(xml.attrib['failures'])==0
expected={
'R1_R2_ForwardCleansAndMops':'직진 명령, 청소·물걸레 활성, 통상 출력 1, 첫 틱 1',
'R3_LeftPreferredAndCleaningStops':'전방 장애물에서 좌회전, 청소·물걸레 중지, 출력 0',
'R3_RightWhenLeftBlocked':'전방·좌측이 막히면 우회전',
'R3_LeftWhenRightBlocked':'전방·우측이 막히면 좌회전',
'R3_ResumesAfterTurn':'회전 다음 틱에 전방이 비면 직진 및 청소 재개',
'R4_BackThenTurnThenResume':'세 방향이 막히면 후진→회전→직진·청소 재개',
'R3_RechecksFrontAfterTurn':'회전 후 새 전방 장애물이 있으면 다시 회피하며 청소 중지',
'Profile_SideOnlyDoesNotInterruptForward':'측면만 막힌 경우 전방 직진 유지',
'R5_ThreeActiveTicksThenNormal':'먼지 감지부터 청소 가능 3틱은 출력 2, 다음은 출력 1',
'R5_RepeatedDustRefreshesDuration':'강화 중 재감지 시 3틱으로 갱신',
'R3_R5_AvoidanceOverridesAndPausesBoost':'회피 시 출력 0, 남은 강화 시간 보존, 재개 후 강화',
'R3_R5_DustDuringAvoidanceIsPending':'회피 중 먼지를 pending으로 보존하고 재개 시 강화',
'R4_R5_PendingSurvivesBackwardAndTurn':'후진·회전 동안 pending 유지, 직진 재개 때 강화',
'Profile_BackwardUsesCurrentOpenRight':'후진 후 좌측이 막히고 우측이 비면 우회전',
'R4_RepeatedEnclosureRemainsStopped':'후진·회전 후에도 세 방향이 막히면 다시 후진, 청소 중지 유지',
'Profile_StateTickCountsAndIndependentContexts':'상태 연속 횟수 증가, 독립 컨텍스트의 틱·상태 초기화',
'R3_R4_AllSensorCombinationsPreserveValues':'16개 센서 조합을 보존하고 전방·좌측·우측 AND로 all_blocked 계산',
'R1_R5_ActualOutputAndReset':'통합 파이프라인의 강화·회전 JSON, 새 실행 시 틱 1로 초기화',
'InvalidInputIsRejectedWithoutCommand':'잘못된 센서 값·토큰은 명령 없이 오류, 빈 입력은 정상 EOF',
'NullPortsAndNullSnapshot':'null 포트/스냅샷과 잘못된 모터 값의 방어 처리',
'FinalLineValidationDistinguishesMalformedInputFromEof':'줄바꿈 없는 잘못된 입력은 오류, 올바른 마지막 행은 정상 처리',
'LongRecordIsRejectedAndAllBooleanEncodingsArePreserved':'긴 레코드·범위 밖 값 거부, 후진·우회전·센서 true/false 직렬화 보존',
}
text='# Unit Test Cases\n\n소스: [tests/controller_test.cpp](../../tests/controller_test.cpp). 요구사항은 [Event List](../SA/event_list.md)의 R1~R7을 따른다. 좌우 선택·틱 시간·우선순위의 상세 기대값은 사용자 확인을 받은 [P1](../SD/simulation_profile.md)에서 도출했다.\n\n| ID | GoogleTest | 근거 | Expected | Actual |\n|---|---|---|---|---|\n'
for index,test in enumerate(xml.findall('.//testcase'),1):
    name=test.attrib['name'];assert name in expected
    refs=list(dict.fromkeys(__import__('re').findall(r'R[1-7]',name)))
    ref=', '.join(refs) if refs else 'P1 / 전송·수명주기 검증'
    text+=f'| UT-{index:02d} | {test.attrib["classname"]}.{name} | {ref} | {expected[name]} | PASS |\n'
text+='\nR6은 HW 상세 구현 제외, R7은 자동 청소 범위라는 비기능 범위 제약으로 [모듈 추적성](module_traceability.md)과 [P1](../SD/simulation_profile.md)에서 검토했다. 이 두 제약을 물리 장치 테스트로 검증했다고 주장하지 않는다.\n'
(OUT/'unit_test_cases.md').write_text(text,encoding='utf-8')
coverage=json.loads((OUT/'coverage/summary.json').read_text(encoding='utf-8'))['total']
text=f'''# Implementation and TDD Test Report

실행일: 2026-11-06 (Asia/Seoul). 최종 GoogleTest **22/22 통과**, 환경 모델 테스트 **8/8 통과**. 시스템 시나리오는 20개 × 100틱을 실행했으며 **사람 판정은 PENDING**이다.

## 빌드 환경

- GCC/G++/gcov 14.2.0, CMake 4.4.4, GoogleTest 1.15.2, CTest.
- 프로덕션 C11, 테스트 C++17. C 코드에는 -Wall -Wextra -Wpedantic -Werror를 적용했다.
- 생산 코드: src/main.c, src/rvc.c, src/fsm.c 및 include/rvc.h.

## 실행한 Red–Green–Refactor

| 단계 | 실제 결과 | 근거 |
|---|---|---|
| 초기 RED | FSM 스텁에서 20개 중 18개 실패. 청소·회피·강화 미구현을 검출 | [tdd_red.log](tdd_red.log) |
| GREEN | 같은 20개 테스트 모두 통과 | [tdd_green.log](tdd_green.log) |
| Refactor | 좌우 선택 보조 함수로 중복 제거 후 재검증 | [최종 CTest log](tdd_refactor.log) |
| 전송 경계 RED | 테스트 2개 추가 후 22개 중 줄바꿈 없는 잘못된 입력 처리 1개 실패 | [tdd_transport_red.log](tdd_transport_red.log) |
| 최종 GREEN | VALID/EOF/INVALID 구분 후 22개 모두 통과 | [GoogleTest XML](unit_results.xml), [CTest log](tdd_refactor.log) |

단위 케이스별 기대값과 근거는 [unit_test_cases.md](unit_test_cases.md)에 있다. 최종 테스트 결과를 XML에서 읽어 이 보고서를 생성했다.

## Coverage

- 행: {coverage['lines_hit']}/{coverage['lines']} = {100*coverage['lines_hit']/coverage['lines']:.2f}%.
- 분기 결과: {coverage['branches_hit']}/{coverage['branches']} = {100*coverage['branches_hit']/coverage['branches']:.2f}%.
- 범위: 제어 로직 src/fsm.c 및 src/rvc.c. src/main.c의 단순 stdin/stdout 진입점은 제외.
- 메모리 할당 실패와 파일 읽기 오류의 3개 분기 결과는 미실행이다. [상세 보고서](coverage_report.md)에 공개했다.

## 통합 검증

- [SD→C 추적성](module_traceability.md): 모듈 13개, 모듈 사이의 12개 호출 관계 일치.
- Python 환경 모델 테스트 8개: 잘못된 지도, 기본값, 센서·경계, 후진 차단, 초기화·독립성·결정성·틱 제한 확인.
- [시스템 실행](../SystemTest/test_results.md): 2,000틱, 2,020 snapshots. 최종 실행 파일로 저장 입력 20개를 재생하여 모든 C 출력과 일치함을 재확인.
- [브라우저 검사](../SystemTest/browser/checks.json): 지도 편집·시작 위치·방향·기록·내보내기·수동 평가 저장·자동 정지 및 모바일 레이아웃. JS 예외 없음.
- [데스크톱](../SystemTest/browser/desktop.png)·[모바일](../SystemTest/browser/mobile.png) 캡처를 직접 확인했다.

## 승인 및 제한

사용자의 시뮬레이터까지 완성하라는 진행 지시와 기본값 확인을 근거로 구현했다. 원래 SA·SD의 초안 기록을 승인 완료로 소급 변경하지 않았다. P1의 구체화 기준은 [simulation_profile.md](../SD/simulation_profile.md)에 있다.

자동 테스트 통과는 사람의 시스템 요구사항 판정을 대체하지 않는다. UI에서 PASS/FAIL/INCONCLUSIVE를 직접 기록할 수 있다. 실제 하드웨어 제어·성능·안전성, 전체 청소 면적 보장 및 배포는 범위 밖이다.
'''
(OUT/'test_report.md').write_text(text,encoding='utf-8')
print('Wrote reports from 22 successful GoogleTest XML records and measured coverage.')
