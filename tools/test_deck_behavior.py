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


# --- 글자 크기 하한 (Task 6) --------------------------------------------------
#
# check_slides.py 의 check_font_floor 는 인라인 style 만 본다. Task 5 리뷰가 잰
# 하한 미달 180개는 인라인이 하나도 없었다 — 전부 CSS 규칙이었다. 상속·구체성·
# :has() 까지 풀어야 진짜 크기가 나오므로, 그건 정규식이 아니라 브라우저만 답할 수
# 있다. 그래서 실제 강제는 여기서 한다.

FONT_FLOOR = 24        # px, 1280 좌표계 본문 하한
FONT_FLOOR_MONO = 20   # px, 코드 하한

# 예외 목록. 각 줄의 근거는 oauth2_slides.html 의 DECK:STAGE:CSS 「활자 하한」
# 주석과 짝을 이룬다 — 한쪽만 고치면 이 테스트가 잡는다.
EXEMPT = [
    ('.seq-cap',
     '시퀀스 행 이름표(20px). 지도의 범례이고, 같은 말이 바로 아래 .seq-detail 의 '
     '.lbl(24px)에 제 크기로 다시 나온다'),
    ('.seq-legend, .seq-legend *',
     '채널 색 범례(15px). "노란 파선이 프론트채널입니다"라고 발표자가 말한다'),
    ('.dia-tag',
     '그림 왼쪽 위 꼬리표(11px). 바로 옆 <h2> 가 같은 말을 44px 로 한다'),
    ('.badge',
     '"실제 HMAC-SHA256 서명/검증" 같은 부가 표지(16px). 내용이 아니라 표지다'),
    ('.jwt-parts, .jwt-parts *',
     '토큰 세 토막의 이름표(15px). 바로 위 .jwt-raw 의 세 가지 색이 같은 말을 한다'),
    ('.seq-title', '시퀀스 제목 줄(18px). 그 장의 <h2> 가 같은 말을 크게 한다'),
    ('.seq-counter', '"3 / 16" 계기판(18px). 발표자용이다'),
    ('.step-n', '단계 번호(16px). 바로 옆 .lbl 이 단계 이름을 24px 로 말한다'),
    ('.seq-controls button', '◀ 이전 · 다음 ▶ 이송 버튼(18-20px). 발표자의 손잡이다'),
    # SVG 는 크기의 단위 자체가 다르다. font-size 12.5px 는 viewBox 좌표이고,
    # 화면에 몇 px 로 나오는지는 상자 너비 ÷ viewBox 너비가 정한다 — 같은 값이
    # 슬라이드마다 달라진다. 그림이 나르는 '문장'은 SVG 안이 아니라 .dia-cap(26px)에
    # 있고, 그쪽은 이 테스트가 그대로 잰다.
    ('svg, svg *', 'SVG 텍스트의 font-size 는 viewBox 좌표라 화면 px 이 아니다'),
]

MEASURE_FONTS = """
(exempt) => {
  const bad = [];
  document.querySelectorAll('.slide').forEach(slide => {
    slide.querySelectorAll('*').forEach(el => {
      if (!el.getClientRects().length) return;          // 그려지지 않는 것은 읽히지도 않는다
      if (exempt.some(sel => el.matches(sel))) return;
      const own = Array.from(el.childNodes)
        .filter(n => n.nodeType === 3 && n.textContent.trim())
        .map(n => n.textContent.trim()).join(' ');
      if (!own) return;                                 // 자식만 있는 상자는 글자를 안 나른다
      const cs = getComputedStyle(el);
      const px = parseFloat(cs.fontSize);
      const mono = /mono|Menlo|Consolas|Courier/i.test(cs.fontFamily);
      const floor = mono ? %d : %d;
      if (px + 0.01 < floor) {
        bad.push(slide.id + ' ' + el.tagName.toLowerCase() +
                 (el.className ? '.' + String(el.className).trim().split(/\\s+/).join('.') : '') +
                 '  ' + px + 'px < ' + floor + '  | ' + own.slice(0, 40));
      }
    });
  });
  return bad;
}
""" % (FONT_FLOOR_MONO, FONT_FLOOR)


def test_every_visible_text_is_at_or_above_the_font_floor(page):
    """슬라이드 전체를 돌며 실제 computed font-size 를 재고 하한과 대조한다.

    특정 슬라이드를 가리키지 않는다 — 문서에 있는 .slide 를 전부 훑으므로 장이
    늘어도 그대로 돈다. 예외는 EXEMPT 에 적힌 것뿐이고, 목록에 없는 것이 하한
    아래로 내려가면 그 자리에서 실패한다."""
    page.goto(DECK)
    n = page.evaluate('Deck.slides.length')
    # 도착해야 만들어지는 자산(s45 의 JWT 데모, 시퀀스)이 있어서 한 바퀴 깨워 둔다.
    for i in range(n):
        page.evaluate('i => Deck.go(i)', i)
    page.evaluate('Deck.go(0)')
    # 퀴즈 해설은 눌러야 열린다. 최악의 상태로 재려고 미리 펼친다.
    page.evaluate("document.querySelectorAll('.slide .explain')"
                  ".forEach(e => e.classList.add('show'))")
    bad = page.evaluate(MEASURE_FONTS, [sel for sel, _ in EXEMPT])
    assert bad == [], '하한 미만 %d개:\n  %s' % (len(bad), '\n  '.join(bad[:20]))


def test_no_slide_overflows_the_720px_stage(page):
    """어느 비트에서도 슬라이드 내용이 무대(0..720) 밖으로 나가지 않는다.

    스크롤 상자(.demo · .win-body · .seq-rows · .jwt-checks …) 안의 내용은 그 상자가
    가두므로 상자까지만 잰다. 넘치는 장은 줄일 것이 아니라 쪼갤 장이라는 신호다."""
    page.goto(DECK)
    n = page.evaluate('Deck.slides.length')
    page.evaluate("document.querySelectorAll('.slide .explain')"
                  ".forEach(e => e.classList.add('show'))")
    box_js = """
    () => {
      const slide = Deck.slides[Deck.index];
      const st = document.getElementById('stage').getBoundingClientRect();
      // #stage 는 fitStage() 가 뷰포트에 맞춰 scale() 한다. 재는 값은 무대 좌표계
      // (1280x720)로 되돌려야 720 이라는 숫자와 비교할 수 있다.
      const k = st.width / 1280;
      const inScroller = el => {
        for (let e = el.parentElement; e && e !== slide; e = e.parentElement) {
          const o = getComputedStyle(e);
          if (/(auto|scroll|hidden)/.test(o.overflowY + ' ' + o.overflowX)) return true;
        }
        return false;
      };
      let top = Infinity, bottom = -Infinity;
      slide.querySelectorAll('*').forEach(el => {
        if (el.closest('svg') || inScroller(el)) return;
        const r = el.getBoundingClientRect();
        if (!r.width && !r.height) return;
        top = Math.min(top, (r.top - st.top) / k);
        bottom = Math.max(bottom, (r.bottom - st.top) / k);
      });
      return [slide.id, top, bottom];
    }
    """
    over = []
    for i in range(n):
        page.evaluate('i => Deck.go(i)', i)
        beats = page.evaluate('i => beatCount(Deck.slides[i])', i)
        for b in range(beats):
            page.evaluate('b => { Deck.beat = b; applyBeat(Deck.slides[Deck.index], b); }', b)
            sid, top, bottom = page.evaluate(box_js)
            if top < 0 or bottom > 720:
                over.append('%s 비트%d: top=%.1f bottom=%.1f' % (sid, b, top, bottom))
    assert over == [], '무대 밖으로 나간 장 %d건:\n  %s' % (len(over), '\n  '.join(over[:10]))
