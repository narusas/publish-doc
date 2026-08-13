#!/usr/bin/env python3
"""단일 HTML 튜토리얼의 구조 불변식 검사기.

표준 라이브러리만 사용한다. 이 저장소의 모든 *_tutorial.html / *_basics.html 에
공통으로 적용되는 규칙을 검사한다.

사용법:
    python3 tools/check_tutorial.py aws_network_security.html
    python3 tools/check_tutorial.py *.html
"""
import re
import sys

# --- 규칙 정의 -------------------------------------------------------------

# 리소스를 '로드'하는 태그만 본다. <a href="https://...">는 링크일 뿐이라 허용한다.
RESOURCE_LOAD = re.compile(
    r'<(?:script|img|iframe|link|source|video|audio|embed|object)\b[^>]*?'
    r'\b(?:src|href|data)\s*=\s*["\'](?:https?:)?//',
    re.I,
)
# Prism 최소화 소스에 들어 있는 `new Worker(...)`는 실제로 실행되지 않으므로 제외한다.
NET_CALL = re.compile(
    r'\b(?:fetch\s*\(|XMLHttpRequest|new\s+Image\s*\(|new\s+WebSocket|navigator\.sendBeacon)'
)
CSS_REMOTE = re.compile(r'(?:@import\s+["\']?(?:https?:)?//|url\(\s*["\']?(?:https?:)?//)', re.I)

ID_ATTR = re.compile(r'\bid\s*=\s*"([^"]+)"')
SECTION_TAG = re.compile(r'<section\b([^>]*)>', re.I)
DATA_TITLE = re.compile(r'\bdata-title\s*=\s*"([^"]*)"')
ANCHOR_HREF = re.compile(r'\bhref\s*=\s*"#([^"]+)"')
# 태그 하나를 통째로 잡은 뒤 class/data-t 속성을 순서와 무관하게 찾는다.
# (class="term" ... data-t="..." 순서를 강제하면 속성 순서가 뒤집힌 경우를 놓친다)
TAG_OPEN = re.compile(r'<[a-zA-Z][\w-]*\b[^>]*>')
CLASS_ATTR = re.compile(r'\bclass\s*=\s*"([^"]*)"')
DATA_T_ATTR = re.compile(r'\bdata-t\s*=\s*"([^"]*)"')
GLOSSARY_BLOCK = re.compile(r'const\s+GLOSSARY\s*=\s*\{(.*?)//\s*@GLOSSARY_END', re.S)
GLOSSARY_KEY = re.compile(r'"([^"]+)"\s*:')
# 여는 태그만 정규식으로 찾고, 짝이 맞는 </div>는 중첩 깊이를 세어 직접 찾는다.
# (이전 버전은 `</div>\s*</section>` 인접을 요구해서, 퀴즈 뒤에 다른 형제 요소가
#  하나라도 더 있으면 그 섹션의 퀴즈 전체를 조용히 건너뛰었다)
QUIZ_OPEN = re.compile(r'<div\s+class="quiz"([^>]*)>', re.I)
DIV_TAG = re.compile(r'<(/?)div\b[^>]*>', re.I)
DEMO_TAG = re.compile(r'class="demo"')


def find_term_keys(src):
    """class="term" 이 붙은 태그의 data-t 값을 속성 순서와 무관하게 모은다."""
    keys = []
    for m in TAG_OPEN.finditer(src):
        tag = m.group(0)
        cm = CLASS_ATTR.search(tag)
        if not cm or 'term' not in cm.group(1).split():
            continue
        dm = DATA_T_ATTR.search(tag)
        if dm:
            keys.append(dm.group(1))
    return keys


def iter_quiz_blocks(src):
    """<div class="quiz" ...>...</div> 를 </section> 인접 여부와 상관없이,
    div 중첩 깊이를 세어 짝이 맞는 닫는 태그까지 (attrs, body) 로 내놓는다."""
    for m in QUIZ_OPEN.finditer(src):
        attrs = m.group(1)
        pos = m.end()
        depth = 1
        end = None
        for dm in DIV_TAG.finditer(src, pos):
            if dm.group(1):  # </div>
                depth -= 1
                if depth == 0:
                    end = dm.start()
                    break
            else:  # <div ...>
                depth += 1
        if end is not None:
            yield attrs, src[pos:end]


def check(path, allow_missing_anchors=False):
    problems = []
    try:
        src = open(path, encoding='utf-8').read()
    except UnicodeDecodeError as e:
        return [f'[encoding] UTF-8로 읽을 수 없음: {e}'], (0, 0, 0)

    # 1. 외부 의존성
    for m in RESOURCE_LOAD.finditer(src):
        problems.append(f'[external] 외부 리소스 로드: {m.group(0)[:80]}')
    for m in NET_CALL.finditer(src):
        problems.append(f'[external] 네트워크 호출: {m.group(0)}')
    for m in CSS_REMOTE.finditer(src):
        problems.append(f'[external] CSS 원격 참조: {m.group(0)[:60]}')

    # 2. 메타
    if '<title>' not in src:
        problems.append('[meta] <title>이 없음')
    if 'name="description"' not in src:
        problems.append('[meta] meta description이 없음')

    # 3. id 유일성
    ids = ID_ATTR.findall(src)
    for i in sorted({x for x in ids if ids.count(x) > 1}):
        problems.append(f'[id] id가 중복됨: {i}')
    idset = set(ids)

    # 4. 섹션에 data-title
    sections = SECTION_TAG.findall(src)
    for attrs in sections:
        sid = ID_ATTR.search(attrs)
        if not DATA_TITLE.search(attrs):
            problems.append(f'[section] data-title 없음: id={sid.group(1) if sid else "?"}')
        if not sid:
            problems.append(f'[section] id 없음: <section{attrs[:60]}>')

    # 5. 내부 앵커 해석
    # 문서를 장별로 증분 작성하는 동안에는 목차가 아직 없는 섹션을 가리키므로
    # --allow-missing-anchors 로 이 검사만 유예할 수 있다. 나머지는 그대로 적용된다.
    if not allow_missing_anchors:
        for a in sorted(set(ANCHOR_HREF.findall(src))):
            if a not in idset:
                problems.append(f'[anchor] 가리키는 id가 없음: #{a}')

    # 6. 용어 ↔ 사전
    gm = GLOSSARY_BLOCK.search(src)
    gkeys = set(GLOSSARY_KEY.findall(gm.group(1))) if gm else set()
    term_keys = find_term_keys(src)
    if not gm and term_keys:
        problems.append('[glossary] GLOSSARY 블록(… // @GLOSSARY_END)을 찾을 수 없음')
    for t in sorted(set(term_keys)):
        if t not in gkeys:
            problems.append(f'[glossary] GLOSSARY에 없는 용어: {t}')

    # 7. 퀴즈 정합성
    qids = []
    for attrs, body in iter_quiz_blocks(src):
        qid = re.search(r'data-qid\s*=\s*"([^"]+)"', attrs)
        ans = re.search(r'data-answer\s*=\s*"([^"]+)"', attrs)
        if not qid:
            problems.append('[quiz] data-qid 없음')
            continue
        qids.append(qid.group(1))
        if not ans:
            problems.append(f'[quiz] data-answer 없음: {qid.group(1)}')
            continue
        opts = set(re.findall(r'data-opt\s*=\s*"([^"]+)"', body))
        if ans.group(1) not in opts:
            problems.append(
                f'[quiz] data-answer="{ans.group(1)}"에 해당하는 보기가 없음: {qid.group(1)} (보기: {sorted(opts)})'
            )
        if '<div class="explain">' not in body and 'class="explain"' not in body:
            problems.append(f'[quiz] 해설(.explain)이 없음: {qid.group(1)}')
    for q in sorted({x for x in qids if qids.count(x) > 1}):
        problems.append(f'[quiz] data-qid 중복: {q}')

    return problems, (len(sections), len(qids), len(DEMO_TAG.findall(src)))


def main(argv):
    allow = '--allow-missing-anchors' in argv[1:]
    paths = [a for a in argv[1:] if not a.startswith('-')]
    unknown = [a for a in argv[1:] if a.startswith('-') and a != '--allow-missing-anchors']
    if unknown:
        print(f'알 수 없는 옵션: {" ".join(unknown)}', file=sys.stderr)
        return 2
    if not paths:
        print('사용법: python3 tools/check_tutorial.py [--allow-missing-anchors] <파일...>', file=sys.stderr)
        return 2
    failed = False
    note = ' [앵커 검사 유예]' if allow else ''
    for p in paths:
        problems, (ns, nq, nd) = check(p, allow)
        if problems:
            failed = True
            print(f'FAIL {p}:')
            for msg in problems:
                print(f'  - {msg}')
        else:
            print(f'OK {p} (섹션 {ns} · 퀴즈 {nq} · 데모 {nd}){note}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
