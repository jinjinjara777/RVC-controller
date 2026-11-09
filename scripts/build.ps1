$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $cmakePath = Join-Path $projectRoot '.tools/python/cmake/data/bin/cmake.exe'
    if (-not (Test-Path -LiteralPath $cmakePath)) { throw '먼저 python scripts/bootstrap.py를 실행하세요.' }
    & $cmakePath -S . -B build -G 'MinGW Makefiles' -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++
    if ($LASTEXITCODE -ne 0) { throw 'CMake 설정 실패' }
    & $cmakePath --build build -j 4
    if ($LASTEXITCODE -ne 0) { throw '빌드 실패' }
    $ctestPath = Join-Path (Split-Path $cmakePath) 'ctest.exe'
    & $ctestPath --test-dir build --output-on-failure
    if ($LASTEXITCODE -ne 0) { throw '단위 테스트 실패' }
} finally { Pop-Location }
