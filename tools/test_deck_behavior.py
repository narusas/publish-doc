"""덱의 키보드 동작 테스트. 브라우저가 없으면 skip 하지 않고 실패한다.

활자 하한(24/20)·720px 넘침·키보드 계약을 강제하는 곳이 여기뿐이라, 물러서면
그 계약들이 통째로 사라지면서 화면에는 초록불이 뜬다. 고치는 법은 한 줄이다:

  python3 -m playwright install chromium   # 한 번만

이 테스트는 슬라이드 '내용'에 기대지 않는다. Task 6·8 을 거치며 덱이 3장에서
67장이 되어도 엔진의 불변식은 그대로여야 하기 때문이다. 특정 슬라이드를
가리키는 대신, 필요한 성질(비트가 둘 이상인 슬라이드 등)을 그때그때 찾아 쓴다.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_slides as cs        # noqa: E402  (같은 tools/ 안의 표준 라이브러리 전용 모듈)

# 브라우저가 없으면 skip 이 아니라 실패다.
#
# 활자 하한(본문 24px · 코드 20px)을 실제로 강제하는 것은 이 파일뿐이다.
# check_slides.py 의 check_font_floor 는 인라인 style 만 보는데 이 덱에는 그런 값이
# 하나도 없어서 0개를 잡는다 — 그리고 CSS 규칙 쪽은 정규식으로 답이 안 나온다.
# ASSET:CSS 가 이식해 온 값(.seq-cap 11.5px, .dia .cap-l 9.5px …)을 DECK:STAGE:CSS 가
# .slide 접두사로 덮어쓰는 구조라, 규칙만 훑으면 실제로는 지켜지는 38개를 위반이라고
# 부른다. 구체성과 캐스케이드를 다시 구현하지 않는 한 그 길은 없다.
#
# 그래서 이 관문은 브라우저에만 있다. 예전처럼 임포트 단계에서 모듈을 통째로
# 건너뛰거나 브라우저가 없다고 물러서면, 그런 기계에서는 24/20 계약이 통째로
# 증발하면서 화면에는 초록불이 뜬다. 시끄럽게 실패하는 편이 낫다 — 고치는 법은 한 줄이다:
#
#     python3 -m playwright install chromium
#
# 모듈 자체는 playwright 없이도 임포트된다. 브라우저가 필요 없는 검사
# (test_the_font_floor_exemptions_match_their_css_comment)는 그 기계에서도 돌아야 한다.
try:
    from playwright import sync_api as playwright_api
except ImportError as exc:                           # pragma: no cover - 설치 안 된 기계
    playwright_api = None
    IMPORT_ERROR = exc

NO_BROWSER = ('덱 동작 테스트는 브라우저를 요구한다 — %s.\n'
              '활자 하한(24/20)·720px 넘침·키보드 계약을 강제하는 곳이 여기뿐이라 '
              'skip 하지 않는다.\n설치: python3 -m playwright install chromium')

# 이 덱이 반드시 갖고 있는 성질을 못 찾았을 때 쓰는 말.
#
# skip 이면 안 되는 이유가 이 물결 전체의 이유와 같다. 예를 들어 createSequence 에서
# leave(){ stop(); } 한 줄을 지우면 — I3 회귀의 자산 쪽 판박이다 — autoplaying_slide()
# 가 아무것도 못 찾아 두 테스트가 skip 되고, 같은 술어를 쓰는 Deck.go 의 selfRunning
# 도 함께 죽는다. 한 줄로 Important 두 개가 풀리는데 스위트는 초록이 된다.
# '아직 그런 슬라이드가 없다'는 덱이 3장이던 시절의 말이고, 지금은 67장짜리 완성품이다.
MUST_EXIST = ('%s — 이 덱에는 있어야 하는 성질이다. 못 찾았다면 덱이 아니라 그것을 '
              '만드는 코드가 깨진 것이므로 skip 하지 않는다.')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = 'file://' + os.path.join(ROOT, 'oauth2_slides.html')


@pytest.fixture(scope='module')
def page():
    if playwright_api is None:
        pytest.fail(NO_BROWSER % ('playwright 가 설치돼 있지 않다(%s)' % IMPORT_ERROR))
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:                     # 브라우저 바이너리 없음
            pytest.fail(NO_BROWSER % ('chromium 을 띄우지 못했다(%s)' % exc))
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
        pytest.fail(MUST_EXIST % '비트가 둘 이상인 슬라이드')
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
        pytest.fail(MUST_EXIST % '.build 가 둘 이상인 슬라이드')
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
    # ↓ 가 아니라 → 로 넘긴다. 서랍이 열려 있는 동안 ↓ 는 서랍을 굴리는 키다
    # (test_arrow_keys_scroll_the_open_notes_drawer_instead_of_the_deck).
    while state(page)['i'] == 0:
        page.keyboard.press('ArrowRight')
    assert page.inner_text('#notes') != first, '슬라이드를 넘겼는데 노트가 그대로다'


# --- 겹쳐 뜬 창이 굴리는 키를 갖는다 -------------------------------------------
#
# 노트 서랍과 개요 그리드는 둘 다 스크롤 상자이고 둘 다 무대보다 크다. onKey 가
# ↑↓·PageUp/Down 을 조건 없이 가져가던 동안, 발표자가 '읽으려고' 누른 키는 창을
# 굴리는 대신 창 뒤에서 슬라이드를 넘겼다. 화면에 아무 표시가 없으므로 창을 닫고
# 나서야 엉뚱한 장에 서 있는 것을 안다.


def overflowing_notes_slide(pg):
    """대본이 서랍(max-height:38%)을 넘치는 첫 슬라이드. 없으면 skip."""
    i = pg.evaluate("""() => {
      const n = document.getElementById('notes');
      const keep = Deck.index, wasOn = n.classList.contains('on');
      n.classList.add('on');
      let found = -1;
      for (let i = 0; i < Deck.slides.length; i++) {
        Deck.go(i); notesFor = null; renderNotes();
        if (n.scrollHeight - n.clientHeight > 1) { found = i; break; }
      }
      if (!wasOn) n.classList.remove('on');
      Deck.go(keep);
      return found;
    }""")
    if i < 0:
        pytest.fail(MUST_EXIST % '노트 서랍(273px)을 넘치는 대본')
    return i


def settled_scroll_top(pg, sel):
    """스크롤이 멈춘 뒤의 scrollTop.

    크롬은 키보드 스크롤을 애니메이션으로 굴린다. 누른 직후에 읽으면 아직 0 이라
    '굴러가지 않았다'와 구분이 안 된다. 값이 두 번 연속 같을 때까지 기다린다."""
    last = None
    for _ in range(25):
        pg.wait_for_timeout(120)
        now = pg.eval_on_selector(sel, 'e => e.scrollTop')
        if now == last:
            return now
        last = now
    return last


def test_arrow_keys_scroll_the_open_notes_drawer_instead_of_the_deck(page):
    """서랍이 열려 있으면 ↓·PageDown 은 대본을 굴린다. 슬라이드는 그대로다.

    서랍은 max-height:38% = 273px 이고, 대본이 그것을 넘치는 장이 예순일곱 중
    열여섯이다(s30 은 538px 이 필요하다). 굴릴 수 없는 서랍은 그 열여섯 장에서
    대본의 절반이 없는 것과 같다 — 그리고 읽으려고 누른 그 키가 덱을 두 장
    넘겨 버린다."""
    page.goto(DECK)
    i = overflowing_notes_slide(page)
    goto(page, i)
    page.keyboard.press('s')
    assert on(page, '#notes') is True
    assert page.eval_on_selector('#notes', 'e => e.scrollTop') == 0
    page.keyboard.press('ArrowDown')
    page.keyboard.press('PageDown')
    moved = settled_scroll_top(page, '#notes')
    assert state(page)['i'] == i, \
        '서랍이 열려 있는데 ↓·PageDown 이 슬라이드를 넘겼다 (%d → %d)' % (i, state(page)['i'])
    assert moved > 0, '서랍이 열려 있는데 ↓·PageDown 이 대본을 굴리지 않는다'
    page.keyboard.press('ArrowUp')
    assert settled_scroll_top(page, '#notes') < moved, '↑ 가 대본을 되돌리지 않는다'
    assert state(page)['i'] == i, '서랍이 열려 있는데 ↑ 가 슬라이드를 되돌렸다'


def test_open_notes_drawer_keeps_its_scroll_while_the_timer_runs(page):
    """타이머가 도는 동안에도 읽던 자리를 지킨다.

    paint() 는 타이머가 켜져 있으면 0.5초마다 불린다. 그때마다 서랍의 innerHTML 을
    다시 넣으면 scrollTop 이 0 으로 돌아간다 — 발표자는 타이머를 켜 놓고 발표하므로
    굴릴 수 있게 만들어 놓고도 0.5초마다 맨 위로 튕긴다."""
    page.goto(DECK)
    i = overflowing_notes_slide(page)
    goto(page, i)
    page.keyboard.press('s')
    page.keyboard.press('PageDown')
    moved = settled_scroll_top(page, '#notes')
    assert moved > 0
    page.keyboard.press('t')                      # 타이머 시작 → paint() 가 0.5초마다
    page.wait_for_timeout(1400)
    assert page.eval_on_selector('#notes', 'e => e.scrollTop') == moved, \
        '타이머가 도는 동안 서랍이 맨 위로 되돌아갔다'
    page.keyboard.press('t')


def test_arrow_keys_scroll_the_open_overview_instead_of_the_deck(page):
    """개요가 열려 있으면 ↓·End 는 그리드를 굴린다. 슬라이드는 그대로다."""
    page.goto(DECK)
    goto(page, 10)
    page.keyboard.press('o')
    assert on(page, '#overview') is True
    box = page.eval_on_selector(
        '#overview', 'e => [e.scrollHeight, e.clientHeight]')
    assert box[0] > box[1], '개요가 무대 안에 다 들어가 스크롤을 잴 수 없다'
    start = settled_scroll_top(page, '#overview')
    for _ in range(3):
        page.keyboard.press('ArrowDown')
    assert settled_scroll_top(page, '#overview') > start, \
        '개요가 열려 있는데 ↓ 가 그리드를 굴리지 않는다'
    assert state(page)['i'] == 10, \
        '개요가 열려 있는데 ↓ 가 창 뒤에서 슬라이드를 넘겼다'
    page.keyboard.press('End')
    assert settled_scroll_top(page, '#overview') > start
    assert state(page)['i'] == 10, '개요가 열려 있는데 End 가 슬라이드를 옮겼다'


def test_overview_brings_the_current_cell_into_view_when_it_opens(page):
    """어느 장에서 열어도 지금 서 있는 칸이 보인다.

    그리드는 720px 무대 안에서 1321px 이라 두 화면 가까이 된다. 스크롤을 0 에
    두고 열면 인덱스 40 부터는 현재 칸이 아예 화면 밖이다(index 40 → curTop 650,
    index 60 → 1098) — 예순일곱 장 중 스물일곱 장. 개요는 설계 10절이 '눈 검사'의
    도구로 지정한 자리이자 질의응답 때 부록으로 들어가는 문이라, 열었을 때 내가
    어디 있는지가 안 보이면 둘 다 못 한다."""
    page.goto(DECK)
    n = state(page)['n']
    bad = []
    for i in [0, n // 3, n // 2, 2 * n // 3, n - 1]:
        seen = page.evaluate("""(i) => {
          const ov = document.getElementById('overview');
          if (ov.classList.contains('on')) toggleOverview();
          Deck.go(i);
          toggleOverview();
          const c = ov.querySelector('.ov-cell.cur');
          if (!c) return {i, ok: false, why: '현재 칸 표시가 없다'};
          const cb = c.getBoundingClientRect(), ob = ov.getBoundingClientRect();
          const ok = cb.top >= ob.top - 0.5 && cb.bottom <= ob.bottom + 0.5;
          const out = {i, ok, why: 'cellTop=' + Math.round(cb.top - ob.top) +
                       ' viewH=' + Math.round(ob.height)};
          toggleOverview();
          return out;
        }""", i)
        if not seen['ok']:
            bad.append('index %d: %s' % (seen['i'], seen['why']))
    assert bad == [], '개요를 열었는데 현재 칸이 화면 밖이다:\n  %s' % '\n  '.join(bad)


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


def type_number(pg, n):
    for ch in str(n):
        pg.keyboard.press(ch)
    pg.keyboard.press('Enter')


def main_indexes(pg):
    return pg.evaluate('Deck.slides.map((s, i) => [i, s.classList.contains("appendix")])'
                       '.filter(([, a]) => !a).map(([i]) => i)')


def test_number_then_enter_jumps_to_that_slide(page):
    page.goto(DECK)
    type_number(page, 3)
    assert state(page)['i'] == main_indexes(page)[2], \
        '화면 번호는 1-기반, 인덱스는 0-기반이다'


def test_digit_jump_counts_main_slides_not_the_whole_file(page):
    """숫자 점프의 좌표계는 HUD·개요와 같은 '본편 1..53'이다.

    본편만 세는 계기(막대) 옆에서 숫자만 67 좌표계로 남으면, 발표자가 화면에서
    읽은 번호와 쳐야 하는 번호가 갈린다. 부록이 앞에 없는 이 덱에서는 두 좌표계가
    본편 구간에서 우연히 겹치므로, 겹치지 않는 자리 — 마지막 본편 장과 그 너머 —
    에서 확인한다."""
    page.goto(DECK)
    mains = main_indexes(page)
    n = len(mains)
    type_number(page, n)
    assert state(page)['i'] == mains[-1], \
        '%d 을 쳤는데 마지막 본편 장(%d)이 아니라 %d 번 장에 있다' % (
            n, mains[-1], state(page)['i'])
    # 본편 마지막을 넘는 번호는 부록으로 이어지지 않는다 — 부록은 A 와 개요로 간다
    here = state(page)['i']
    type_number(page, n + 1)
    assert state(page)['i'] == here, '본편 수를 넘는 번호가 부록으로 넘어갔다'
    type_number(page, state(page)['n'])
    assert state(page)['i'] == here, '전체 장 수를 쳤더니 움직였다 — 67 좌표계가 남아 있다'


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


def counter_head(pg):
    """HUD 숫자에서 비트 부분(· 3/7)을 뗀 앞부분."""
    return pg.inner_text('#counter').split('·')[0].strip()


def test_counter_measures_the_talk_not_the_file(page):
    """HUD 의 숫자는 막대와 같은 것을 잰다 — 오늘 발표하는 본편 53장.

    막대 둘이 53장을 재는 옆에서 숫자만 "31 / 67"이면, 그 둘을 한눈에 보는
    발표자는 자기가 실제보다 덜 왔다고 읽는다. 'N / M'은 좌표가 아니라 진행률로
    읽히는 관용구이기 때문이다. 재보정을 한 이유가 그 실패였고, 숫자를 그대로 두면
    같은 실패가 옆 칸으로 옮겨 갈 뿐이다."""
    page.goto(DECK)
    mains = main_indexes(page)
    apps = appendix_indexes(page)
    n_main, n_app = len(mains), len(apps)

    for k in (0, n_main // 2, n_main - 1):
        goto(page, mains[k])
        assert counter_head(page) == '%d / %d' % (k + 1, n_main), \
            '%d 번째 본편 장의 숫자가 "%s"' % (k + 1, counter_head(page))

    for k in (0, n_app // 2, n_app - 1):
        goto(page, apps[k])
        head = counter_head(page)
        assert head == '부록 %d / %d' % (k + 1, n_app), \
            '%d 번째 부록 장의 숫자가 "%s"' % (k + 1, head)
        assert '/ %d' % state(page)['n'] not in head, \
            '부록 숫자가 아직 전체 장 수를 분모로 쓴다'


def test_counter_keeps_the_beat_sub_counter(page):
    """비트 하위 숫자(· 3/7)는 좌표계와 무관하다 — 슬라이드 안의 단계 수다."""
    page.goto(DECK)
    i, n = first_multi_beat_slide(page)
    goto(page, i)
    assert page.inner_text('#counter').strip().endswith('· 1/%d' % n), \
        '비트가 %d 개인 장인데 하위 숫자가 없다: %s' % (n, page.inner_text('#counter'))


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

        # 발표자 창의 번호는 무대의 HUD 와 같은 좌표계다. 두 화면이 다른 번호를
        # 말하면 발표자가 발표 중에 어느 쪽을 믿을지를 정해야 한다. 본편에서만
        # 보면 두 좌표계가 겹쳐 통과하므로, 갈리는 자리인 부록에서도 본다.
        for probe in (main_indexes(page)[-1], appendix_indexes(page)[0]):
            goto(page, probe)
            assert pres.inner_text('#cnt').strip() == counter_head(page), \
                '%d 번 장에서 발표자 창의 번호(%s)가 HUD(%s)와 다르다' % (
                    probe, pres.inner_text('#cnt').strip(), counter_head(page))
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
        pytest.fail(MUST_EXIST % '부록 슬라이드')
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
        pytest.fail(MUST_EXIST % '부록의 시퀀스')
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


# --- ON_ENTER 생명주기 --------------------------------------------------------
#
# Deck.go 는 떠나는 장의 leave() 와 들어오는 장의 enter() 를 부른다. 두 짝이 다
# 필요하다. leave() 를 지우면 떠난 장의 타이머가 화면 밖에서 계속 돌고(s19 에 6초
# 서 있으면 #mainSeq17 이 6 / 16 을 가리킨다), enter() 를 지우면 되감기와 재생이
# 같이 죽는다 — 그리고 활자 하한·720px 넘침 두 테스트가 기대는 '한 바퀴 깨우기'가
# 아무것도 깨우지 않게 된다. 둘 다 지워도 검사기는 통과하고, 이 파일에도 그것을
# 잡는 자리가 없었다.


def autoplaying_slide(pg):
    """leave() 를 가진 ON_ENTER 자산이 실린 첫 슬라이드의 (id, 번호). 없으면 skip.

    특정 장 번호를 적지 않는다 — 장이 늘거나 번호가 바뀌어도 그대로 돈다."""
    got = pg.evaluate("""() => {
      for (const id of Object.keys(ON_ENTER)) {
        if (!ON_ENTER[id].leave) continue;
        const i = Deck.slides.findIndex(s => s.id === id);
        if (i >= 0 && Deck.slides[i].querySelector('.seq-counter')) return [id, i];
      }
      return null;
    }""")
    if not got:
        pytest.fail(MUST_EXIST % 'leave() 를 가진 자동재생 자산')
    return got[0], got[1]


def seq_step(pg, sid):
    """'3 / 16' 계기판에서 현재 단계 번호만 뽑는다."""
    return pg.evaluate(
        'id => +document.getElementById(id).querySelector(".seq-counter")'
        '.textContent.trim().split("/")[0]', sid)


def test_leaving_an_autoplaying_slide_stops_it(page):
    """떠난 장의 자동재생은 멈춘다.

    안 멈추면 화면 밖에서 계속 돈다. 재현된 결과: leave() 없이 s19 에 6초 서
    있으면 #mainSeq17 이 6 / 16 을 가리킨다. 나중에 그 장으로 ← 로 돌아오면
    발표자가 말하려던 단계가 아니라 혼자 굴러간 단계가 서 있고, 다른 장의 자산까지
    깨어나면 두 장이 동시에 진행한다."""
    page.goto(DECK)
    sid, i = autoplaying_slide(page)
    goto(page, i)
    page.wait_for_timeout(2200)                 # 자동재생은 1700ms 간격이다
    running = seq_step(page, sid)
    assert running > 1, '자동재생이 애초에 돌지 않는다 (%d 단계)' % running

    goto(page, i + 1)                           # 떠난다
    left = seq_step(page, sid)
    page.wait_for_timeout(4000)
    assert seq_step(page, sid) == left, \
        '%s 를 떠났는데 시퀀스가 화면 밖에서 %d → %d 로 계속 갔다' % (
            sid, left, seq_step(page, sid))


def test_entering_an_autoplaying_slide_rewinds_and_starts_it(page):
    """들어온 장의 자동재생은 처음부터 다시 시작한다.

    enter() 가 없으면 두 가지가 같이 죽는다. 되감기(← 로 돌아왔을 때 발표자가
    설명을 다시 시작하는데 화면은 마지막 단계에 서 있다)와 재생(화면이 아예 안
    움직인다). 활자 하한·720px 테스트의 '한 바퀴 깨우기'도 이 호출에 기댄다."""
    page.goto(DECK)
    sid, i = autoplaying_slide(page)
    goto(page, i)
    page.wait_for_timeout(2200)
    assert seq_step(page, sid) > 1
    goto(page, i + 1)                           # 나갔다가
    goto(page, i)                               # 다시 들어온다

    assert seq_step(page, sid) == 1, \
        '%s 에 다시 들어왔는데 처음으로 되감기지 않았다 (%d 단계)' % (
            sid, seq_step(page, sid))
    page.wait_for_timeout(2200)
    assert seq_step(page, sid) > 1, '%s 에 들어왔는데 자동재생이 시작되지 않았다' % sid


def test_a_stray_right_arrow_during_autoplay_does_not_cost_the_slide(page):
    """자동재생 중의 → 한 번은 장을 잃지 않는다.

    두 장은 덱에서 가장 중요한 1분이다. 자동재생은 25.5초에 끝나는데 대본은 35초를
    더 말하고, 그 정지 구간에서 급한 발표자는 → 로 시퀀스를 밀어 본다. 비트가
    하나뿐이던 동안 그 한 번은 슬라이드를 넘겼고, ← 로 돌아오면 enter() 가 되감아
    25.6초를 처음부터 다시 재생했다 — 열여섯 단계를 처음 설명하던 도중에.

    지금은 → 가 '멈추고 마지막 단계에 선다'를 뜻한다. 자동재생이 어차피 가고 있던
    자리이므로 잃는 것이 없다. 한 번 더 누르면 그때 넘어간다."""
    page.goto(DECK)
    sid, i = autoplaying_slide(page)
    n = page.evaluate('i => beatCount(Deck.slides[i])', i)
    assert n > 1, '%s 에 → 가 쓸 비트가 없다 — 한 번의 오타가 장을 통째로 넘긴다' % sid

    goto(page, i)
    page.wait_for_timeout(2200)
    assert seq_step(page, sid) > 1, '자동재생이 돌지 않는다'

    page.keyboard.press('ArrowRight')
    assert state(page)['i'] == i, '자동재생 중의 → 한 번에 장을 잃었다'
    last = page.evaluate('id => ON_ENTER[id].n', sid)
    assert seq_step(page, sid) == last, \
        '→ 가 마지막 단계(%d)로 가지 않았다 (%d)' % (last, seq_step(page, sid))
    page.wait_for_timeout(2500)
    assert seq_step(page, sid) == last, '→ 뒤에도 자동재생이 계속 돈다'

    page.keyboard.press('ArrowRight')
    assert state(page)['i'] == i + 1, '비트를 다 썼는데 → 가 넘어가지 않는다'


def test_backing_into_an_autoplaying_slide_lands_on_the_beat_it_shows(page):
    """← 로 들어온 장의 비트는 자산이 정한 상태와 같아야 한다.

    '스스로 도는' 자산은 enter() 에서 되감아 다시 재생한다. 그런데 ← 는 원칙적으로
    마지막 비트로 들어오므로, 그대로 두면 화면은 1단계인데 비트만 마지막이다.
    HUD 가 '2/2'라고 거짓말을 하고, ← 를 한 번 더 눌러야 그 장을 빠져나간다.
    가름은 leave() 의 유무다 — 스스로 도는 것만 leave() 를 갖는다."""
    page.goto(DECK)
    sid, i = autoplaying_slide(page)
    goto(page, i + 1)
    page.keyboard.press('ArrowLeft')
    assert state(page)['i'] == i
    assert state(page)['b'] == 0, \
        '← 로 들어왔는데 비트가 %d 다 — 화면은 되감겼는데 HUD 만 끝에 서 있다' % state(page)['b']
    assert seq_step(page, sid) == 1, '← 로 들어왔는데 되감기지 않았다'
    page.keyboard.press('ArrowLeft')
    assert state(page)['i'] == i - 1, '← 한 번으로 자동재생 장을 빠져나가지 못한다'


def test_leaving_an_autoplaying_slide_backwards_never_shows_a_beat_that_lies(page):
    """스스로 도는 장에는 뒤로 가는 비트가 없다 — ← 는 비트를 거치지 않고 떠난다.

    비트 1 은 '멈추고 마지막 단계에 선다'이고 비트 0 의 go() 는 일부러 아무것도
    하지 않는다(도착 직후 enter() 가 덮어쓰기 때문이다). 그래서 → 로 비트 1 에
    올라간 뒤 ← 로 비트만 되돌리면, 화면은 16/16 에 선 채로 HUD 만 1/2 로 돌아간다.
    → 한 번이 지운 거짓말이 ← 한 번으로 되살아나는 셈이다. 거짓말하는 계기는
    없느니만 못하다.

    도착 규칙과 대칭이다. ← 로 들어올 때 비트를 거치지 않고 0 에서 시작하듯,
    나갈 때도 비트를 거치지 않고 떠난다. 가름도 같은 술어(leave() 의 유무)를 쓴다."""
    page.goto(DECK)
    sid, i = autoplaying_slide(page)
    goto(page, i)
    page.wait_for_timeout(2200)

    page.keyboard.press('ArrowRight')                 # 비트 1 — 멈추고 마지막 단계
    last = page.evaluate('id => ON_ENTER[id].n', sid)
    assert (state(page)['i'], state(page)['b']) == (i, 1)
    assert seq_step(page, sid) == last

    page.keyboard.press('ArrowLeft')
    st = state(page)
    if st['i'] == i:
        # 남아 있다면 화면과 계기가 같은 말을 해야 한다 — 그러지 못하는 것이 이 결함이다
        assert False, (
            '← 가 비트만 되돌렸다: 화면은 %d / %d 인데 HUD 는 비트 %d 를 말한다'
            % (seq_step(page, sid), last, st['b'] + 1))
    assert st['i'] == i - 1, '← 한 번으로 자동재생 장을 빠져나가지 못한다'


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
        pytest.fail(MUST_EXIST % '퀴즈가 둘 이상인 부록 장')
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


def test_the_position_bar_and_the_counter_read_the_same_coordinate_system(page):
    """막대와 그 옆의 숫자가 같은 것을 세야 한다.

    무대 위에서 발표자는 이 둘을 한눈에 본다. 숫자가 "26 / 48"인데 막대가 64.6%
    에 서 있으면 어느 쪽을 믿을지 정해야 하고, 그건 발표 중에 할 일이 아니다.

    이 성질은 '지금 통과한다'만으로는 확인되지 않는다. 본편 53장이 전부 부록
    14장보다 앞에 있는 동안에는 절대 index + 1 과 본편 번호가 우연히 같기 때문이다.
    그 순서를 강제하는 것은 아무것도 없으므로, 여기서는 부록을 앞으로 끌어와
    두 좌표계를 일부러 갈라 놓고 잰다."""
    page.goto(DECK)
    moved = page.evaluate("""() => {
      // 앞쪽 본편 몇 장을 부록으로 다시 분류해 두 좌표계를 갈라 놓는다.
      const mains = Deck.slides.filter(s => !s.classList.contains('appendix'));
      const picked = mains.slice(0, 5).map(s => s.id);
      picked.forEach(id => document.getElementById(id).classList.add('appendix'));
      return picked;
    }""")
    assert moved, '본편 장이 없다'
    try:
        probes = page.evaluate("""() => {
          const out = [];
          Deck.slides.forEach((s, i) => { if (!s.classList.contains('appendix')) out.push(i); });
          return [out[0], out[Math.floor(out.length / 2)], out[out.length - 1]];
        }""")
        bad = []
        for i in probes:
            page.evaluate('i => Deck.go(i)', i)
            pos = page.eval_on_selector('#barPos', 'e => parseFloat(e.style.width)')
            head = page.inner_text('#counter').split('·')[0].strip()
            num, den = [int(x) for x in head.split('/')]
            want = num / den * 100
            if abs(pos - want) > 0.5:
                bad.append('index %d: HUD "%s" = %.1f%% 인데 막대는 %.1f%%'
                           % (i, head, want, pos))
        assert bad == [], '막대와 숫자가 다른 좌표계를 쓴다:\n  %s' % '\n  '.join(bad)
    finally:
        page.evaluate("""ids => { ids.forEach(id =>
          document.getElementById(id).classList.remove('appendix')); Deck.go(0); }""", moved)

    # 되돌린 뒤에도 마지막 본편 장은 100% 다 — 위 조작이 새어 나가지 않았는지 같이 본다
    last_main = page.evaluate(
        'Deck.slides.map((s, i) => [i, s.classList.contains("appendix")])'
        '.filter(([, a]) => !a).map(([i]) => i).pop()')
    page.evaluate('i => Deck.go(i)', last_main)
    assert page.eval_on_selector('#barPos', 'e => parseFloat(e.style.width)') \
        == pytest.approx(100, abs=0.5)


def test_form_controls_keep_the_keys_they_use(page):
    """<select> 에 포커스가 있을 때 ↓ 는 값을 바꾸지, 슬라이드를 넘기지 않는다.

    동시에 덱의 손잡이는 살아 있어야 한다. tagName 만 보고 통째로 return 하면
    select 를 한 번 클릭한 뒤로 O·P·A·Escape 가 전부 죽는다 — 원래 버그보다 나쁘다."""
    page.goto(DECK)
    sel = page.evaluate('Deck.slides.findIndex(s => s.querySelector("select"))')
    if sel < 0:
        pytest.fail(MUST_EXIST % '<select> 가 있는 슬라이드')
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
    # 스페이스도 <select> 의 키다 — 목록을 펼친다. 화살표만 비켜 주고 스페이스를
    # 가로채면, 값을 고르려던 발표자가 슬라이드를 넘긴다.
    page.keyboard.press(' ')
    assert state(page)['i'] == sel, '<select> 에서 스페이스를 눌렀는데 슬라이드가 넘어갔다'
    assert page.evaluate('window.__pd') is False, \
        '덱이 스페이스에 preventDefault 를 걸어 <select> 가 목록을 못 편다'
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


def test_overview_numbers_main_slides_from_one_and_appendix_apart(page):
    """개요 칸의 번호도 HUD·숫자 점프와 같은 좌표계다.

    발표자는 개요에서 번호를 읽고 창을 닫은 뒤 그 번호를 친다. 여기가 67 좌표계로
    남으면 그 점프가 통째로 빗나간다."""
    page.goto(DECK)
    page.keyboard.press('o')
    nums = page.eval_on_selector_all(
        '.ov-cell', 'els => els.map(e => e.querySelector(".n").textContent.trim())')
    mains, apps = main_indexes(page), appendix_indexes(page)
    assert [nums[i] for i in mains] == [str(k + 1) for k in range(len(mains))], \
        '본편 칸이 1..%d 로 매겨지지 않았다' % len(mains)
    assert [nums[i] for i in apps] == ['부록 %d' % (k + 1) for k in range(len(apps))], \
        '부록 칸이 본편과 다른 표기를 쓰지 않는다: %s' % [nums[i] for i in apps]
    # 부록은 번호로 못 가는 대신 칸을 눌러서 간다 — 그 문이 살아 있어야 한다
    page.click('.ov-cell[data-i="%d"]' % apps[0])
    assert state(page)['i'] == apps[0], '부록 칸을 눌렀는데 안 갔다'


def test_overview_cells_hold_their_time_label_inside(page):
    """개요 칸의 0:xx 시간 이름표가 칸 밖으로 밀리지 않는다.

    이 화면은 설계 10절이 '눈 검사'의 도구로 지정한 자리다. 도구가 깨져 보이면
    그 도구로 내린 판정도 못 믿는다.

    한때 예순일곱 칸 중 예순한 칸이 최대 23px 씩 넘쳤다. 원인은 .ov-cell 의
    min-height 가 아니라 그리드 행 트랙이 '제목이 줄바꿈하기 전에' 74px 로 굳는
    것이었다. 그래서 이 테스트는 min-height 를 재지 않고 실제 좌표를 잰다 —
    #overview 의 grid-auto-rows 를 되돌리거나 minmax() 로 바꾸면(고정 최솟값이
    들어가는 순간 같은 74px 경로로 되돌아간다) 여기서 잡힌다.

    두 가지를 같이 본다. 이름표를 칸 안에 넣겠다고 칸만 늘리면 이번에는 칸이
    아래 줄 칸을 덮는다 — 그것도 실패다."""
    page.goto(DECK)
    page.keyboard.press('o')
    bad = page.evaluate("""() => {
      const cells = [...document.querySelectorAll('.ov-cell')];
      const cols = getComputedStyle(document.getElementById('overview'))
        .gridTemplateColumns.split(' ').length;
      const spill = [], collide = [];
      cells.forEach((c, i) => {
        const cb = c.getBoundingClientRect();
        const s = c.querySelector('.s').getBoundingClientRect();
        if (s.bottom - cb.bottom > 0.5)
          spill.push(c.querySelector('.n').textContent.trim() +
                     ' +' + (s.bottom - cb.bottom).toFixed(1) + 'px');
        const below = cells[i + cols];
        if (below && cb.bottom - below.getBoundingClientRect().top > 0.5)
          collide.push(c.querySelector('.n').textContent.trim());
      });
      return {spill, collide, n: cells.length};
    }""")
    assert bad['spill'] == [], \
        '%d 칸 중 %d 칸에서 시간 이름표가 칸 밖으로 밀렸다: %s' % (
            bad['n'], len(bad['spill']), bad['spill'][:6])
    assert bad['collide'] == [], \
        '칸이 아래 줄 칸을 덮는다: %s' % bad['collide'][:6]


# --- 글자 크기 하한 (Task 6) --------------------------------------------------
#
# check_slides.py 의 check_font_floor 는 인라인 style 만 본다. Task 5 리뷰가 잰
# 하한 미달 180개는 인라인이 하나도 없었다 — 전부 CSS 규칙이었다. 상속·구체성·
# :has() 까지 풀어야 진짜 크기가 나오므로, 그건 정규식이 아니라 브라우저만 답할 수
# 있다. 그래서 실제 강제는 여기서 한다.

FONT_FLOOR = 24        # px, 1280 좌표계 본문 하한
FONT_FLOOR_MONO = 20   # px, 코드 하한

# 예외 목록 — (셀렉터, 바닥, 근거) 세 칸.
#
# 한때는 두 칸이었고 바닥이 없었다. 예외 셀렉터에 걸리면 MEASURE_FONTS 가 측정
# 자체를 건너뛰었으므로 .seq-cap · .badge · .dia-tag 를 1px 로 줄여도 아무 테스트가
# 울지 않았다 — 근거("같은 말이 옆에서 제 크기로 다시 나온다")는 성립하는데 그
# 근거가 지켜지는지를 아무도 재지 않는 상태였다. 지금은 줄마다 제 바닥이 있고,
# 값은 전부 '지금 쓰는 크기 그대로'다. 즉 더 줄이는 것만 막는다.
#
# 이 목록은 oauth2_slides.html 의 DECK:STAGE:CSS 「활자 하한」 주석 안
# '예외 목록 시작/끝' 블록과 한 글자씩 짝을 이룬다. 아래
# test_the_font_floor_exemptions_match_their_css_comment 가 대조한다.
EXEMPT = [
    ('.seq-cap', 20,
     '시퀀스 행 이름표. 지도의 범례이고, 같은 말이 바로 아래 .seq-detail 의 .lbl 에 24px 로 다시 나온다'),
    ('.seq-msg.self .seq-pill', 20,
     'self 단계(from===to)의 이름표. .seq-cap 의 짝이고 근거도 같다. 부록 a02 에서 처음 쓰인다'),
    ('.seq-legend, .seq-legend *', 15,
     '채널 색 범례. "노란 파선이 프론트채널입니다"라고 발표자가 말한다'),
    ('.dia-tag', 11,
     '그림 왼쪽 위 꼬리표. 바로 옆 <h2> 가 같은 말을 44px 로 한다'),
    ('.badge', 16,
     '"실제 HMAC-SHA256 서명/검증" 같은 부가 표지. 내용이 아니라 표지다'),
    ('.jwt-parts, .jwt-parts *', 15,
     '토큰 세 토막의 이름표. 바로 위 .jwt-raw 의 세 가지 색이 같은 말을 한다'),
    ('.seq-title', 18,
     '시퀀스 제목 줄. 그 장의 <h2> 가 같은 말을 크게 한다'),
    ('.seq-counter', 18,
     '"3 / 16" 계기판. 청중이 아니라 발표자가 보는 숫자다'),
    ('.step-n', 16,
     '단계 번호. 바로 옆 .lbl 이 단계 이름을 24px 로 말한다'),
    ('.seq-controls button', 18,
     '◀ 이전 · 다음 ▶ 이송 버튼. 발표자의 손잡이다'),
    ('svg, svg *', 12,
     '그림 속 글자. viewBox 좌표를 화면 px 로 환산해서 잰다. 같은 말을 .dia-cap 이 26px 로 다시 싣는다'),
]

# CSS 주석 쪽의 한 줄: "     [.seq-cap] 바닥 20px — 근거"
EXEMPT_BLOCK = re.compile(
    r'====\s*예외 목록 시작\s*====(.*?)====\s*예외 목록 끝\s*====', re.S)
EXEMPT_LINE = re.compile(r'^\s*\[([^\]]+)\]\s*바닥\s*(\d+)px\s*—\s*(.+?)\s*$')

MEASURE_FONTS = """
(spec) => {
  const bad = [];
  // #stage 는 fitStage() 가 뷰포트에 맞춰 scale() 한다. SVG 안의 글자를 화면 px 로
  // 환산할 때 그 배율을 되나눠야 1280 좌표계의 숫자와 비교가 된다.
  const k = document.getElementById('stage').getBoundingClientRect().width / 1280;
  document.querySelectorAll('.slide').forEach(slide => {
    slide.querySelectorAll('*').forEach(el => {
      if (!el.getClientRects().length) return;          // 그려지지 않는 것은 읽히지도 않는다
      const own = Array.from(el.childNodes)
        .filter(n => n.nodeType === 3 && n.textContent.trim())
        .map(n => n.textContent.trim()).join(' ');
      if (!own) return;                                 // 자식만 있는 상자는 글자를 안 나른다
      const cs = getComputedStyle(el);
      let px = parseFloat(cs.fontSize);
      // SVG 의 font-size 는 viewBox 좌표다. 그대로 24 와 비교하면 다른 단위끼리
      // 비교하는 것이므로, getScreenCTM 으로 화면 px 로 편 뒤 무대 배율을 되나눈다.
      const sv = el.ownerSVGElement;
      if (sv) { const m = sv.getScreenCTM(); if (m) px = px * m.d / k; }
      const mono = /mono|Menlo|Consolas|Courier/i.test(cs.fontFamily);
      let floor = mono ? spec.mono : spec.body;
      // 예외에 걸리면 그 줄의 바닥으로 잰다 — 건너뛰지 않는다. 여러 줄에 걸리면
      // 가장 낮은 바닥을 쓴다(목록의 순서에 답이 달리지 않게).
      const hits = spec.exempt.filter(([sel]) => el.matches(sel)).map(([, f]) => f);
      if (hits.length) floor = Math.min(...hits);
      if (px + 0.01 < floor) {
        bad.push(slide.id + ' ' + el.tagName.toLowerCase() +
                 (el.className ? '.' + String(el.className.baseVal !== undefined
                    ? el.className.baseVal : el.className).trim().split(/\\s+/).join('.') : '') +
                 '  ' + px.toFixed(1) + 'px < ' + floor + '  | ' + own.slice(0, 40));
      }
    });
  });
  return bad;
}
"""

MEASURE_SPEC = {
    'body': FONT_FLOOR,
    'mono': FONT_FLOOR_MONO,
    'exempt': [[sel, floor] for sel, floor, _ in EXEMPT],
}


def test_the_font_floor_exemptions_match_their_css_comment():
    """예외 목록은 두 곳에 있고, 두 곳이 같아야 한다.

    덱의 CSS 주석은 다음 덱을 짓는 사람이 먼저 읽는 자리이고, 이 파일의 EXEMPT 는
    실제로 강제하는 자리다. 한때 둘은 이미 벌어져 있었다 — 주석은 "여섯 갈래"라고
    적어 놓고 일곱 줄에 열 개의 셀렉터를 늘어놓았고, EXEMPT 에는 열한 줄이 있었으며,
    노트는 "예외 열두 줄"이라고 했다. 셀렉터도 세 자리에서 달랐다(.seq-pill ↔
    .seq-msg.self .seq-pill 등). 주석이 "한 글자씩 짝을 이룬다"고 약속하는 이상,
    그 약속을 사람의 성실함이 아니라 이 테스트가 지켜야 한다.

    브라우저가 필요 없는 검사라 chromium 이 없어도 돈다."""
    with open(os.path.join(ROOT, 'oauth2_slides.html'), encoding='utf-8') as fh:
        html = fh.read()
    block = EXEMPT_BLOCK.search(html)
    assert block, 'DECK:STAGE:CSS 에서 「예외 목록 시작/끝」 블록을 찾지 못했다'

    parsed = []
    for line in block.group(1).splitlines():
        m = EXEMPT_LINE.match(line)
        if m:
            parsed.append((m.group(1), int(m.group(2)), m.group(3)))

    assert parsed == EXEMPT, (
        'CSS 주석의 예외 목록과 EXEMPT 가 다르다.\n'
        'CSS  (%d줄): %s\nEXEMPT(%d줄): %s' % (
            len(parsed), [p[:2] for p in parsed],
            len(EXEMPT), [e[:2] for e in EXEMPT]))
    assert len(EXEMPT) == 11, \
        '예외가 %d줄이다 — CSS 주석·노트의 "열한 줄"도 같이 고쳐라' % len(EXEMPT)


def warm_up(pg):
    """측정 전에 덱을 한 바퀴 깨우고, 측정 함수를 페이지에 심는다.

    도착해야 만들어지는 자산(s45 의 JWT 데모, 시퀀스)이 있어서 한 장씩 들른다 —
    그 일을 하는 것이 ON_ENTER.enter() 다. 퀴즈 해설은 눌러야 열리므로 최악의
    상태로 재려고 미리 펼친다."""
    n = pg.evaluate('Deck.slides.length')
    for i in range(n):
        pg.evaluate('i => Deck.go(i)', i)
    pg.evaluate('Deck.go(0)')
    pg.evaluate("document.querySelectorAll('.slide .explain')"
                ".forEach(e => e.classList.add('show'))")
    pg.evaluate('fn => { window.__measure = eval(fn); }', MEASURE_FONTS)


def test_every_exempted_selector_is_measured_against_a_real_floor(page):
    """예외에도 바닥이 있다 — 건너뛰는 것이 아니라 낮춰서 잰다.

    한때 예외 셀렉터에 걸리면 측정 자체를 건너뛰었다. 그래서 .seq-cap(20px)·
    .badge(16px)·.dia-tag(11px)를 나중에 누가 1px 로 줄여도 아무 테스트가 울지
    않았다. 근거("같은 말이 옆에서 제 크기로 다시 나온다")는 성립하는데, 그 근거가
    지켜지는지를 아무도 재지 않는 상태였다.

    바닥이 실제로 걸리는지를 줄마다 밟아 본다. 바닥을 1px 올려 다시 재서 그
    셀렉터가 잡히면, 지금 크기가 바닥에 닿아 있다는 뜻이다 — 즉 더 줄이는 순간
    잡힌다. 헐거우면(실제 크기가 바닥보다 크면) 그 틈만큼은 여전히 아무도 안 본다.

    CSS 를 주입해서 확인할 수는 없다. 크롬은 지금 서 있지 않은 장의 숨은 요소를
    다시 스타일링하지 않아서, 넣은 규칙이 그 장에는 닿지 않는다."""
    page.goto(DECK)
    warm_up(page)
    slack = []
    for sel, floor, _ in EXEMPT:
        # 대상만 바닥을 1 올리고 나머지 예외는 0 으로 내린다. 그러면 보고되는 것은
        # 이 셀렉터가 잡은 요소뿐이다 — 본문·코드 하한은 덱이 이미 지키고 있다.
        spec = {
            'body': FONT_FLOOR, 'mono': FONT_FLOOR_MONO,
            'exempt': [[other, (floor + 1) if other == sel else 0]
                       for other, _f, _r in EXEMPT],
        }
        if not page.evaluate('spec => window.__measure(spec)', spec):
            slack.append('%s: 바닥 %dpx 인데 실제 크기가 그보다 커서 헐겁다 — '
                         '실측에 맞춰 올려라' % (sel, floor))
    assert slack == [], \
        '예외의 바닥이 실제 크기에 닿아 있지 않다:\n  %s' % '\n  '.join(slack)


def test_every_visible_text_is_at_or_above_the_font_floor(page):
    """슬라이드 전체를 돌며 실제 computed font-size 를 재고 하한과 대조한다.

    특정 슬라이드를 가리키지 않는다 — 문서에 있는 .slide 를 전부 훑으므로 장이
    늘어도 그대로 돈다. 예외는 EXEMPT 에 적힌 것뿐이고, 목록에 없는 것이 하한
    아래로 내려가면 그 자리에서 실패한다."""
    page.goto(DECK)
    warm_up(page)
    bad = page.evaluate(MEASURE_FONTS, MEASURE_SPEC)
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


# --- 검사기와 덱이 같은 초를 말한다 (M6 후속) ---------------------------------

def test_the_deck_and_the_checker_agree_on_every_slide_time(page):
    """예순일곱 장 전부에서 두 구현이 같은 초를 내야 한다.

    한때 아니었다. 검사기가 `round(chars/SPEED, 1)` 로 한 번 접고 `_fmt` 가 다시
    접는 동안, 덱은 원값에 `Math.round` 를 한 번만 했다. 파이썬의 round 는 .5 를
    짝수로 붙이고 자바스크립트는 위로 붙이므로 아홉 장(s06·s26·s28·s29·s32·
    a01·a03·a08·a10)이 1초씩 갈렸다. 합계는 안 움직였지만, 상수를 맞춰 놓고
    "두 소비자가 같은 바이트를 읽으니 같은 답이 나온다"고 말하는 것은 그때
    거짓이었다 — test_the_deck_and_the_checker_share_their_constants 가 지키는
    것은 상수까지이지 답까지가 아니다.

    중간 반올림을 지우면 둘이 완전히 같아진다. chars/5.5 = 2*chars/11 이 정확히
    x.5 가 되려면 4*chars = 11*(2m+1) 이어야 하는데 오른쪽은 언제나 홀수라,
    짝수 반올림 규칙이 발동할 동점 자체가 생기지 않는다.

    개요 칸의 0:xx 도 같은 값을 쓰므로, 여기가 갈리면 화면과 검사기 출력이
    한 장에서 다른 숫자를 말한다."""
    page.goto(DECK)
    deck = cs.read_deck(os.path.join(ROOT, 'oauth2_slides.html'))
    mine = page.evaluate(
        'Deck.slides.map(s => [s.id, Deck.secOf(s.id), fmt(Deck.secOf(s.id))])')
    assert len(mine) == len(deck.slides), '장 수가 다르다'

    bad = []
    for sid, sec, shown in mine:
        want = cs.seconds(deck.script[sid])
        if abs(sec - want) > 1e-9:
            bad.append('%s: 덱 %.4f초 ≠ 검사기 %.4f초' % (sid, sec, want))
        elif shown != cs._fmt(want):
            bad.append('%s: 덱은 %s 라 쓰고 검사기는 %s 라 쓴다' % (sid, shown, cs._fmt(want)))
    assert bad == [], '두 구현이 다른 초를 말한다 (%d장):\n  %s' % (
        len(bad), '\n  '.join(bad[:12]))


# --- 넘치지 않는 서랍은 키를 먹지 않는다 (I1 후속) ----------------------------

def non_overflowing_notes_slide(pg):
    """대본이 서랍 안에 다 들어가는 슬라이드. 예순일곱 중 쉰한 장이 그렇다.

    앞뒤 양쪽으로 움직일 수 있어야 네 키를 다 잴 수 있으므로 첫 장과 끝 장은 뺀다."""
    i = pg.evaluate("""() => {
      const n = document.getElementById('notes');
      const keep = Deck.index, wasOn = n.classList.contains('on');
      n.classList.add('on');
      let found = -1;
      for (let i = 1; i < Deck.slides.length - 1; i++) {
        Deck.go(i); notesFor = null; renderNotes();
        if (n.scrollHeight - n.clientHeight <= 1) { found = i; break; }
      }
      if (!wasOn) n.classList.remove('on');
      Deck.go(keep);
      return found;
    }""")
    if i < 0:
        pytest.fail(MUST_EXIST % '대본이 서랍 안에 다 들어가는 슬라이드')
    return i


def test_a_notes_drawer_that_fits_does_not_eat_the_navigation_keys(page):
    """넘치지 않는 서랍은 굴릴 것이 없으므로 키를 가져가면 안 된다.

    열려 있다는 이유만으로 넘겨주면, 그 키는 창을 굴리지도 못하고 덱을 넘기지도
    못한 채 그냥 죽는다. 서랍이 넘치는 장은 예순일곱 중 열여섯뿐이라 나머지
    쉰한 장에서 네 키가 전부 무반응이었다. 그중 PageDown·PageUp 은 발표자용
    리모컨이 보내는 키이고, 서랍은 발표하는 내내 열어 두는 물건이다."""
    page.goto(DECK)
    i = non_overflowing_notes_slide(page)
    dead = []
    for key, delta in (('PageDown', 1), ('ArrowDown', 1), ('PageUp', -1), ('ArrowUp', -1)):
        goto(page, i)
        page.keyboard.press('s')
        assert on(page, '#notes') is True
        assert page.eval_on_selector(
            '#notes', 'e => e.scrollHeight - e.clientHeight <= 1'), '서랍이 넘친다'
        page.keyboard.press(key)
        if state(page)['i'] != i + delta:
            dead.append(key)
        page.keyboard.press('Escape')
    assert dead == [], \
        '넘치지 않는 서랍이 이 키들을 먹었다(창도 안 굴러가고 덱도 안 움직인다): %s' % dead
