# RVC Controller & Simulator

SASD로 작성한 SA·SD를 바탕으로 구현한 C11 제어기와 로컬 웹 시뮬레이터이다. UI에서 지도를 편집하고 실제 C 제어기를 한 틱씩 실행한다. 제어 로직을 JavaScript로 재구현하지 않았다.

## 실행

현재 워크스페이스에는 GCC로 빌드한 `build/rvc_cli.exe`와 로컬 개발 도구가 준비되어 있다.

```powershell
python simulator/server.py
```

[http://127.0.0.1:8765](http://127.0.0.1:8765)를 브라우저에서 연다. 포트가 이미 사용 중이면 `python simulator/server.py --port 8766`으로 다른 포트를 사용한다. 서버 종료는 실행 터미널에서 Ctrl+C이다. 프런트엔드는 외부 CDN이나 npm 설치 없이 동작한다.

자동 빌드가 필요한 경우 다음 스크립트를 사용할 수 있다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_simulator.ps1
```

## 새 환경에서 빌드

Windows의 Python 3.11 이상과 GCC/G++/mingw32-make/gcov가 PATH에 있어야 한다. 이 워크스페이스에서는 MSYS2 UCRT64의 GCC 14.2.0을 사용했다. 네트워크가 필요한 최초 의존성 설치는 프로젝트 `.tools/` 안에서만 수행한다.

```powershell
python scripts/bootstrap.py
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

CMake 4.4.4와 GoogleTest 1.15.2를 사용한다. 프로덕션 코드는 C11, GoogleTest 코드는 C++17이며 CTest로 실행한다.

## 사용 방법

1. 시나리오 20개 중 하나를 선택한다. 또는 장애물·먼지·시작점 도구로 지도를 편집하고 초기 방향을 선택한다. 시작점은 기본 (4,4), 북쪽이다.
2. **시작**으로 자동 실행하거나 **한 틱**으로 수동 실행한다. 최대 100틱에서 정지한다. 재생 속도를 바꿀 수 있다.
3. **이전 틱**, 슬라이더 또는 기록 행으로 과거 상태를 본다. 과거 조회는 C 상태를 역실행하지 않는다. 과거에서 재생하면 저장된 기록을 따라간 뒤 새 틱을 실행한다.
4. **재설정**은 초기 지도와 제어 상태를 복원하고, **다시 실행**은 복원 후 자동 실행한다. 지도 편집도 새 실행으로 전환한다.
5. **전체 상태**에서 입력 센서, 이전/현재 상태, 모터·청소·물걸레 출력, 타이머, pending/강화 플래그, 선택 회전 및 환경 변화를 확인한다.
6. 사용자 지도는 **새 시나리오 저장** 또는 JSON 내보내기로 보존한다. 지도 JSON과 내보낸 trace의 config를 다시 불러올 수 있다.
7. 기대 동작을 검토한 사람이 PASS/FAIL/INCONCLUSIVE, 평가자, 관련 틱, 관찰 내용을 기록한다. 프로그램은 시스템 시나리오의 판정을 자동 지정하지 않는다.

사용자 지도와 평가 기록은 `simulator/saved/`에 저장된다. 전체 trace도 JSON으로 다운로드할 수 있다. 화면의 틱 0은 아직 첫 C 업데이트 전이므로 센서·제어기 값은 미관측으로 표시한다.

## 검증 재실행

```powershell
python tests/test_simulator.py
python scripts/run_system_tests.py
python scripts/check_traceability.py
python scripts/coverage.py
```

브라우저 검증은 선택적 개발 도구가 필요하다. 서버를 별도 터미널에서 8766 포트로 실행한 뒤 다음을 실행한다.

```powershell
python scripts/bootstrap.py --browser
python tests/browser_smoke.py
```

브라우저 테스트는 사전 시나리오 20개가 있는 깨끗한 저장소 상태를 전제로 한다. 합성 사용자 지도와 INCONCLUSIVE 저장 테스트를 수행한 뒤 자신이 만든 데이터만 제거한다. 실제 평가를 자동 수행하지 않는다.

## 산출물

| 단계 | 문서 |
|---|---|
| SA | [문서 목록](artifacts/SA/README.md) |
| SD | [Transform Analysis](artifacts/SD/transform_analysis.md), [Structure Chart](artifacts/SD/structure_chart.md) |
| 동작 상세 기준 | [사용자가 승인한 P1 프로파일](artifacts/SD/simulation_profile.md) |
| 구현·TDD | [테스트 결과](artifacts/Implementation/test_report.md), [테스트 케이스](artifacts/Implementation/unit_test_cases.md), [커버리지](artifacts/Implementation/coverage_report.md), [모듈 추적성](artifacts/Implementation/module_traceability.md) |
| 시스템 테스트 | [시뮬레이터 명세](artifacts/SystemTest/simulator_specification.md), [20개 시나리오](artifacts/SystemTest/test_scenarios.md), [실행 결과](artifacts/SystemTest/test_results.md), [요구사항 추적성](artifacts/SystemTest/requirement_traceability.md) |
| 화면 확인 | [데스크톱](artifacts/SystemTest/browser/desktop.png), [모바일](artifacts/SystemTest/browser/mobile.png) |

## 모델의 범위

[원본 요구사항](docs/preliminary_requirement.md)에 없는 시간·거리·좌우 선택 정책은 사용자 확인을 받은 P1으로 구체화했다. 한 틱은 1칸 이동 또는 90도 회전이며, 먼지 감지 시 청소 가능 3틱 동안 출력이 강화된다. 회피 시 청소·물걸레를 중지하고 강화 타이머를 일시정지한다.

Python은 지도에서 센서를 구하고 C 명령에 따른 환경 효과만 적용한다. 매 틱 누적 센서 입력을 C CLI에 재생하는 방식이라 세션 상태가 분리되며, 최대 100틱 범위에서 결정적으로 동작한다. 가속된 재생 속도는 목표 간격이며 네이티브 프로세스 실행 시간의 영향을 받는다.

HW 제어·후방 센서·도킹·배터리·전체 면적 커버리지 보장은 포함하지 않는다. 후진 목적지가 막히면 환경이 이동을 차단하고 trace에 남긴다. 실제 장치 안전성이나 물리 성능을 검증한 시뮬레이터는 아니다.