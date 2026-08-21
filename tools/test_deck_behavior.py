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


# --- 부록 (Task 8) ------------------------------------------------------------
#
# 부록의 판단 셋을 붙잡는다. 셋 다 지금은 주석으로만 지켜지고 있어서, 나중에
# 뒤집어도 아무 테스트가 울지 않는 자리였다.


def appendix_indexes(pg):
    """부록 슬라이드의 번호 목록. 없으면 skip."""
    got = pg.evaluate('Deck.slides.map((s, i) => [i, s.classList.contains("appendix")])'
                      '.filter(([, a]) => a).map(([i]) => i)')
    if not got:
        pytest.skip('부록 슬라이드가 아직 없다')
    return got


def test_a_jumps_to_the_first_appendix_slide(page):
    """s52 의 대본이 청중에게 "A 를 누르면 부록"이라고 예고한다.

    그 약속이 코드에 남아 있는지 확인한다. 번호가 아니라 class 로 찾는다 —
    본편이 한 장 늘어도 이 성질은 그대로여야 한다."""
    page.goto(DECK)
    first = appendix_indexes(page)[0]
    for probe in (0, first // 2, first - 1, first):
        goto(page, probe)
        page.keyboard.press('a')
        assert state(page)['i'] == first, '%d 번 장에서 A 가 부록 첫 장으로 안 갔다' % probe


def test_appendix_sequences_do_not_play_by_themselves(page):
    """부록의 시퀀스는 자동재생하지 않는다.

    s17·s51 이 자동재생하는 이유는 열여섯 단계의 '모양'을 정해진 시간 안에 보여
    주는 것이다. 부록은 반대 상황이다 — 질문이 나와서 여는 장이고, 발표자는 특정
    단계에 멈춰 서서 답해야 한다. 자동재생은 답하는 동안 화면을 혼자 굴린다.

    ON_ENTER 에 부록이 하나라도 들어가면 그 자리에서 실패한다. 그것만으로는
    '등록하지 않았다'까지밖에 말하지 못하므로, 실제로 벽시계로도 재 본다."""
    page.goto(DECK)
    ids = page.evaluate('Deck.slides.map(s => s.id)')
    leaked = [ids[i] for i in appendix_indexes(page)
              if page.evaluate('id => id in ON_ENTER', ids[i])]
    assert leaked == [], 'ON_ENTER 에 등록된 부록 장: %s — 자동재생이 걸린다' % leaked

    seq_slides = [i for i in appendix_indexes(page)
                  if page.evaluate('i => !!Deck.slides[i].querySelector(".seq-counter")', i)]
    if not seq_slides:
        pytest.skip('부록에 시퀀스가 아직 없다')
    for i in seq_slides:
        goto(page, i)
        read = 'i => Deck.slides[i].querySelector(".seq-counter").textContent.trim()'
        before = page.evaluate(read, i)
        page.wait_for_timeout(2000)          # 자동재생은 1700ms 간격으로 한 칸 넘긴다
        assert page.evaluate(read, i) == before, \
            '%s 의 시퀀스가 저절로 넘어갔다 (%s)' % (ids[i], before)
        # 손으로는 넘어가야 한다 — 멈춰 있는 것과 죽어 있는 것은 다르다
        page.keyboard.press('ArrowRight')
        assert page.evaluate(read, i) != before, '%s 의 시퀀스가 → 로도 안 넘어간다' % ids[i]
        assert state(page)['i'] == i, '→ 가 단계를 넘기지 않고 슬라이드를 넘겼다'


def test_appendix_quiz_bank_shows_exactly_one_question_per_beat(page):
    """퀴즈 은행은 한 비트에 문제 하나만 세운다.

    .build 로는 안 되는 일이다 — 쌓이는 공개라 마지막 비트에서 다섯 문제가 한꺼번에
    서고, 720px 을 넘길뿐더러 청중이 발표자보다 먼저 다음 문제를 읽는다. 그래서
    registerBeats 의 컨트롤러 자리에 갈아 끼우기를 넣었다. 이 테스트가 그것을 붙잡는다:
    숨김이 opacity 로 바뀌거나(자리를 계속 먹는다) 누적 공개로 돌아가면 실패한다."""
    page.goto(DECK)
    banks = [i for i in appendix_indexes(page)
             if page.evaluate('i => Deck.slides[i].querySelectorAll(".quiz").length > 1', i)]
    if not banks:
        pytest.skip('퀴즈가 둘 이상인 부록 장이 아직 없다')
    for i in banks:
        total = page.evaluate('i => Deck.slides[i].querySelectorAll(".quiz").length', i)
        n = page.evaluate('i => beatCount(Deck.slides[i])', i)
        assert n == total, '비트 %d 개 ≠ 문제 %d 개 — 손이 안 닿는 문제가 생긴다' % (n, total)
        goto(page, i)
        seen = []
        for beat in range(n):
            page.evaluate('b => { Deck.beat = b; applyBeat(Deck.slides[Deck.index], b); }', beat)
            shown = page.evaluate(
                'i => Array.from(Deck.slides[i].querySelectorAll(".quiz"))'
                '.filter(q => q.offsetParent !== null).map(q => q.dataset.qid)', i)
            assert len(shown) == 1, '비트 %d 에 보이는 문제가 %d 개다' % (beat, len(shown))
            seen.append(shown[0])
        assert len(set(seen)) == n, '비트마다 다른 문제가 나오지 않는다: %s' % seen


def test_the_time_meter_counts_only_the_slides_that_get_presented(page):
    """계측의 분모는 본편이다. 부록은 넘어가는 장이라 예정 시간에 들어가면 안 된다.

    이 덱에 시간 막대가 있는 이유는 타이밍을 리허설에서 발견하는 대신 숫자로 아는
    것이다. 부록까지 더한 분모는 52분에 정확히 끝낸 발표자에게 86%를 보여 준다.
    14% 어긋난 계기는 없는 것보다 나쁘다 — 믿고 보기 때문이다.

    tools/check_slides.py 의 check_total 과 같은 가름이고, 둘은 늘 같이 움직여야
    한다. 한쪽만 고치면 검사기는 52:00 이라고 하는데 무대의 막대는 다른 말을 한다."""
    page.goto(DECK)
    all_sec = page.evaluate('Deck.slides.reduce((a, s) => a + Deck.secOf(s.id), 0)')
    main_sec = page.evaluate(
        'Deck.slides.filter(s => !s.classList.contains("appendix"))'
        '.reduce((a, s) => a + Deck.secOf(s.id), 0)')
    assert page.evaluate('Deck.plannedTotal()') == pytest.approx(main_sec), \
        'plannedTotal 이 본편 합계와 다르다'
    if appendix_indexes(page):
        assert main_sec < all_sec, '픽스처에 부록이 있는데 두 합계가 같다'

    # 본편 마지막 장에서 '예정대로 끝냈을 때' 두 막대가 100%를 가리켜야 한다.
    last_main = page.evaluate(
        'Deck.slides.map((s, i) => [i, s.classList.contains("appendix")])'
        '.filter(([, a]) => !a).map(([i]) => i).pop()')
    page.evaluate('([i, t]) => { Deck.go(i); elapsed = t; t0 = null; paint(); }',
                  [last_main, main_sec])
    pos = page.eval_on_selector('#barPos', 'e => parseFloat(e.style.width)')
    tim = page.eval_on_selector('#barTime', 'e => parseFloat(e.style.width)')
    assert pos == pytest.approx(100, abs=0.5), '본편 마지막 장인데 위치 막대가 %.1f%%' % pos
    assert tim == pytest.approx(100, abs=0.5), '예정대로 끝냈는데 시간 막대가 %.1f%%' % tim


def test_form_controls_keep_the_keys_they_use(page):
    """<select> 에 포커스가 있을 때 ↓ 는 값을 바꾸지, 슬라이드를 넘기지 않는다.

    동시에 덱의 손잡이는 살아 있어야 한다. tagName 만 보고 통째로 return 하면
    select 를 한 번 클릭한 뒤로 O·P·A·Escape 가 전부 죽는다 — 원래 버그보다 나쁘다."""
    page.goto(DECK)
    sel = page.evaluate('Deck.slides.findIndex(s => s.querySelector("select"))')
    if sel < 0:
        pytest.skip('<select> 가 있는 슬라이드가 아직 없다')
    goto(page, sel)
    handle = page.eval_on_selector('.slide.on select', 'e => e.id')
    page.focus('#' + handle)
    # 덱이 이 키를 삼켰는지는 두 가지로 본다: 슬라이드가 안 넘어갔는가, 그리고
    # preventDefault 가 안 걸렸는가. 값이 실제로 바뀌는 것은 브라우저의 몫이고
    # headless 에서 합성 키로는 재현되지 않아 여기서 재지 않는다.
    page.evaluate('window.__pd = null;'
                  'addEventListener("keydown", e => { window.__pd = e.defaultPrevented; });')
    page.keyboard.press('ArrowDown')
    assert state(page)['i'] == sel, '<select> 에서 ↓ 를 눌렀는데 슬라이드가 넘어갔다'
    assert page.evaluate('window.__pd') is False, \
        '덱이 ↓ 에 preventDefault 를 걸어 <select> 가 값을 못 바꾼다'
    # 포커스가 select 에 남아 있어도 덱의 키는 살아 있다
    page.keyboard.press('o')
    assert on(page, '#overview') is True, 'select 에 포커스가 있으면 O 가 죽는다'
    page.keyboard.press('Escape')
    assert on(page, '#overview') is False, 'select 에 포커스가 있으면 Escape 가 죽는다'
    page.keyboard.press('ArrowRight')
    assert state(page)['i'] == sel + 1, 'select 에 포커스가 있으면 → 가 죽는다'


def test_overview_marks_appendix_cells_apart(page):
    """개요 그리드에서 부록이 본편과 구별된다. 예순일곱 칸이 한 덩어리로 이어지면
    어디까지가 오늘 발표인지 눈으로 잘리지 않는다."""
    page.goto(DECK)
    page.keyboard.press('o')
    marked = page.eval_on_selector_all('.ov-cell.app', 'els => els.length')
    assert marked == len(appendix_indexes(page))
    # 표시는 앞이 아니라 뒤에 몰려 있어야 한다 — 부록은 본편 뒤에 온다
    idx = page.eval_on_selector_all('.ov-cell.app', 'els => els.map(e => +e.dataset.i)')
    assert idx == appendix_indexes(page)


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
    ('.seq-msg.self .seq-pill',
     'self 단계(from===to)의 이름표(20px). .seq-cap 의 짝이고, 같은 말이 바로 아래 '
     '.seq-detail 의 .lbl(24px)에 제 크기로 다시 나온다'),
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
    # SVG 는 두 가지가 겹친 자리라 근거를 나눠 적는다.
    # (1) 단위: font-size 12.5 는 viewBox 좌표이지 화면 px 이 아니다. 화면 크기는
    #     상자 너비 ÷ viewBox 너비가 정하므로 computed 값을 24 와 비교할 수 없다.
    # (2) 그러면 실제로는 몇 px 인가 — 1280x720 에서 getScreenCTM 으로 197개를 재면
    #     12.7~23.3px, 중앙값 15.6px 이다. 하한 아래다. 그러니 "못 읽어도 되는 표지"
    #     라서 빼는 것이 아니다. s10 3프레임처럼 그 장의 요점 자체가 SVG 문자열
    #     ('이 선은 없다', 14.9px)인 자리가 실제로 있다.
    # 빼는 진짜 근거는 같은 말이 .dia-cap 에 26px 로 다시 실린다는 것이다. 뒷자리가
    # 잃는 것은 뜻이 아니라 그 뜻이 그림의 어디를 가리키는가이고, 그건 발표자가 짚는다.
    ('svg, svg *',
     'SVG 의 font-size 는 viewBox 좌표라 화면 px 이 아니다(실측 12.7~23.3px, 중앙 15.6). '
     '프레임의 문장은 .dia-cap 이 26px 로 다시 싣는다'),
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


def test_the_two_jwt_demos_stay_identical_apart_from_their_button_rows(page):
    """s44 와 s45 는 JWT 데모 마크업을 한 벌씩 따로 들고 있다.

    Task 6 이 중복 id(jwtRaw·jwtDecoded·jwtChecks)를 클래스로 바꾸면서 두 벌을
    합치지 않기로 했다 — 두 장은 버튼 줄과 제목이 실제로 다르고, 마크업을 JS 안으로
    옮기면 SLIDES 블록만 읽어서는 그 장에 무엇이 있는지 알 수 없게 되기 때문이다.
    그 판단이 성립하려면 '두 벌이 어긋나면 바로 안다'가 참이어야 한다. 지금은
    s44 의 이름표를 고치고 s45 를 안 고쳐도 아무것도 잡지 않는다. 이 테스트가 그 자리다.

    비교에서 빼는 것은 둘뿐이다:
      - .btn-row  두 장이 다른 버튼을 보여 주는 것이 이 데모의 설계다
      - 실행 중에 채워지는 세 곳(.jwt-raw · .jwt-decoded · .jwt-checks)의 내용
    나머지(구조·제목·이름표·배지)가 한 글자라도 벌어지면 실패한다.
    """
    page.goto(DECK)
    skeleton = """
    (id) => {
      const src = document.getElementById(id);
      if (!src) return null;
      const c = src.cloneNode(true);
      c.removeAttribute('id');
      c.querySelectorAll('.btn-row').forEach(e => e.remove());
      c.querySelectorAll('.jwt-raw, .jwt-decoded, .jwt-checks').forEach(e => e.textContent = '');
      return c.innerHTML.replace(/\\s+/g, ' ').trim();
    }
    """
    a = page.evaluate(skeleton, 'jwtDemo44')
    b = page.evaluate(skeleton, 'jwtDemo45')
    assert a is not None and b is not None, 'jwtDemo44/45 를 찾지 못했다'
    assert a == b, ('s44 와 s45 의 JWT 데모 마크업이 버튼 줄 말고도 벌어졌다.\n'
                    's44: %s\ns45: %s' % (a[:400], b[:400]))
