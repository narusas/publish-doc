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
