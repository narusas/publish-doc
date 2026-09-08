#!/usr/bin/env python3
"""도해가 실제로 움직이는지 브라우저에서 확인한다.

정적 검사(test_defensive_diagrams.py)는 도해가 거기 있다는 것까지만 본다. 단계가
실제로 넘어가는지, 움직임을 줄여 달라고 한 사용자에게 자동 재생이 걸리지 않는지는
여기에서만 확인된다. 브라우저가 없으면 건너뛰지 않고 실패한다 — 이 저장소의 기존
규칙이다 (tools/test_defensive_behavior.py 참고).

사용법: python3 -m pytest tools/test_defensive_diagram_behavior.py -v
"""
import os

import pytest

try:
    from playwright import sync_api as playwright_api
except ImportError as exc:                    # pragma: no cover - 설치 안 된 기계
    playwright_api = None
    IMPORT_ERROR = exc

NO_BROWSER = ('도해 동작 테스트는 브라우저를 요구한다 — %s.\n'
              '정적 검사만으로는 단계 전환과 자동 재생 억제를 확인할 수 없어 skip 하지 않는다.\n'
              '설치: python3 -m playwright install chromium')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = 'file://' + os.path.join(ROOT, 'defensive_programming.html')

DIAGRAMS = ['diaBlame', 'diaSilent', 'diaBoundary', 'diaShape', 'diaCommit',
            'diaLayers', 'diaPool', 'diaBudget', 'diaSpecGap', 'diaRadius']


@pytest.fixture(scope='module')
def browser():
    if playwright_api is None:
        pytest.fail(NO_BROWSER % IMPORT_ERROR)
    with playwright_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as exc:              # pragma: no cover - 브라우저 미설치
            pytest.fail(NO_BROWSER % exc)
        yield b
        b.close()


@pytest.fixture
def pg(browser):
    page = browser.new_page()
    page.goto(DOC)
    yield page
    page.close()


def test_every_diagram_is_wired(pg):
    """배선되지 않은 도해는 단계 점이 하나도 없다. wireDia 호출을 빠뜨리면 여기서 걸린다."""
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        assert n >= 4, f'{fid}: 단계 점이 {n}개다'


def test_clicking_a_dot_moves_to_that_step(pg):
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        for k in (0, n - 1):
            pg.locator(f'#{fid} .dia-dot').nth(k).click()
            assert pg.get_attribute(f'#{fid}', 'data-s') == str(k)
            on = pg.locator(f'#{fid} .dia-dot.on')
            assert on.count() == 1


def test_the_step_box_changes_with_the_step(pg):
    """단계 설명이 단계마다 갈리지 않으면 단계를 나눈 뜻이 없다."""
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        seen = set()
        for k in range(n):
            pg.locator(f'#{fid} .dia-dot').nth(k).click()
            seen.add(pg.inner_text(f'#{fid} .dia-cap').strip())
        assert len(seen) == n, f'{fid}: 단계 설명이 {len(seen)}가지뿐이다'


def test_only_the_elements_for_this_step_are_visible(pg):
    """data-at 이 지정한 단계에서만 .vis 가 붙는다."""
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        pg.locator(f'#{fid} .dia-dot').nth(0).click()
        wrong = pg.evaluate("""(fid) => {
          const fig = document.getElementById(fid);
          const i = +fig.dataset.s;
          const bad = [];
          fig.querySelectorAll('[data-at]').forEach(el => {
            const spec = el.dataset.at;
            const want = window.diaAt(spec, %d).has(i);
            if (el.classList.contains('vis') !== want) bad.push(spec);
          });
          return bad;
        }""" % n, fid)
        assert wrong == [], f'{fid}: {wrong} 의 표시가 단계와 어긋난다'


def test_the_play_button_toggles(pg):
    fid = DIAGRAMS[0]
    btn = pg.locator(f'#{fid} .dia-btn')
    before = btn.get_attribute('aria-pressed')
    btn.click()
    assert btn.get_attribute('aria-pressed') != before


def test_reduced_motion_does_not_autoplay(browser):
    """움직임을 줄여 달라고 한 사용자에게는 자동 재생을 걸지 않고 마지막 단계를 세워 둔다."""
    ctx = browser.new_context(reduced_motion='reduce')
    page = ctx.new_page()
    page.goto(DOC)
    for fid in DIAGRAMS:
        n = page.locator(f'#{fid} .dia-dot').count()
        assert page.get_attribute(f'#{fid}', 'data-s') == str(n - 1), f'{fid}: 마지막 단계가 아니다'
        assert 'paused' in (page.get_attribute(f'#{fid}', 'class') or ''), f'{fid}: 멈춰 있지 않다'
    ctx.close()


def test_the_radius_diagram_is_drawn_from_the_shared_array(pg):
    """반경 지도의 문구가 RADIUS 에서 나온다. 손으로 적으면 개요와 어긋날 수 있다."""
    n = pg.evaluate("window.RADIUS.length")
    assert pg.locator('#diaRadius .rband-hot').count() == n
    names = pg.evaluate("window.RADIUS.map(r => r.n)")
    text = pg.text_content('#diaRadius svg')  # SVG 요소에는 innerText 가 없다
    for nm in names:
        assert nm in text, f'반경 이름 "{nm}" 이 그림에 없다'


def test_dia_at_reads_all_three_notations(pg):
    assert pg.evaluate("[...window.diaAt('0,2', 5)]") == [0, 2]
    assert pg.evaluate("[...window.diaAt('1-3', 5)]") == [1, 2, 3]
    assert pg.evaluate("[...window.diaAt('2+', 5)]") == [2, 3, 4]


def test_no_diagram_overflows_a_narrow_screen(browser):
    """좁은 화면에서 넘치는 것은 그림 상자 안이어야 한다. 본문이 가로로 밀리면 안 된다.

    budget 도해의 3000ms 막대는 720 폭 viewBox 안에 1950px 로 일부러 그려 SVG 가
    잘라 내게 한 것이다 — 그 막대의 문구를 그림으로 증명하기 위한 설계다(마크업 주석
    참고). 그 잘림은 SVG 내부에서 끝나고 document 의 scrollWidth 에는 나타나지
    않으므로, 이 테스트는 그 rect 를 결함으로 다루지 않는다. 여기서 보는 것은 어디까지나
    문서 전체의 가로 폭이다."""
    ctx = browser.new_context(viewport={'width': 375, 'height': 800})
    page = ctx.new_page()
    page.goto(DOC)
    doc_w = page.evaluate("document.documentElement.scrollWidth")
    win_w = page.evaluate("window.innerWidth")
    assert doc_w <= win_w + 1, f'문서가 가로로 넘친다: {doc_w} > {win_w}'
    ctx.close()
