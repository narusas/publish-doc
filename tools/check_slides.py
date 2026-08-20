#!/usr/bin/env python3
"""발표 덱(*_slides.html)의 구조 불변식 검사기.

표준 라이브러리만 사용한다. 튜토리얼용 tools/check_tutorial.py와 짝을 이룬다.

사용법:
    python3 tools/check_slides.py oauth2_slides.html
"""
import json
import re
import sys
from collections import namedtuple

# 한국어 발표 속도. 덱의 DECK:CORE:JS도 같은 값을 쓴다 — 한쪽만 고치면 계측이 어긋난다.
SPEED = 5.5          # 자/초
TOTAL_TARGET = 3120  # 52:00
TOTAL_TOL = 180      # ±3:00
SLIDE_MIN = 25       # 초
SLIDE_MAX = 110      # 초 — 넘으면 슬라이드가 아니라 문서다

SLIDES_BLOCK = re.compile(
    r'<!--\s*====\s*SLIDES\s*====\s*-->(.*?)<!--\s*====\s*/SLIDES\s*====\s*-->', re.S)
SLIDE_TAG = re.compile(r'''<section\b[^>]*\bclass\s*=\s*["'][^"']*\bslide\b[^"']*["'][^>]*>''')
ID_ATTR = re.compile(r'''\bid\s*=\s*["']([^"']+)["']''')
SCRIPT_BLOCK = re.compile(
    r'''<script\b[^>]*\bid\s*=\s*["']deck-script["'][^>]*>(.*?)</script>''', re.S)

Deck = namedtuple('Deck', 'html slides script')


def read_deck(path):
    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    block = SLIDES_BLOCK.search(html)
    if not block:
        raise ValueError('%s: SLIDES 마커 블록을 찾지 못했다' % path)
    slides = []
    for tag in SLIDE_TAG.findall(block.group(1)):
        m = ID_ATTR.search(tag)
        if not m:
            raise ValueError('%s: id 없는 .slide 가 있다 — %s' % (path, tag[:60]))
        slides.append(m.group(1))

    sb = SCRIPT_BLOCK.search(html)
    if not sb:
        raise ValueError('%s: <script id="deck-script"> 를 찾지 못했다' % path)
    script = json.loads(sb.group(1))

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


CHECKS = [check_script_present, check_slide_seconds, check_total]


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
