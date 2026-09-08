"""defensive_programming.html 의 도해 정적 불변식.

브라우저 없이 소스만 본다. 동작 검사는 test_defensive_diagram_behavior.py 가 맡는다.
"""
import re
from pathlib import Path

import pytest

DOC = Path(__file__).resolve().parent.parent / 'defensive_programming.html'

# 이 문서가 그리기로 한 도해. 태스크가 하나씩 채운다.
# (figure id, 그 도해가 속한 섹션 id)
DIAGRAMS = [
    ('diaBlame', 'trace'),
    ('diaSilent', 'silent'),
    ('diaBoundary', 'boundary'),
    ('diaShape', 'invariant'),
]

FIGURE_OPEN = re.compile(r'<figure class="dia" id="([^"]+)"')
# data-at 이 받는 표기는 셋뿐이다. 오타는 조용히 '그 단계에 안 보임'이 되므로 여기서 막는다.
DATA_AT = re.compile(r'\bdata-at="([^"]*)"')
DATA_AT_OK = re.compile(r'^\s*\d+(?:-\d+|\+)?(?:\s*,\s*\d+(?:-\d+|\+)?)*\s*$')

# 그림 안의 글자도 산문이다. 각색 금칙어는 SVG 안에서도 나오면 안 된다.
FORBIDDEN = ['cheil', 'ssfshop', 'dspCnr', 'ConttImg',
             'includeMultiMainContents', 'SecureValueExpression', '전시코너', '전시 코너']


@pytest.fixture(scope='module')
def src():
    return DOC.read_text(encoding='utf-8')


def iter_figures(src):
    """<figure class="dia" ...> 를 짝이 맞는 </figure> 까지 (id, 본문) 으로 내놓는다.

    figure 는 이 문서에서 중첩되지 않지만, 셀렉터가 어긋나면 조용히 0개를 세게 되므로
    아래 test_the_figure_parser_still_matches_the_markup 이 개수를 대조한다.
    """
    for m in FIGURE_OPEN.finditer(src):
        end = src.find('</figure>', m.end())
        if end != -1:
            yield m.group(1), src[m.end():end]


def test_the_figure_parser_still_matches_the_markup(src):
    assert src.count('<figure class="dia"') == len(list(iter_figures(src)))


def test_every_planned_diagram_is_present(src):
    assert [fid for fid, _ in iter_figures(src)] == [fid for fid, _ in DIAGRAMS]


def test_every_diagram_sits_in_its_chapter(src):
    for fid, sec in DIAGRAMS:
        sec_start = src.index(f'<section id="{sec}"')
        sec_end = src.index('</section>', sec_start)
        assert sec_start < src.index(f'id="{fid}"') < sec_end, f'{fid} 가 {sec} 밖에 있다'


def test_every_diagram_carries_one_svg_with_a_sentence_label(src):
    for fid, body in iter_figures(src):
        assert body.count('<svg') == 1, f'{fid}: svg 는 하나여야 한다'
        m = re.search(r'<svg[^>]*\baria-label="([^"]*)"', body)
        assert m, f'{fid}: aria-label 이 없다'
        # 도형 목록이 아니라 문장이어야 한다. 문장이면 최소한 마침표가 있고 길다.
        assert len(m.group(1)) >= 60 and '.' in m.group(1), f'{fid}: aria-label 이 문장이 아니다'
        assert 'role="img"' in body, f'{fid}: role="img" 가 없다'


def test_every_diagram_has_a_caption_and_a_step_box(src):
    for fid, body in iter_figures(src):
        assert '<figcaption>' in body, f'{fid}: figcaption 이 없다'
        assert 'class="dia-cap"' in body, f'{fid}: .dia-cap 이 없다'
        assert 'aria-hidden="true"' in body, f'{fid}: .dia-cap 을 낭독기에서 덮지 않았다'


def test_every_diagram_has_a_nonempty_figcaption(src):
    for fid, body in iter_figures(src):
        cap = re.search(r'<figcaption>(.*?)</figcaption>', body, re.S)
        assert cap and cap.group(1).strip(), f'{fid}: figcaption 이 비어 있다'


def test_data_at_notation_is_valid_everywhere(src):
    """표기 오타는 조용히 '그 단계에 안 보임'이 되므로 여기서 막는다.

    figure 본문 안만 본다. 문서 산문과 주석에 적힌 예시까지 검사하면 헛경보가 난다."""
    for fid, body in iter_figures(src):
        for raw in DATA_AT.findall(body):
            assert DATA_AT_OK.match(raw), f'{fid}: data-at="{raw}" 는 해석할 수 없는 표기다'


def test_diagrams_carry_no_internal_identifiers(src):
    for fid, body in iter_figures(src):
        for bad in FORBIDDEN:
            assert bad not in body, f'{fid}: 각색하지 않은 식별자 {bad}'


def test_the_evidence_the_first_diagram_must_keep(src):
    body = dict(iter_figures(src))['diaBlame']
    for keep in ('BeanELResolver', '_005fset_005f141', '9946'):
        assert keep in body, f'diaBlame 이 {keep} 을 잃었다'
