# Implementation and TDD Test Report

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

- 행: 96/96 = 100.00%.
- 분기 결과: 99/102 = 97.06%.
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
