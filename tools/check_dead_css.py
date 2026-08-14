#!/usr/bin/env python3
"""CSS에 정의됐지만 마크업/스크립트에서 쓰이지 않는 클래스를 찾는다.

표준 라이브러리만 사용한다. 단일 HTML 튜토리얼에서 다른 문서의 컴포넌트를
복제해 올 때 딸려 오는 사장 코드를 막는 것이 목적이다.

사용법:
    python3 tools/check_dead_css.py auth_basics.html
    python3 tools/check_dead_css.py --report *.html   # 종료 코드 0, 목록만 출력
"""
import re
import sys

# Prism 테마 블록은 제외한다. 그 토큰 클래스들은 Prism이 런타임에 붙이므로
# 소스에 나타나지 않고, 포함하면 전부 오탐이 된다.
STYLE_TAG = re.compile(r'<style([^>]*)>(.*?)</style>', re.S)
CLASS_SELECTOR = re.compile(r'\.([a-zA-Z][\w-]*)')
CLASS_ATTR = re.compile(r'''\bclass\s*=\s*["']([^"']*)["']''')
CLASS_LIST = re.compile(r'''classList\.(?:add|remove|toggle|contains)\(\s*["']([^"']+)["']''')


def dead_classes(src):
    styles = [m.group(2) for m in STYLE_TAG.finditer(src)
              if 'prism-theme' not in m.group(1)]
    css = '\n'.join(styles)
    rest = STYLE_TAG.sub('', src)

    defined = set(CLASS_SELECTOR.findall(css))
    used = set()
    for m in CLASS_ATTR.finditer(rest):
        used.update(m.group(1).split())
    for m in CLASS_LIST.finditer(rest):
        used.add(m.group(1))
    return sorted(defined - used), len(defined), len(used & defined)


def main(argv):
    report_only = '--report' in argv[1:]
    paths = [a for a in argv[1:] if not a.startswith('-')]
    if not paths:
        print('사용법: python3 tools/check_dead_css.py [--report] <파일...>', file=sys.stderr)
        return 2
    failed = False
    for p in paths:
        src = open(p, encoding='utf-8').read()
        dead, ndef, nused = dead_classes(src)
        if dead:
            if not report_only:
                failed = True
            print(f'{"WARN" if report_only else "FAIL"} {p}: 정의 {ndef} · 사용 {nused} · '
                  f'미사용 {len(dead)}')
            for c in dead:
                print(f'  - .{c}')
        else:
            print(f'OK {p} (정의 {ndef} · 전부 사용됨)')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
