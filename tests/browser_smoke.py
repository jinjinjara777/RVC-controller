"""Browser checks on the real local server and compiled controller."""
from pathlib import Path
import json
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'.tools/browsers')
from playwright.sync_api import sync_playwright, expect

OUT=ROOT/'artifacts/SystemTest/browser';OUT.mkdir(parents=True,exist_ok=True)
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1080},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8766',wait_until='networkidle')
    expect(page.locator('#grid .cell')).to_have_count(100)
    expect(page.locator('#scenario option')).to_have_count(20)
    expect(page.locator('#step')).to_be_enabled()
    checks.append('Initial 10x10 map, 20 scenarios, native engine connection')
    for tick in range(1,4):
        page.locator('#step').click();expect(page.locator('#history-label')).to_have_text(f'{tick} / {tick}')
    page.locator('#previous').click();expect(page.locator('#history-label')).to_have_text('2 / 3')
    page.locator('#history-slider').fill('0');page.locator('#history-slider').dispatch_event('input')
    expect(page.locator('#history-label')).to_have_text('0 / 3')
    page.locator('#step').click();expect(page.locator('#history-label')).to_have_text('1 / 3')
    page.locator('details').click();expect(page.locator('#state-json')).to_contain_text('boost_remaining')
    page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
    checks.append('Manual step, previous tick, slider, cached history, complete C state')
    page.locator('#reset').click();expect(page.locator('#history-label')).to_have_text('0 / 0')
    page.locator('[data-tool=obstacle]').click();page.locator('.cell[data-x="0"][data-y="0"]').click()
    expect(page.locator('.cell[data-x="0"][data-y="0"]')).to_have_class('cell wall')
    page.locator('[data-tool=start]').click();page.locator('.cell[data-x="0"][data-y="0"]').click()
    expect(page.locator('#message')).to_contain_text('장애물 위에는')
    page.locator('.cell[data-x="5"][data-y="5"]').click();expect(page.locator('#position')).to_have_text('5, 5')
    page.locator('#direction').select_option('1');expect(page.locator('#heading')).to_have_text('→ 동')
    page.locator('[data-tool=dust]').click();page.locator('.cell[data-x="1"][data-y="1"]').click()
    expect(page.locator('.cell[data-x="1"][data-y="1"]')).to_have_class('cell dust')
    checks.append('Obstacle/dust editing, start position, direction, invalid placement prevention')
    with page.expect_download() as download:
        page.locator('#export-map').click()
    download.value.save_as(str(OUT/'map.json'))
    exported=json.loads((OUT/'map.json').read_text(encoding='utf-8'))
    assert exported['start']==[5,5] and exported['direction']==1
    invalid=dict(exported,start=[0,0]);bad=OUT/'invalid-map.json';bad.write_text(json.dumps(invalid),encoding='utf-8')
    page.locator('#import-map').set_input_files(str(bad));expect(page.locator('#message')).to_contain_text('시작 위치에 장애물')
    expect(page.locator('#position')).to_have_text('5, 5')
    page.locator('#import-map').set_input_files(str(OUT/'map.json'))
    expect(page.locator('#message')).to_contain_text('준비되었습니다')
    page.locator('#map-name').fill('UI 검증용 사용자 지도')
    page.locator('#save-map').click();expect(page.locator('#scenario option')).to_have_count(21)
    custom_id=page.locator('#scenario').input_value();assert custom_id.startswith('CUSTOM-')
    page.locator('#step').click();expect(page.locator('#history-label')).to_have_text('1 / 1')
    page.locator('#result').select_option('INCONCLUSIVE')
    page.locator('#evaluator').fill('UI 기능 검증')
    page.locator('#notes').fill('합성 사용자 지도에서 저장 기능만 확인. 요구사항 시나리오 판정이 아님.')
    page.locator('#eval-ticks').fill('1')
    page.locator('#save-evaluation').click();expect(page.locator('#evaluation-status')).to_have_text('INCONCLUSIVE')
    with page.expect_download() as download:
        page.locator('#export-trace').click()
    download.value.save_as(str(OUT/'trace.json'))
    trace=json.loads((OUT/'trace.json').read_text(encoding='utf-8'))
    assert len(trace['history'])==2 and trace['evaluation']['result']=='INCONCLUSIVE'
    checks.append('Custom map save/import/export, rejection without map mutation, evaluation and trace persistence')
    page.locator('#limit').fill('3');page.locator('#limit').dispatch_event('change')
    expect(page.locator('#history-label')).to_have_text('0 / 0')
    page.locator('#speed').select_option('150');page.locator('#start').click()
    expect(page.locator('#history-label')).to_have_text('3 / 3',timeout=10000)
    expect(page.locator('#step')).to_be_disabled();expect(page.locator('#run-status')).to_have_text('틱 제한 도달')
    page.locator('#restart').click();expect(page.locator('#history-label')).to_have_text('3 / 3',timeout=10000)
    page.locator('#limit').fill('100');page.locator('#limit').dispatch_event('change')
    expect(page.locator('#history-label')).to_have_text('0 / 0')
    page.locator('#start').click();expect(page.locator('#pause')).to_be_enabled();page.locator('#pause').click()
    expect(page.locator('#step')).to_be_enabled()
    paused=page.locator('#history-label').inner_text();page.wait_for_timeout(450)
    assert page.locator('#history-label').inner_text()==paused
    checks.append('Auto playback, configurable speed, pause, reset/restart, stop at configured tick limit')
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    assert not errors, errors
    checks.append('390px mobile layout without page overflow and no JavaScript exceptions')
    # Remove only the synthetic map/evaluation created by this validation.
    saved=ROOT/'simulator/saved'
    (saved/f'map-{custom_id}.json').unlink()
    for path in saved.glob('result-*.json'):
        data=json.loads(path.read_text(encoding='utf-8'))
        if data.get('config',{}).get('id')==custom_id and data.get('evaluation',{}).get('evaluator')=='UI 기능 검증':
            path.unlink()
    browser.close()
(OUT/'checks.json').write_text(json.dumps({'checks':checks,'javascript_errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print('BROWSER CHECKS PASSED: '+str(len(checks))+' groups; desktop/mobile screenshots saved.')
