#!/usr/bin/env python3
"""CSS에 정의됐지만 마크업/스크립트에서 쓰이지 않는 클래스를 찾는다.

표준 라이브러리만 사용한다. 단일 HTML 튜토리얼에서 다른 문서의 컴포넌트를
복제해 올 때 딸려 오는 사장 코드를 막는 것이 목적이다.

--report 모드에서는 역방향 검사도 함께 보여준다: 마크업/스크립트가 참조하지만
CSS에 정의가 없는 클래스. 이쪽은 오탐(부모 셀렉터로만 스타일되는 클래스 등)이
나올 수 있어 항상 정보용이다 — 종료 코드에는 영향을 주지 않는다.

사용법:
    python3 tools/check_dead_css.py auth_basics.html
    python3 tools/check_dead_css.py --report *.html   # 종료 코드 0, 목록만 출력
"""
import re
import sys

# Prism 테마 블록은 제외한다. 그 토큰 클래스들은 Prism이 런타임에 붙이므로
# 소스에 나타나지 않고, 포함하면 전부 오탐이 된다.
STYLE_TAG = re.compile(r'<style([^>]*)>(.*?)</style>', re.S)
SCRIPT_TAG = re.compile(r'<script([^>]*)>(.*?)</script>', re.S)
# CSS 주석. 셀렉터를 찾기 전에 먼저 지운다 — 주석 안의 산문에 `.무엇` 같은 조각이
# 있으면 클래스 정의로 오인되기 때문이다(파이썬 3의 `\w`는 한글도 매칭한다).
# 주석에서 점을 빼는 식의 우회는 재발하므로 여기서 근본을 막는다.
CSS_COMMENT = re.compile(r'/\*.*?\*/', re.S)
# `.foo` 셀렉터. 이름 자체는 ASCII로 한정한다 — 이 저장소의 클래스는 전부 ASCII이고,
# `\w`를 그대로 두면 CSS 문자열(content: "…")에 남은 한글이 다시 섞여 들어온다.
CLASS_SELECTOR = re.compile(r'\.([a-zA-Z][A-Za-z0-9_-]*)')
CLASS_ATTR = re.compile(r'''\bclass\s*=\s*["']([^"']*)["']''')
CLASS_LIST = re.compile(r'''classList\.(?:add|remove|toggle|contains)\(\s*["']([^"']+)["']''')
# `d.className = 'g-item'` 처럼 속성이 아니라 프로퍼티 대입으로 클래스를 붙이는
# 경우. classList와 달리 여러 클래스를 공백으로 함께 넣을 수 있어 split()한다.
CLASS_NAME_ASSIGN = re.compile(r'''\.className\s*=\s*["']([^"']*)["']''')
# `el.setAttribute('class', 'foo bar')` 형태.
SET_ATTR_CLASS = re.compile(r'''setAttribute\(\s*["']class["']\s*,\s*["']([^"']*)["']\s*\)''')
# 이 저장소의 전역 헬퍼 `$`/`$$`(querySelector(All) 래퍼)에 넘긴 선택자 문자열.
# `$$('.tog', root)`처럼 markup 없이 셀렉터만으로 클래스 존재를 가정하는 코드를
# 잡으려는 것이라, 문자열 안의 `.foo` 토큰을 전부 뽑아낸다(복합 셀렉터 대응).
QUERY_ARG = re.compile(r'''(?<![\w$])\$\$?\(\s*["']([^"']*)["']''')


def analyze(src):
    styles = [m.group(2) for m in STYLE_TAG.finditer(src)
              if 'prism-theme' not in m.group(1)]
    css = CSS_COMMENT.sub(' ', '\n'.join(styles))
    rest = STYLE_TAG.sub('', src)
    # 테마 블록을 '정의'에서 빼는 것과 대칭으로, Prism 최소화 소스는 '사용'에서 뺀다.
    # 그 안의 `e.classList.add("language-"+t)` 같은 문자열 리터럴 조각이 클래스
    # 사용으로 잡혀 역방향 검사에 `.language-` 오탐을 만들기 때문이다.
    rest = SCRIPT_TAG.sub(
        lambda m: '' if 'prism' in m.group(1).lower() else m.group(0), rest)

    defined = set(CLASS_SELECTOR.findall(css))
    used = set()
    for m in CLASS_ATTR.finditer(rest):
        used.update(m.group(1).split())
    for m in CLASS_LIST.finditer(rest):
        used.add(m.group(1))
    for m in CLASS_NAME_ASSIGN.finditer(rest):
        used.update(m.group(1).split())
    for m in SET_ATTR_CLASS.finditer(rest):
        used.update(m.group(1).split())
    for m in QUERY_ARG.finditer(rest):
        used.update(CLASS_SELECTOR.findall(m.group(1)))

    dead = sorted(defined - used)
    undefined_used = sorted(used - defined)
    return dead, undefined_used, len(defined), len(used & defined)


def main(argv):
    report_only = '--report' in argv[1:]
    paths = [a for a in argv[1:] if not a.startswith('-')]
    if not paths:
        print('사용법: python3 tools/check_dead_css.py [--report] <파일...>', file=sys.stderr)
        return 2
    failed = False
    for p in paths:
        src = open(p, encoding='utf-8').read()
        dead, undefined_used, ndef, nused = analyze(src)
        if dead:
            if not report_only:
                failed = True
            print(f'{"WARN" if report_only else "FAIL"} {p}: 정의 {ndef} · 사용 {nused} · '
                  f'미사용(CSS에만 있음) {len(dead)}')
            for c in dead:
                print(f'  - .{c}')
        else:
            print(f'OK {p} (정의 {ndef} · 전부 사용됨)')

        # 역방향 검사는 --report에서만, 항상 정보용(종료 코드에 영향 없음).
        if report_only:
            if undefined_used:
                print(f'INFO {p}: 정의 없음(마크업/스크립트에만 있음) {len(undefined_used)}')
                for c in undefined_used:
                    print(f'  + .{c}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
