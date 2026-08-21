import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_slides as cs

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = os.path.join(ROOT, 'oauth2_slides.html')


def deck(name):
    return cs.read_deck(os.path.join(HERE, name))


def test_read_deck_finds_slides_in_document_order():
    d = deck('deck_ok.html')
    assert d.slides == ['s00', 's01']


def test_read_deck_parses_script_block():
    d = deck('deck_ok.html')
    assert set(d.script) == {'s00', 's01'}
    assert isinstance(d.script['s00'], list)


def test_seconds_uses_5_5_chars_per_second():
    assert cs.seconds(['가' * 55]) == 10.0


def test_ok_fixture_has_no_missing_script():
    assert cs.check_script_present(deck('deck_ok.html')) == []


def test_missing_script_is_reported_with_slide_id():
    problems = cs.check_script_present(deck('deck_no_script.html'))
    assert len(problems) == 1
    assert 's01' in problems[0]


def test_ok_fixture_slide_seconds_in_range():
    assert cs.check_slide_seconds(deck('deck_ok.html')) == []


def test_slide_over_110_seconds_is_reported():
    problems = cs.check_slide_seconds(deck('deck_too_long.html'))
    assert len(problems) == 1
    assert 's01' in problems[0]


def test_total_far_below_target_is_reported():
    problems = cs.check_total(deck('deck_ok.html'))
    assert len(problems) == 1
    assert '52:00' in problems[0]


# --- 프레임 일치 (Task 5) ---------------------------------------------------

def test_frame_count_mismatch_is_reported():
    problems = cs.check_dia_frames(deck('deck_frame_mismatch.html'))
    assert len(problems) == 1
    assert 'diaX' in problems[0]


def test_ok_fixture_has_no_dia_to_check():
    assert cs.check_dia_frames(deck('deck_ok.html')) == []


def test_figure_registered_to_another_slide_is_reported():
    """registerBeats('s01', wireDia('diaY',...)) 인데 diaY 의 마크업은 s02 에 있다.

    프레임 수는 맞으므로 프레임 일치 검사는 통과한다. 그래도 발표는 깨진다 —
    s01 은 그림 없이 비트만 셋이고, s02 는 그림이 있는데 구동기가 없다.
    슬라이드 번호를 다시 매길 때 조용히 생기는 어긋남이라 검사로 잡는다."""
    problems = cs.check_dia_frames(deck('deck_dia_wrong_slide.html'))
    assert len(problems) == 1
    assert 'diaY' in problems[0] and 's01' in problems[0]


def test_figure_in_its_registered_slide_is_not_reported():
    assert cs.check_dia_frames(deck('deck_frame_mismatch.html')) == [
        'diaX: data-at 프레임 2개 ≠ wireDia 단계 3개']


def test_sequence_mounted_in_another_slide_is_reported():
    """createSequence 로 마운트한 자산도 wireDia 와 같은 방식으로 어긋난다.

    한때 REGISTER_WIRE_DIA 가 registerBeats(…, wireDia(…)) 만 잡았다. 그래서 부록의
    세 시퀀스(registerBeats('a02', createSequence('nativeSeq', …)))와 ON_ENTER 로
    얹은 두 시퀀스는 아무도 안 봤다 — <div class="seq-mount" id="nativeSeq"> 를 a02
    에서 a03 으로 옮기면 검사기가 exit 0 · '✓ 통과' 를 내면서 a02 는 beatCount 9
    짜리 플레이어 없는 장이 됐다. wireDia 쪽 절반이 막으려고 존재하는 그 실패다.

    픽스처는 두 갈래를 다 들고 있다. registerBeats 로 직접 등록한 nativeSeq 와
    변수를 거쳐 ON_ENTER 에 얹은 mainSeqA."""
    problems = cs.check_dia_frames(deck('deck_seq_wrong_slide.html'))
    assert len(problems) == 2, problems
    joined = '\n'.join(problems)
    assert 'nativeSeq' in joined and 's01' in joined      # registerBeats 갈래
    assert 'mainSeqA' in joined and 's00' in joined       # ON_ENTER 갈래


def test_sequence_mounted_in_its_own_slide_is_not_reported():
    """같은 픽스처의 s04 는 등록과 마크업이 한 장에 있다. 여기까지 보고하면
    검사가 '전부 위반'이라고 말하는 것과 같아 아무 신호가 아니다."""
    problems = cs.check_dia_frames(deck('deck_seq_wrong_slide.html'))
    assert not any('ccSeq' in p for p in problems), problems


def test_on_enter_with_an_inline_object_has_no_mount_to_check():
    """ON_ENTER['s45']={enter(){…}} 처럼 그 자리에서 만든 객체는 마운트 id 가 없다.

    대조할 것이 없으므로 짝 목록에 들어오지 않아야 한다 — 들어오면 마운트 이름
    자리에 변수 이름이 앉아 없는 id 를 찾다가 거짓 위반이 된다."""
    html = """
      ON_ENTER['s45']={ enter(){ build(); } };
      const seqZ=createSequence('zMount',{}); ON_ENTER['s17']=seqZ;
    """
    assert cs._mount_bindings(html) == [('s17', 'zMount')]


# --- 슬라이드 판별: 이름만 비슷한 section 을 세면 안 된다 (Task 5) -----------

def test_lookalike_class_names_are_not_slides():
    """class="slide-notes" · "not-slide" 는 슬라이드가 아니다.
    \\b 는 하이픈을 낱말 경계로 보기 때문에 정규식만으로는 둘 다 통과한다."""
    d = deck('deck_lookalike_sections.html')
    assert d.slides == ['s00', 's01']


# --- 외부 요청 금지 (Task 5) ------------------------------------------------

def test_external_resources_are_reported():
    problems = cs.check_no_external(deck('deck_external.html'))
    joined = '\n'.join(problems)
    assert '<link' in joined and '외부 리소스 로드' in joined   # <link href="https://...">
    assert 'fetch' in joined                                  # 네트워크 호출
    assert 'CSS 원격 참조' in joined                           # @import url(https://...)
    assert len(problems) == 3


def test_ok_fixture_has_no_external_resource():
    assert cs.check_no_external(deck('deck_ok.html')) == []


# --- 대본 안의 </script (Task 5) --------------------------------------------

def test_close_script_inside_narration_is_reported():
    problems = cs.check_script_terminator(deck('deck_script_terminator.html'))
    assert len(problems) == 1
    assert '</script' in problems[0]


def test_ok_fixture_script_block_is_closed_exactly_once():
    assert cs.check_script_terminator(deck('deck_ok.html')) == []


def test_open_script_tag_inside_narration_is_not_reported():
    """XSS 를 설명하는 대본은 "<script> 한 줄을 넣으면" 이라고 쓴다.

    여는 태그는 HTML 파서를 끊지 않으므로 대본은 멀쩡하다. '다음 <script 까지'로
    구간을 잡던 옛 구현은 이 문장에서 구간이 잘려 "</script 가 0개 있다"고
    엉뚱한 곳을 가리켰다."""
    assert cs.check_script_terminator(deck('deck_script_open_in_narration.html')) == []


# --- 글자 크기 하한 (Task 6) --------------------------------------------------

def test_inline_font_size_below_floor_is_reported():
    problems = cs.check_font_floor(deck('deck_small_text.html'))
    assert len(problems) == 1
    assert '18' in problems[0]


def test_ok_fixture_passes_font_floor():
    assert cs.check_font_floor(deck('deck_ok.html')) == []


def test_code_gets_the_lower_mono_floor():
    """<pre>/<code> 는 20px 이 하한이다. 같은 20px 이 본문이면 위반, 코드면 통과."""
    problems = cs.check_font_floor(deck('deck_small_text.html'))
    assert not any('pre' in p for p in problems), '코드 20px 을 본문 하한으로 재고 있다'


# --- 부록은 합계에서 뺀다 (Task 8) ------------------------------------------
#
# 픽스처 deck_with_appendix.html 은 일부러 규칙을 어긴 부록 두 장을 들고 있다 —
# 대본이 없는 a01 과 25초에 못 미치는 a02. '어기지 않은 것을 보고 통과라고 말하는'
# 테스트는 구현을 아무리 망가뜨려도 통과하기 때문이다(합계에서 빼는 것과 대본을
# 요구하는 것은 서로 다른 규칙인데, 둘 다 지키는 픽스처로는 구분이 안 된다).

def test_appendix_slides_are_excluded_from_total():
    """부록은 발표하지 않는 장이다. 합계에 넣으면 읽지도 않을 분량 때문에
    본편을 깎게 된다."""
    d = deck('deck_with_appendix.html')
    assert 'a00' in d.script
    assert d.main_slides == ['s00', 's01', 's02', 's03']       # 부록 제외
    assert d.slides == ['s00', 's01', 's02', 's03',
                        'a00', 'a01', 'a02']                   # 전체는 포함


def test_lookalike_class_names_are_not_appendix():
    """class="slide appendix-note" · "slide not-appendix" 는 부록이 아니다.

    'appendix' 를 부분 문자열로 찾으면 둘 다 부록으로 세어져 합계에서 조용히
    빠진다. 화면에는 아무 표시가 없고, 발표 분량이 줄어든 것은 리허설에서야
    드러난다. 위 test_lookalike_class_names_are_not_slides 가 'slide' 에 대해
    지키는 것과 같은 성질이다."""
    d = deck('deck_with_appendix.html')
    assert 's02' in d.main_slides and 's03' in d.main_slides


def test_appendix_slide_without_script_is_reported():
    """부록에도 대본은 있어야 한다 — 질문이 나와 꺼내는 순간 읽게 되는 문장이다.

    대본 검사는 main_slides 가 아니라 slides 를 돈다. 이 테스트가 그것을 붙잡는다:
    check_script_present 가 본편만 보게 되면 a01 의 빈 대본이 보고되지 않는다."""
    problems = cs.check_script_present(deck('deck_with_appendix.html'))
    assert problems == ['a01: 대본이 없다']


def test_appendix_slide_below_the_floor_is_reported():
    """부록도 한 장에 25~110초를 지킨다. a02 는 1초짜리라 하한에 걸려야 한다.

    check_slide_seconds 가 main_slides 를 돌게 되면 이 위반이 사라진다."""
    problems = cs.check_slide_seconds(deck('deck_with_appendix.html'))
    assert len(problems) == 1
    assert problems[0].startswith('a02:') and '하한 25초' in problems[0]


def test_check_total_ignores_appendix_seconds():
    """부록 대본을 더해도 합계는 본편 장들의 합 그대로여야 한다."""
    d = deck('deck_with_appendix.html')
    main_only = sum(cs.seconds(d.script[s]) for s in d.main_slides)
    reported = cs.check_total(d)
    assert len(reported) == 1                      # 픽스처는 52분에 한참 못 미친다
    assert cs._fmt(main_only) in reported[0]


def test_ok_fixture_has_no_appendix():
    """appendix 클래스가 없으면 전체와 본편이 같다."""
    d = deck('deck_ok.html')
    assert d.main_slides == d.slides


# --- 실물 덱 (최종 점검) -----------------------------------------------------
#
# 여기까지의 테스트는 전부 픽스처를 본다. 그래서 `pytest tools/` 는 통과하는데
# `check_slides.py oauth2_slides.html` 은 실패하는 상태가 만들어질 수 있었다 —
# 두 관문을 잇는 것이 사람이 명령 두 개를 치는 습관뿐이었기 때문이다. 그림을 다른
# 장으로 옮기기, wireDia 단계 수 어긋내기, 외부 <script src>·<img>·fetch() 넣기,
# 합계를 ±3:00 밖으로 밀기, 25초 미만·110초 초과 장 만들기, 부록을 52:00 합계에
# 넣기 — 열 가지가 전부 59/59 통과였다. 아래 한 줄이 그 열 가지를 다 닫는다.


def test_the_shipped_deck_passes_every_check():
    """실제로 배포하는 덱을 검사기 전부에 물린다.

    이 테스트가 없으면 검사기와 테스트가 서로 다른 물건을 보고 각자 '통과'라고
    말한다. 픽스처는 규칙 하나하나가 사는지를 보고, 이 줄은 그 규칙들이 실물에
    실제로 걸리는지를 본다."""
    deck = cs.read_deck(DECK)
    problems = [p for check in cs.CHECKS for p in check(deck)]
    assert problems == [], '배포하는 덱이 검사기를 통과하지 못한다:\n  %s' % (
        '\n  '.join(problems[:20]))


def test_every_check_function_is_wired_into_the_gate():
    """CHECKS 에서 한 줄을 지우면 그 규칙은 조용히 사라진다.

    위 test_the_shipped_deck_passes_every_check 는 CHECKS 를 돌기 때문에, 항목이
    빠지면 '통과'가 더 쉬워질 뿐 아무 데도 걸리지 않는다. 목록 자체를 못으로 박는다."""
    assert [c.__name__ for c in cs.CHECKS] == [
        'check_script_present', 'check_slide_seconds', 'check_total',
        'check_dia_frames', 'check_no_external', 'check_script_terminator',
        'check_font_floor',
    ], 'CHECKS 목록이 바뀌었다 — 규칙을 빼거나 더했다면 이 줄도 같이 고쳐라'


def test_the_thresholds_are_the_ones_the_deck_was_built_to():
    """허용 폭을 넓히는 것도 검사를 지우는 것과 같다.

    TOTAL_TOL 을 열 배로 늘리면 합계 검사는 살아 있는 채로 아무것도 막지 않는다.
    숫자를 바꾸는 것은 명세를 바꾸는 일이므로 여기서 한 번 멈추게 한다."""
    assert (cs.TOTAL_TARGET, cs.TOTAL_TOL) == (3120, 180)   # 52:00 ±3:00
    assert (cs.SLIDE_MIN, cs.SLIDE_MAX) == (25, 110)        # 초
    assert cs.SPEED == 5.5                                  # 자/초


def test_the_browser_gate_does_not_skip_itself_away():
    """활자 하한(24/20)을 강제하는 곳은 브라우저 테스트뿐이다.

    check_font_floor 는 인라인 style 만 보고, 이 덱에는 그런 값이 하나도 없어
    0개를 잡는다. CSS 규칙 쪽은 정규식으로 답이 안 나온다 — ASSET:CSS 의 이식값을
    DECK:STAGE:CSS 가 .slide 접두사로 덮어쓰는 구조라 규칙만 세면 실제로는 지켜지는
    38개를 위반이라고 부른다.

    그러니 test_deck_behavior.py 가 chromium 없다고 물러서면 그 계약은 통째로
    증발하면서 초록불이 뜬다. 이 테스트는 그 물러섬이 다시 들어오는 것을 막는다.
    브라우저가 필요 없으므로 chromium 없는 기계에서도 이 줄만은 돈다."""
    with open(os.path.join(os.path.dirname(DECK), 'tools', 'test_deck_behavior.py'),
              encoding='utf-8') as fh:
        src = fh.read()
    assert 'pytest.importorskip(' not in src, \
        'test_deck_behavior.py 가 임포트 단계에서 통째로 물러선다 — 브라우저가 ' \
        '없으면 24/20 계약이 조용히 사라진다'
    assert 'pytest.skip(NO_BROWSER' not in src, 'NO_BROWSER 를 skip 으로 낸다'
    for form in ("pytest.skip('chromium", 'pytest.skip("chromium'):
        assert form not in src, 'chromium 이 없을 때 skip 한다 — 실패해야 한다'
    assert 'pytest.fail(NO_BROWSER' in src, \
        '브라우저가 없을 때 시끄럽게 실패하는 자리가 없다'


DECK_CONST = re.compile(r'^const\s+(SPEED|SLIDE_MIN|SLIDE_MAX)\s*=\s*([\d.]+)\s*;', re.M)


def test_the_deck_and_the_checker_share_their_constants():
    """같은 숫자를 두 파일이 들고 있으면 한쪽만 고쳐진다.

    SPEED 는 대본 길이를 초로 바꾸는 값이고, SLIDE_MIN·SLIDE_MAX 는 개요 그리드가
    칸의 시간 색을 정하는 선이다. 검사기 쪽에만 "덱과 같은 값이어야 한다"고 적혀
    있었을 뿐 아무도 대조하지 않았다 — 덱의 const 만 고치면 검사기는 통과라고
    하는데 무대의 계기가 다른 말을 하거나, 위반이 아닌 장이 빨갛게 칠해진다.

    브라우저가 필요 없다. 두 파일의 텍스트를 읽어 비교할 뿐이다."""
    with open(DECK, encoding='utf-8') as fh:
        found = dict(DECK_CONST.findall(fh.read()))
    assert set(found) == {'SPEED', 'SLIDE_MIN', 'SLIDE_MAX'}, \
        '덱에서 못 찾은 상수가 있다: %s' % (
            {'SPEED', 'SLIDE_MIN', 'SLIDE_MAX'} - set(found))
    assert float(found['SPEED']) == cs.SPEED, \
        '덱의 SPEED %s ≠ 검사기의 %s' % (found['SPEED'], cs.SPEED)
    assert int(found['SLIDE_MIN']) == cs.SLIDE_MIN, \
        '덱의 SLIDE_MIN %s ≠ 검사기의 %s' % (found['SLIDE_MIN'], cs.SLIDE_MIN)
    assert int(found['SLIDE_MAX']) == cs.SLIDE_MAX, \
        '덱의 SLIDE_MAX %s ≠ 검사기의 %s' % (found['SLIDE_MAX'], cs.SLIDE_MAX)


def test_the_deck_does_not_hardcode_the_slide_length_limits_again():
    """개요 그리드가 25·110 을 다시 박으면 위 대조가 아무것도 막지 못한다."""
    with open(DECK, encoding='utf-8') as fh:
        line = [l for l in fh if l.lstrip().startswith('const warn =')]
    assert line, '개요 칸의 시간 색을 정하는 줄을 찾지 못했다'
    assert 'SLIDE_MAX' in line[0] and 'SLIDE_MIN' in line[0], \
        '개요 칸이 상수 대신 숫자를 다시 박았다: %s' % line[0].strip()


CHROME_BLOCK = re.compile(
    r'<!--\s*====\s*DECK:CHROME\s*====\s*-->(.*?)<!--\s*====\s*/DECK:CHROME\s*====\s*-->',
    re.S)
CORE_JS = re.compile(
    r'/\* ==== DECK:CORE:JS ==== \*/(.*?)/\* ==== /DECK:CORE:JS ==== \*/', re.S)
DOLLAR_ID = re.compile(r"""\$\(\s*['"]#([\w-]+)['"]""")
ANY_ID = re.compile(r"""\bid\s*=\s*["']([\w-]+)["']""")

# 대본 블록은 크롬이 아니다. 슬라이드별 문장이 사는 곳이라 덱마다 내용이 다르고,
# SLIDES 와 함께 움직인다.
NOT_CHROME = {'deck-script'}

CHROME_IDS = {'viewport', 'stage', 'bars', 'barPos', 'barTime', 'hud',
              'clock', 'counter', 'notes', 'overview', 'toast'}


def test_the_deck_chrome_lives_inside_its_own_marker():
    """DECK:CORE:CSS 가 꾸미고 DECK:CORE:JS 가 붙잡는 DOM 도 마커를 가져야 한다.

    설계 9절은 CORE 블록을 build_slides.py 의 템플릿으로 뽑겠다고 한다. 그런데
    크롬 마크업이 어느 마커에도 없으면, 그 절차대로 뽑은 CSS 와 JS 는 붙을 DOM 이
    하나도 없는 채로 나온다. paint() 는 첫 번째 없는 id 에서 그 자리에 던지므로
    '기능 하나가 죽는' 것이 아니라 '덱이 안 켜지는' 것이다."""
    with open(DECK, encoding='utf-8') as fh:
        html = fh.read()
    blocks = CHROME_BLOCK.findall(html)
    assert len(blocks) == 2, \
        'DECK:CHROME 블록이 %d개다 — SLIDES 가 #stage 안에 있어 둘로 갈린다' % len(blocks)
    have = set(ANY_ID.findall('\n'.join(blocks)))
    assert have == CHROME_IDS, \
        'DECK:CHROME 이 들고 있는 id 가 달라졌다: %s' % sorted(have)


def test_every_id_the_core_js_reaches_for_is_in_the_chrome_block():
    """코어 JS 가 $('#x') 로 찾는 것은 전부 크롬 안에 있어야 한다.

    이 짝이 어긋나면 두 조각을 같이 옮기지 않았다는 뜻이고, 그 결과는 화면이 아니라
    콘솔에서 터진다. 발표자 창의 id(now·nxt·el·pl…)는 자식 창 문서의 것이라
    d.getElementById 로 찾으므로 여기 걸리지 않는다."""
    with open(DECK, encoding='utf-8') as fh:
        html = fh.read()
    core = CORE_JS.search(html)
    assert core, 'DECK:CORE:JS 블록을 찾지 못했다'
    chrome = set(ANY_ID.findall('\n'.join(CHROME_BLOCK.findall(html))))
    missing = sorted(set(DOLLAR_ID.findall(core.group(1))) - NOT_CHROME - chrome)
    assert missing == [], \
        '코어 JS 가 찾는데 DECK:CHROME 에 없는 id: %s' % missing
