import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_slides as cs

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')


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

def test_appendix_slides_are_excluded_from_total():
    """부록은 발표하지 않는 장이다. 합계에 넣으면 읽지도 않을 분량 때문에
    본편을 깎게 된다."""
    d = deck('deck_with_appendix.html')
    assert 'a00' in d.script
    assert d.main_slides == ['s00', 's01']        # 부록 제외
    assert d.slides == ['s00', 's01', 'a00']      # 전체는 포함


def test_appendix_slide_still_needs_script():
    """꺼내 읽을 문장이 없으면 질문에 답할 수 없다. 대본 검사는 전체를 본다."""
    d = deck('deck_with_appendix.html')
    assert cs.check_script_present(d) == []


def test_appendix_slide_seconds_are_still_bounded():
    """부록도 한 장에 25~110초를 지킨다 — 읽어 주는 장이기 때문이다."""
    assert cs.check_slide_seconds(deck('deck_with_appendix.html')) == []


def test_check_total_ignores_appendix_seconds():
    """부록 대본을 더해도 합계는 본편 두 장의 합 그대로여야 한다."""
    d = deck('deck_with_appendix.html')
    main_only = sum(cs.seconds(d.script[s]) for s in d.main_slides)
    reported = cs.check_total(d)
    assert len(reported) == 1                      # 픽스처는 52분에 한참 못 미친다
    assert cs._fmt(main_only) in reported[0]


def test_ok_fixture_has_no_appendix():
    """appendix 클래스가 없으면 전체와 본편이 같다."""
    d = deck('deck_ok.html')
    assert d.main_slides == d.slides
