#!/usr/bin/env python3
"""발표 덱(*_slides.html)의 구조 불변식 검사기.

표준 라이브러리만 사용한다. 튜토리얼용 tools/check_tutorial.py와 짝을 이룬다.

사용법:
    python3 tools/check_slides.py oauth2_slides.html
"""
import json
import os
import re
import sys
from collections import namedtuple

# 외부 리소스 규칙은 튜토리얼 검사기와 같은 것을 쓴다. 복사해 두면 한쪽만 고쳐졌을 때
# 덱과 튜토리얼의 '외부 요청 없음' 기준이 조용히 갈라진다.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_tutorial as ct        # noqa: E402  (같은 tools/ 안의 표준 라이브러리 전용 모듈)

# 한국어 발표 속도. 덱의 DECK:CORE:JS도 같은 값을 쓴다 — 한쪽만 고치면 계측이 어긋난다.
SPEED = 5.5          # 자/초
TOTAL_TARGET = 3120  # 52:00
TOTAL_TOL = 180      # ±3:00
SLIDE_MIN = 25       # 초
SLIDE_MAX = 110      # 초 — 넘으면 슬라이드가 아니라 문서다

SLIDES_BLOCK = re.compile(
    r'<!--\s*====\s*SLIDES\s*====\s*-->(.*?)<!--\s*====\s*/SLIDES\s*====\s*-->', re.S)
# 태그를 통째로 잡고 class 속성을 공백으로 쪼개 본다. 정규식 안에서 \bslide\b 로
# 훑으면 하이픈이 낱말 경계라 class="slide-notes" 나 "not-slide" 까지 슬라이드로
# 세어 버린다. check_tutorial.py 의 find_term_keys 가 쓰는 방식과 같게 맞췄다.
SECTION_TAG = re.compile(r'''<section\b([^>]*)>''', re.I)
CLASS_ATTR = re.compile(r'''\bclass\s*=\s*["']([^"']*)["']''')
ID_ATTR = re.compile(r'''\bid\s*=\s*["']([^"']+)["']''')
SCRIPT_BLOCK = re.compile(
    r'''<script\b[^>]*\bid\s*=\s*["']deck-script["'][^>]*>(.*?)</script>''', re.S)
DECK_SCRIPT_OPEN = re.compile(r'''<script\b[^>]*\bid\s*=\s*["']deck-script["'][^>]*>''', re.I)
SCRIPT_OPEN_ANY = re.compile(r'<script\b', re.I)
CLOSE_SCRIPT = re.compile(r'</script', re.I)

Deck = namedtuple('Deck', 'html slides script')


def read_deck(path):
    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    block = SLIDES_BLOCK.search(html)
    if not block:
        raise ValueError('%s: SLIDES 마커 블록을 찾지 못했다' % path)
    slides = []
    for attrs in SECTION_TAG.findall(block.group(1)):
        cm = CLASS_ATTR.search(attrs)
        if not cm or 'slide' not in cm.group(1).split():
            continue
        m = ID_ATTR.search(attrs)
        if not m:
            raise ValueError('%s: id 없는 .slide 가 있다 — <section%s>' % (path, attrs[:60]))
        slides.append(m.group(1))

    sb = SCRIPT_BLOCK.search(html)
    if not sb:
        raise ValueError('%s: <script id="deck-script"> 를 찾지 못했다' % path)
    try:
        script = json.loads(sb.group(1))
    except ValueError as e:
        # 대본에 </script> 가 들어가면 여기서 JSON 이 잘린 채로 온다. 원인을 같이 적어 준다.
        raise ValueError('%s: deck-script 의 JSON 을 읽지 못했다 — %s. '
                         '대본 안에 </script 가 들어 있지 않은지 보라' % (path, e))

    return Deck(html=html, slides=slides, script=script)


def seconds(paras):
    """대본 문단 목록의 예상 소요 시간(초). 공백은 세지 않는다."""
    chars = sum(len(re.sub(r'\s', '', p)) for p in paras)
    return round(chars / SPEED, 1)


def _fmt(sec):
    sec = int(round(sec))
    return '%d:%02d' % (sec // 60, sec % 60)


def check_script_present(deck):
    problems = []
    for sid in deck.slides:
        paras = deck.script.get(sid)
        if not paras:
            problems.append('%s: 대본이 없다' % sid)
    for sid in deck.script:
        if sid not in deck.slides:
            problems.append('%s: 대본만 있고 슬라이드가 없다' % sid)
    return problems


def check_slide_seconds(deck):
    problems = []
    for sid in deck.slides:
        paras = deck.script.get(sid)
        if not paras:
            continue  # check_script_present 가 보고한다
        sec = seconds(paras)
        if sec > SLIDE_MAX:
            problems.append('%s: 대본 %s — 상한 %d초를 넘는다. 슬라이드를 쪼개라'
                            % (sid, _fmt(sec), SLIDE_MAX))
        elif sec < SLIDE_MIN:
            problems.append('%s: 대본 %s — 하한 %d초에 못 미친다. 앞뒤와 합쳐라'
                            % (sid, _fmt(sec), SLIDE_MIN))
    return problems


def check_total(deck):
    total = sum(seconds(deck.script.get(sid, [])) for sid in deck.slides)
    lo, hi = TOTAL_TARGET - TOTAL_TOL, TOTAL_TARGET + TOTAL_TOL
    if not (lo <= total <= hi):
        return ['대본 합계 %s — 목표 %s ±%s 를 벗어난다 (허용 %s~%s)'
                % (_fmt(total), _fmt(TOTAL_TARGET), _fmt(TOTAL_TOL), _fmt(lo), _fmt(hi))]
    return []


DIA_FIG = re.compile(
    r'''<figure\b[^>]*\bclass\s*=\s*["'][^"']*\bdia\b[^"']*["'][^>]*\bid\s*=\s*["']([^"']+)["'](.*?)</figure>''',
    re.S)
DATA_AT = re.compile(r'''\bdata-at\s*=\s*["']([^"']+)["']''')
WIRE_DIA = re.compile(r'''wireDia\(\s*['"](\w+)['"]\s*,\s*\[''')


def _max_at(segment):
    """data-at 이 가리키는 최대 프레임 인덱스. '3+' 나 '1-4' 같은 표기를 푼다."""
    top = -1
    for spec in DATA_AT.findall(segment):
        for part in spec.split(','):
            part = part.strip()
            if not part:
                continue
            if part.endswith('+'):
                part = part[:-1]
            if '-' in part.lstrip('-'):
                part = part.split('-')[-1]
            if part.isdigit():
                top = max(top, int(part))
    return top


def _wiredia_step_counts(html):
    """wireDia(id, [ {c:...}, ... ]) 의 단계 수를 id 별로 센다."""
    counts = {}
    for m in WIRE_DIA.finditer(html):
        i = m.end() - 1
        depth = 0
        while i < len(html):
            if html[i] == '[':
                depth += 1
            elif html[i] == ']':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        counts[m.group(1)] = len(re.findall(r'\{\s*c\s*:', html[m.end():i]))
    return counts


def check_dia_frames(deck):
    """SVG 의 data-at 최대 인덱스 + 1 과 wireDia 단계 수가 어긋나면 프레임이
    조용히 안 보이거나 빈 프레임이 생긴다. 눈에 잘 안 띄어서 검사로 잡는다."""
    problems = []
    counts = _wiredia_step_counts(deck.html)
    for fid, segment in DIA_FIG.findall(deck.html):
        frames = _max_at(segment) + 1
        steps = counts.get(fid)
        if steps is None:
            problems.append('%s: SVG 는 있는데 wireDia 호출이 없다' % fid)
        elif frames != steps:
            problems.append('%s: data-at 프레임 %d개 ≠ wireDia 단계 %d개'
                            % (fid, frames, steps))
    for fid in counts:
        if not re.search(r'''id\s*=\s*["']%s["']''' % re.escape(fid), deck.html):
            problems.append('%s: wireDia 호출은 있는데 SVG 가 없다' % fid)
    return problems


def check_no_external(deck):
    """덱도 단일 파일·외부 요청 0건이어야 한다. 발표장 네트워크는 믿을 것이 못 된다.

    check_tutorial.py 를 그대로 덱에 돌릴 수는 없다 — 그쪽은 meta description 과
    섹션마다의 data-title 까지 요구해서 덱에서는 언제나 실패하고, 슬라이드가 예순 장
    넘어가면 위반 목록이 그 잡음으로 덮인다. 규칙(정규식)만 빌려 온다."""
    problems = []
    for m in ct.RESOURCE_LOAD.finditer(deck.html):
        problems.append('외부 리소스 로드: %s' % m.group(0)[:80])
    for m in ct.NET_CALL.finditer(deck.html):
        problems.append('네트워크 호출: %s' % m.group(0))
    for m in ct.CSS_REMOTE.finditer(deck.html):
        problems.append('CSS 원격 참조: %s' % m.group(0)[:60])
    return problems


def check_script_terminator(deck):
    """대본은 <script type="application/json" id="deck-script"> 안에 있다.
    그 안에 </script 가 한 번이라도 더 나오면 HTML 파서가 거기서 요소를 끊는다.
    덱은 아무 오류 메시지 없이 통째로 죽고, 원인은 대본 한 문장 안에 숨는다.
    XSS 를 다루는 장에서 실제로 나올 수 있는 문자열이라 검사로 잡는다."""
    m = DECK_SCRIPT_OPEN.search(deck.html)
    if not m:
        return []                     # read_deck 이 이미 걸렀다
    nxt = SCRIPT_OPEN_ANY.search(deck.html, m.end())
    region = deck.html[m.end():nxt.start() if nxt else len(deck.html)]
    hits = CLOSE_SCRIPT.findall(region)
    if len(hits) != 1:
        return ['deck-script 블록 안에 </script 가 %d개 있다 — 닫는 것 하나만 있어야 한다. '
                '대본에 그 문자열이 들어가면 HTML 파서가 거기서 대본을 끊는다' % len(hits)]
    return []


CHECKS = [check_script_present, check_slide_seconds, check_total,
          check_dia_frames, check_no_external, check_script_terminator]


def main(argv):
    paths = argv[1:]
    if not paths:
        print(__doc__)
        return 2
    failed = False
    for path in paths:
        deck = read_deck(path)
        problems = []
        for check in CHECKS:
            problems.extend(check(deck))
        total = sum(seconds(deck.script.get(s, [])) for s in deck.slides)
        print('%s — 슬라이드 %d장, 대본 합계 %s' % (path, len(deck.slides), _fmt(total)))
        for p in problems:
            print('  ✗ %s' % p)
        if problems:
            failed = True
        else:
            print('  ✓ 통과')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
