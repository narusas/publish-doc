#!/usr/bin/env python3
"""defensive_programming.html 의 문서 규약 검사.

check_tutorial.py 는 이 저장소의 튜토리얼 전부에 공통으로 적용되는 규칙만 본다.
이 파일은 그 위에 이 문서에만 있는 세 계약을 얹는다. 셋 다 눈으로 보면 '통과'라고
말하기 쉬운 규칙이라 기계에 맡긴다.

  1. 각색 규칙 — 사내에서 온 식별자가 하나도 남지 않았는가 (설계 문서 3절)
  2. 사슬 규칙 — 1~14장이 전부 '다음 문제'로 끝나는가 (설계 문서 6절)
  3. .stack 규칙 — 그 블록을 접어도 논지가 끊기지 않는가 (설계 문서 4절)

사용법: python3 -m pytest tools/test_defensive_document.py -v
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_tutorial as ct        # noqa: E402  (같은 tools/ 안의 표준 라이브러리 전용 모듈)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, 'defensive_programming.html')

# 설계 문서 3절. 사내에서 온 것은 하나도 남으면 안 된다. 오픈소스 클래스명과 줄
# 번호는 여기 없다 — 그것들은 독자가 자기 로그에서 알아봐야 하는 증거라서 남긴다.
FORBIDDEN = [
    'cheil', 'ssfshop', 'dspCnr', 'ConttImg',
    'includeMultiMainContents', 'SecureValueExpression',
    '전시코너', '전시 코너',
]

# 반대로 반드시 있어야 하는 것. 각색하다가 증거까지 지우면 1장과 6장의 논지가
# 근거를 잃는다.
REQUIRED = ['javax.el', 'BeanELResolver', '9946', '_005fset_005f141']

CHAPTERS = [
    ('intro',     '개요'),
    ('trace',     '스택트레이스는 범인이 아니다'),
    ('unknown',   '아직 원인을 모른다'),
    ('silent',    '조용한 실패'),
    ('boundary',  '신뢰 경계'),
    ('invariant', '가질 수 없게 만들기'),
    ('assembly',  '하나가 전체를 데려갔다'),
    ('swallow',   '삼킬 자격'),
    ('failfast',  '죽을 자리와 버틸 자리'),
    ('slowdown',  '느린 것이 더 위험하다'),
    ('fallback',  '빈자리에 무엇을 놓나'),
    ('specgap',   '기획서에는 정상 경로만'),
    ('questions', '물어야 할 열두 가지'),
    ('wording',   '요건 문장으로 굳히기'),
    ('process',   '팀의 절차로'),
    ('recap',     '다시 그 스택트레이스로'),
    ('ap-java',   '부록 A · 자바·스프링 대응표'),
    ('ap-jsp',    '부록 B · JSP·EL 환경'),
    ('ap-cards',  '부록 C · 질문 카드'),
]

# 사슬 규칙을 지는 장. 개요는 지도를 펼치는 자리고, 15장은 회수하는 자리며,
# 부록은 사슬 밖이다.
CHAINED = [cid for cid, _ in CHAPTERS
           if cid not in ('intro', 'recap') and not cid.startswith('ap-')]

SECTION_OPEN = re.compile(r'<section\b([^>]*)>', re.I)
STACK_OPEN = re.compile(r'<details\s+class="stack"[^>]*>', re.I)
DETAILS_TAG = re.compile(r'<(/?)details\b[^>]*>', re.I)


@pytest.fixture(scope='module')
def src():
    with open(DOC, encoding='utf-8') as fh:
        return fh.read()


def iter_sections(src):
    """<section id=...> 부터 짝이 맞는 </section> 까지를 (id, 본문) 으로 내놓는다.

    이 문서의 섹션은 중첩되지 않지만, 정규식으로 </section> 를 바로 잡으면 나중에
    누가 섹션 안에 섹션을 넣었을 때 조용히 잘린 본문을 검사하게 된다."""
    for m in SECTION_OPEN.finditer(src):
        sid = ct.ID_ATTR.search(m.group(1))
        end = src.find('</section>', m.end())
        yield (sid.group(1) if sid else None), src[m.end():end if end > 0 else len(src)]


def iter_stack_blocks(src):
    """<details class="stack"> 의 본문을 details 중첩 깊이를 세어 내놓는다."""
    for m in STACK_OPEN.finditer(src):
        pos, depth = m.end(), 1
        for dm in DETAILS_TAG.finditer(src, pos):
            depth += -1 if dm.group(1) else 1
            if depth == 0:
                yield src[pos:dm.start()]
                break


def test_the_shared_tutorial_checker_passes(src):
    problems, _ = ct.check(DOC)
    assert problems == [], '\n'.join(problems)


def test_no_internal_identifier_survived_the_paraphrase(src):
    low = src.lower()
    leaked = [w for w in FORBIDDEN if w.lower() in low]
    assert leaked == [], (
        '사내 식별자가 남았다: %s. 설계 문서 3절의 각색 규칙을 보라.' % leaked)


def test_the_evidence_the_paraphrase_must_keep_is_still_there(src):
    missing = [w for w in REQUIRED if w not in src]
    assert missing == [], (
        '각색하다가 증거를 지웠다: %s. 이 값들은 1장과 6장의 논지가 서 있는 자리다.'
        % missing)


def test_the_chapter_spine_matches_the_plan(src):
    found = []
    for attrs in SECTION_OPEN.findall(src):
        sid = ct.ID_ATTR.search(attrs)
        title = ct.DATA_TITLE.search(attrs)
        found.append((sid.group(1) if sid else None,
                      title.group(1) if title else None))
    assert found == CHAPTERS


def test_every_chained_chapter_ends_with_the_next_problem(src):
    bodies = dict(iter_sections(src))
    missing = [cid for cid in CHAINED
               if 'class="nextq"' not in bodies.get(cid, '')]
    assert missing == [], (
        '이 장들이 다음 문제 없이 끝난다: %s. 사슬이 끊기면 반경이 아니라 목록이 된다.'
        % missing)


def test_the_next_problem_is_the_last_thing_in_the_chapter(src):
    """.nextq 뒤에 본문이 더 있으면 '다음 문제로 끝난다'가 거짓말이 된다."""
    late = []
    for cid, body in iter_sections(src):
        if cid not in CHAINED:
            continue
        start = body.rfind('class="nextq"')
        close = body.find('</div>', start)
        rest = body[close + len('</div>'):] if close > 0 else ''
        if (re.search(r'<(?:h2|h3|p)\b', rest)
                or 'class="demo"' in rest or 'class="quiz"' in rest):
            late.append(cid)
    assert late == [], '다음 문제 뒤에 본문이 더 있다: %s' % late


def test_the_stack_parser_still_matches_the_markup(src):
    """셀렉터가 마크업과 어긋나면 아래 규칙이 통째로 증발하면서 화면에는 초록불이
    뜬다. 등장 횟수와 파서가 실제로 찾은 블록 수를 대조해 그 침묵을 막는다.
    아직 .stack 이 하나도 없는 단계에서는 0 == 0 으로 성립한다."""
    assert src.count('class="stack"') == len(list(iter_stack_blocks(src)))


def test_stack_blocks_carry_no_load_bearing_content(src):
    """.stack 을 전부 접어도 논지가 끊기지 않아야 한다(설계 문서 4절).

    그것을 기계로 재는 방법은 하나뿐이다: 논지의 뼈대를 그 안에 두지 못하게 하는 것."""
    offenders = []
    for body in iter_stack_blocks(src):
        for bad in ('<h2', '<h3', 'class="demo"', 'class="quiz"', 'class="nextq"'):
            if bad in body:
                offenders.append((bad, body[:60]))
    assert offenders == [], (
        '.stack 안에 논지의 뼈대가 있다: %s' % offenders)


def test_the_progress_key_does_not_collide_with_other_documents(src):
    assert 'defprog:' in src
    assert 'authbasic:' not in src
