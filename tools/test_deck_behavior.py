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
    n = page.evaluate('i => beatCount(Deck.slides[i])', i)
    for beat in range(n):
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


def test_down_arrow_at_the_last_slide_does_not_move(page):
    page.goto(DECK)
    n = state(page)['n']
    page.evaluate('n => Deck.go(n - 1)', n)
    page.keyboard.press('ArrowDown')
    assert state(page)['i'] == n - 1


def test_up_arrow_at_the_first_slide_does_not_move(page):
    page.goto(DECK)
    page.keyboard.press('ArrowUp')
    assert at(page) == (0, 0)


def on(pg, sel):
    return pg.eval_on_selector(sel, 'e => e.classList.contains("on")')


def test_s_toggles_the_notes_drawer(page):
    page.goto(DECK)
    assert on(page, '#notes') is False
    page.keyboard.press('s')
    assert on(page, '#notes') is True
    assert page.inner_text('#notes').strip() != '', '노트 서랍이 비어 있다'
    page.keyboard.press('s')
    assert on(page, '#notes') is False


def test_open_notes_drawer_follows_the_current_slide(page):
    page.goto(DECK)
    page.keyboard.press('s')
    first = page.inner_text('#notes')
    page.keyboard.press('ArrowDown')
    assert page.inner_text('#notes') != first, '슬라이드를 넘겼는데 노트가 그대로다'


def test_o_opens_one_overview_cell_per_slide(page):
    page.goto(DECK)
    page.keyboard.press('o')
    assert on(page, '#overview') is True
    assert page.eval_on_selector_all('.ov-cell', 'els => els.length') == state(page)['n']


def test_overview_cell_click_jumps_to_that_slide(page):
    page.goto(DECK)
    page.keyboard.press('o')
    page.click('.ov-cell[data-i="2"]')
    assert state(page)['i'] == 2
    assert on(page, '#overview') is False


def test_escape_closes_overview_and_notes(page):
    page.goto(DECK)
    page.keyboard.press('o')
    page.keyboard.press('s')
    page.keyboard.press('Escape')
    assert on(page, '#overview') is False
    assert on(page, '#notes') is False


def test_number_then_enter_jumps_to_that_slide(page):
    page.goto(DECK)
    page.keyboard.press('3')
    page.keyboard.press('Enter')
    assert state(page)['i'] == 2, '화면 번호는 1-기반, 인덱스는 0-기반이다'


def test_out_of_range_number_does_not_move(page):
    page.goto(DECK)
    page.keyboard.press('9')
    page.keyboard.press('9')
    page.keyboard.press('9')
    page.keyboard.press('Enter')
    assert state(page)['i'] == 0


def test_escape_discards_a_partially_typed_number(page):
    page.goto(DECK)
    page.keyboard.press('3')
    page.keyboard.press('Escape')
    page.keyboard.press('Enter')
    assert state(page)['i'] == 0


def test_presenter_window_mirrors_the_current_slide(page):
    """발표자 창(P)이 부모의 DOM 을 직접 갱신하는 설계라서, 그 경로가 실제로
    file:// 팝업에서 동작하는지가 이 테스트의 핵심이다 — localStorage 나
    BroadcastChannel 을 안 쓰기 때문에 이것 말고는 검증할 수단이 없다.

    슬라이드 내용에는 기대지 않는다: 특정 제목 문자열이 아니라 titleOf() 가
    돌려주는 값과 발표자 창의 #now 가 같다는 '관계'만 확인한다.
    """
    page.goto(DECK)
    with page.context.expect_page() as pop_info:
        page.keyboard.press('p')
    pres = pop_info.value
    try:
        pres.wait_for_load_state()
        before = page.evaluate('titleOf(Deck.slides[Deck.index])')
        assert pres.inner_text('#now') == before, \
            '발표자 창의 "지금"이 현재 슬라이드 제목과 다르다'

        page.keyboard.press('ArrowDown')
        pres.wait_for_function(
            'prev => document.getElementById("now").textContent !== prev',
            arg=before,
        )
        after = page.evaluate('titleOf(Deck.slides[Deck.index])')
        assert pres.inner_text('#now') == after, \
            '슬라이드를 넘겼는데 발표자 창이 따라가지 않는다'
    finally:
        pres.close()
