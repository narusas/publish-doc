"""덱의 키보드 동작 테스트. Playwright 브라우저가 없으면 통째로 skip 한다.

  python3 -m playwright install chromium   # 한 번만

이 테스트는 슬라이드 '내용'에 기대지 않는다. Task 6·8 을 거치며 덱이 3장에서
67장이 되어도 엔진의 불변식은 그대로여야 하기 때문이다. 특정 슬라이드를
가리키는 대신, 필요한 성질(비트가 둘 이상인 슬라이드 등)을 그때그때 찾아 쓴다.
"""
import os

import pytest

playwright_api = pytest.importorskip('playwright.sync_api')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = 'file://' + os.path.join(ROOT, 'oauth2_slides.html')


@pytest.fixture(scope='module')
def page():
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:                     # 브라우저 바이너리 없음
            pytest.skip('chromium 없음: %s' % exc)
        pg = browser.new_page(viewport={'width': 1440, 'height': 900})
        yield pg
        browser.close()


def state(pg):
    return pg.evaluate('({i: Deck.index, b: Deck.beat, n: Deck.slides.length})')


def at(pg):
    s = state(pg)
    return (s['i'], s['b'])


def goto(pg, i):
    pg.evaluate('i => Deck.go(i)', i)


def first_multi_beat_slide(pg):
    """비트가 둘 이상인 첫 슬라이드의 (번호, 비트 수). 없으면 skip."""
    got = pg.evaluate(
        'Deck.slides.map((s, i) => [i, beatCount(s)]).find(([, n]) => n > 1) || null')
    if not got:
        pytest.skip('비트가 둘 이상인 슬라이드가 아직 없다')
    return got[0], got[1]


def test_starts_on_first_slide_at_beat_zero(page):
    page.goto(DECK)
    assert at(page) == (0, 0)


def test_right_arrow_consumes_every_beat_before_leaving_the_slide(page):
    page.goto(DECK)
    i, n = first_multi_beat_slide(page)
    goto(page, i)
    for expected in range(1, n):
        page.keyboard.press('ArrowRight')
        assert at(page) == (i, expected), '비트를 다 쓰기 전에 슬라이드를 넘겼다'
    page.keyboard.press('ArrowRight')
    assert at(page) == (i + 1, 0), '비트를 다 썼는데 슬라이드를 안 넘겼다'


def test_down_arrow_skips_the_whole_slide_ignoring_beats(page):
    page.goto(DECK)
    i, _ = first_multi_beat_slide(page)
    goto(page, i)
    page.keyboard.press('ArrowDown')
    assert at(page) == (i + 1, 0)


def test_left_arrow_enters_previous_slide_at_its_last_beat(page):
    page.goto(DECK)
    i, n = first_multi_beat_slide(page)
    goto(page, i + 1)
    page.keyboard.press('ArrowLeft')
    assert at(page) == (i, n - 1)


def test_builds_are_visible_exactly_up_to_the_current_beat(page):
    page.goto(DECK)
    i = page.evaluate(
        'Deck.slides.findIndex(s => s.querySelectorAll(".build").length >= 2)')
    if i < 0:
        pytest.skip('.build 가 둘 이상인 슬라이드가 아직 없다')
    goto(page, i)
    for beat in range(3):
        pairs = page.evaluate(
            'i => Array.from(Deck.slides[i].querySelectorAll(".build"))'
            '.map(e => [(+e.dataset.beat || 0), e.classList.contains("vis")])', i)
        for want, shown in pairs:
            assert shown == (want <= beat), \
                '비트 %d 에서 data-beat=%d 의 표시가 틀렸다' % (beat, want)
        page.keyboard.press('ArrowRight')


def test_cannot_advance_past_the_last_slide(page):
    page.goto(DECK)
    n = state(page)['n']
    page.evaluate('n => Deck.go(n - 1)', n)
    for _ in range(6):
        page.keyboard.press('ArrowRight')
    assert state(page)['i'] == n - 1


def test_cannot_go_before_the_first_slide(page):
    page.goto(DECK)
    for _ in range(6):
        page.keyboard.press('ArrowLeft')
    assert at(page) == (0, 0)
