# 방어적 프로그래밍 튜토리얼 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 전시 섹션 하나의 예외가 메인페이지 전체를 죽인 실제 장애를 척추로 삼아, 방어적 프로그래밍을 코드 레벨에서 설계 레벨과 요구사항 레벨까지 끌고 가는 단일 HTML 튜토리얼 `defensive_programming.html` 을 만든다.

**Architecture:** 기존 튜토리얼 8편과 같은 단일 자체완결 HTML 이다. 외부 리소스를 하나도 싣지 않고, 하나의 `<style>` 과 하나의 `<script>` 안에 CSS·용어집·데모를 전부 담는다. 열다섯 장은 반경이 넓어지는 순서(한 줄 → 함수 → 객체 → 모듈 → 프로세스 경계 → 요구사항)로 배열하고, 모든 장이 같은 장애로 돌아온다. 데모 열 개 중 셋(D1 · D4 · D6)은 **순수 함수로 만들어 `window` 에 노출**한다. 그래야 브라우저 테스트가 화면을 흉내 내지 않고 그 함수를 직접 부를 수 있다.

**Tech Stack:** 순수 HTML · CSS · ES2019 자바스크립트(빌드 없음). 검증은 파이썬 표준 라이브러리 검사기(`tools/check_tutorial.py` · `tools/check_dead_css.py`)와 pytest · playwright.

**Spec:** `docs/superpowers/specs/2026-09-07-defensive-programming-design.md`

## Global Constraints

이 절의 항목은 **모든 태스크의 요구사항에 암묵적으로 포함된다.**

- **외부 의존성 0.** `<script src>` · `<link href>` · `<img src>` 로 원격 리소스를 싣지 않고, `fetch` · `XMLHttpRequest` · `new Image()` · `new WebSocket` · `navigator.sendBeacon` 을 쓰지 않는다. `tools/check_tutorial.py` 가 강제한다.
- **각색 규칙(설계 문서 3절).** 다음 문자열은 문서에 **하나도** 나타나면 안 된다: `cheil` · `ssfshop` · `dspCnr` · `ConttImg` · `includeMultiMainContents` · `SecureValueExpression` · `전시코너` · `전시 코너`. 도메인 어휘는 **"전시 섹션"** 으로 통일한다. 반대로 `javax.el` · `org.apache.jasper` · `org.apache.el` · `BeanELResolver` · 줄 번호 `9946` · `_005fset_005f141` 은 **그대로 쓴다.**
- **원인은 아직 규명되지 않았다.** 그 값이 **왜** 문자열이 되었는지도, 그 문자열이 **무엇이었는지도** 단정해서 쓰지 않는다. 스택트레이스가 보증하는 범위는 타입까지다. 2장 전체가 "우리는 아직 모른다"는 사실 위에 서 있으므로, 앞 장에서 내용을 아는 것처럼 쓰면 다음 장이 자기 앞 장과 모순된다. 4장은 전형적인 세 경로를 **가설로** 나란히 놓을 뿐 하나를 고르지 않는다.
  **데모가 화면에 찍는 문자열도 산문이다.** 데모는 구체적인 섹션 이름·값·발원지를 보여 주어야 쓸모가 있는데, 그것들은 전부 시뮬레이션의 가정이지 오늘 장애의 사실이 아니다. 그래서 데모를 감싸는 본문이 그 가정을 명시해야 하고, 데모가 스스로 출력하는 판정문도 실제 장애를 가리키는 자리에서는 발원지를 단정하면 안 된다. 2장이 데모 앞에 둔 **"이 다섯 가지 맥락이 있었다고 가정하고"** 가 이 규칙을 지킨 본보기다.
- **사슬 규칙.** 1장부터 14장까지 모든 장은 `<div class="nextq">…</div>` 하나로 끝난다. 그 안에 다음 장이 푸는 문제를 한 문장으로 적는다. 개요·15장·부록은 예외다.
- **`.stack` 규칙.** 스프링과 라이브러리 이름은 `<details class="stack">` 안에만 둔다. 그 블록 안에 `<h2>` · `<h3>` · `.demo` · `.quiz` · `.nextq` 를 넣지 않는다. 블록을 전부 접어도 논지가 끊기지 않아야 한다.
  **블록 안의 모든 문장은 본문이 이미 세운 개념에 이름을 붙이는 문장이어야 한다.** 블록에서 처음 등장하는 개념이 있으면 위반이다. 그것은 본문으로 옮기거나 지운다. 판별법은 하나다: 그 문장을 지웠을 때 독자가 잃는 것이 **이름**인가 **이해**인가. 이해를 잃으면 그 문장은 본문의 것이다. 기계 검사는 이것을 잡지 못하므로 사람이 본다.
- **난이도 표시.** 장 제목 끝에 `<span class="lvl">🟢</span>` 또는 `<span class="lvl">🔵</span>` 를 단다.
- **저장소 키 접두사**는 `defprog:` 다. (`auth_basics.html` 은 `authbasic:` 을 쓴다. 겹치면 진행률이 섞인다.)
- **컴포넌트의 CSS 는 그 컴포넌트가 처음 등장하는 태스크가 함께 넣는다.** `tools/check_dead_css.py` 가 마크업·스크립트에서 쓰이지 않는 CSS 정의를 실패로 잡으므로, 나중에 쓸 CSS 를 미리 넣어 둘 수 없다. `.demo`·`.picker`·`.stack` 처럼 이 저장소의 다른 문서에 이미 있는 컴포넌트는 `auth_basics.html` 에서 규칙을 그대로 이식한다.
- **모든 `<section>`** 에 `id` 와 `data-title` 이 있어야 한다. `class="term" data-t="X"` 의 `X` 는 전부 `GLOSSARY` 에 있어야 한다.
- **커밋은 매 태스크 끝에 한 번.** 커밋 메시지는 한국어로, 무엇을 왜 했는지 적는다.

---

## 파일 구조

| 파일 | 상태 | 책임 |
|---|---|---|
| `defensive_programming.html` | 신규 | 문서 전체. 껍데기 · 15장 · 부록 3 · 데모 10 · 용어집 · 퀴즈 |
| `tools/test_defensive_document.py` | 신규 | 이 문서에만 있는 세 계약을 강제한다. 각색 규칙 · 사슬 규칙 · `.stack` 규칙 |
| `tools/test_defensive_behavior.py` | 신규 | 순수 함수로 노출한 데모 엔진(`EL` · `Pipeline` · `Assembly`)을 브라우저에서 직접 호출해 검사한다 |
| `index.html` | 수정 | 아홉 번째 카드 추가 |

`tools/check_tutorial.py` 는 **고치지 않는다.** 그 파일은 8편 전부에 공통으로 적용되는 규칙만 들고 있어야 하고, 이 문서에만 필요한 규칙을 거기 넣으면 다른 문서가 이유 없이 그 규칙을 지고 간다.

### 장 목록 (id 와 사이드바 제목)

| # | id | data-title | 난이도 |
|---|---|---|---|
| — | `intro` | 개요 | — |
| 1 | `trace` | 스택트레이스는 범인이 아니다 | 🟢 |
| 2 | `unknown` | 아직 원인을 모른다 | 🟢 |
| 3 | `silent` | 조용한 실패 | 🟢 |
| 4 | `boundary` | 신뢰 경계 | 🟢 |
| 5 | `invariant` | 가질 수 없게 만들기 | 🔵 |
| 6 | `assembly` | 하나가 전체를 데려갔다 | 🟢 |
| 7 | `swallow` | 삼킬 자격 | 🟢 |
| 8 | `failfast` | 죽을 자리와 버틸 자리 | 🟢 |
| 9 | `slowdown` | 느린 것이 더 위험하다 | 🔵 |
| 10 | `fallback` | 빈자리에 무엇을 놓나 | 🟢 |
| 11 | `specgap` | 기획서에는 정상 경로만 | 🟢 |
| 12 | `questions` | 물어야 할 열두 가지 | 🟢 |
| 13 | `wording` | 요건 문장으로 굳히기 | 🟢 |
| 14 | `process` | 팀의 절차로 | 🔵 |
| 15 | `recap` | 다시 그 스택트레이스로 | 🟢 |
| A | `ap-java` | 부록 A · 자바·스프링 대응표 | — |
| B | `ap-jsp` | 부록 B · JSP·EL 환경 | — |
| C | `ap-cards` | 부록 C · 질문 카드 | — |

---

### Task 1: 껍데기와 열여덟 개의 빈 섹션, 그리고 문서 규약 검사기

**Files:**
- Create: `defensive_programming.html`
- Create: `tools/test_defensive_document.py`

**Interfaces:**
- Consumes: `auth_basics.html` 의 껍데기(CSS 변수 · `#sidebar` · `#toc` 자동 생성 · `#progBar` · 용어 툴팁 · 용어집 서랍 · 퀴즈 채점 · `wirePicker` · `wireTogs` · Prism)
- Produces: 전역 헬퍼 `$(sel, root)` · `$$(sel, root)` · `Store.get(k,d)` · `Store.set(k,v)` · `wirePicker(sel, onPick)` · `wireTogs(sel, onChange)`. 이후 모든 태스크가 이 넷을 쓴다. 섹션 id 열여덟 개(위 표)도 이 태스크가 확정한다.

- [ ] **Step 1: 문서 규약 검사기를 먼저 쓴다 (실패하는 테스트)**

`tools/test_defensive_document.py` 를 만든다.

```python
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
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m pytest tools/test_defensive_document.py -v`
Expected: 전부 FAIL 또는 ERROR. `defensive_programming.html` 이 없으므로 `FileNotFoundError` 가 난다.

- [ ] **Step 3: 껍데기를 이식한다**

`auth_basics.html` 을 복사해서 시작한다. 새로 쓰지 않는다.

```bash
cp auth_basics.html defensive_programming.html
```

그다음 다음을 지운다. **본문 섹션 전부**(`<section id="stateless">` 부터 마지막 부록까지), **auth 전용 데모 JS 전부**(`wireDia` 호출부와 각 데모의 IIFE), **auth 전용 `GLOSSARY` 항목 전부**, **auth 전용 CSS 중 남지 않는 컴포넌트**.

**자바스크립트는 전부 남긴다**: Prism 블록 · 전역 헬퍼(`$` · `$$` · `LS` · `esc`) · 목차 자동 생성 · `loadKeys` · `markVisited` · `updateProgress` · 스크롤 스파이 · `.term` 툴팁 · `.quiz` 채점 · 용어집 서랍 · `wirePicker` · `wireTogs`. 이 중 `LS` 는 **`Store` 로 이름을 바꾼다** — 이 계획의 나머지 태스크가 전부 `Store` 로 부른다.

**CSS 는 이 태스크의 마크업이 실제로 쓰는 것만 남긴다**: `:root` 변수 · 레이아웃 · `#sidebar` · `#toc` · `#progBar` · `.term` · `.quiz` 계열 · `.hero` · `.lead` · `.kicker` · `.map-grid` · `.map-card` · `.lvl` · `.dim`. `.demo` · `.picker` · `.pick` · `.verdict` · `.kv` · `.oneline` 처럼 **이 태스크에 아직 마크업이 없는 컴포넌트의 CSS 는 지운다.** 전역 제약대로 그 CSS 는 해당 컴포넌트가 처음 등장하는 태스크(3번 태스크)가 가져온다. Step 8 의 `check_dead_css.py` 가 이것을 강제한다.

`<head>` 를 바꾼다.

```html
<title>방어적 프로그래밍 — 하나가 죽었을 때 전체가 죽지 않게</title>
<meta name="description" content="전시 섹션 하나의 예외가 메인페이지 전체를 죽인 장애에서 출발해, 방어를 코드 습관이 아니라 설계 결정으로 다루는 인터랙티브 튜토리얼. 신뢰 경계·불변식·실패 격리·타임아웃, 그리고 방어를 요구사항으로 만드는 방법까지.">
```

저장소 접두사를 바꾼다.

```js
const Store = {
  get(k, d){ try{ return JSON.parse(localStorage.getItem("defprog:"+k)) ?? d; }catch(e){ return d; } },
  set(k, v){ try{ localStorage.setItem("defprog:"+k, JSON.stringify(v)); }catch(e){} }
};
```

`resetBtn` 핸들러의 접두사도 함께 바꾼다.

```js
['visited','solved','ckl'].forEach(k => localStorage.removeItem('defprog:'+k));
```

- [ ] **Step 4: 사슬 규칙과 `.stack` 의 CSS 를 더한다**

`<style>` 끝에 붙인다.

```css
/* 장을 닫는 '다음 문제'. 사슬 규칙(설계 문서 6절)이 화면에서도 보이게 한다. */
.nextq{
  margin:26px 0 0; padding:14px 18px; border-left:3px solid var(--accent);
  background:linear-gradient(90deg, rgba(45,212,191,.09), transparent 70%);
  border-radius:0 10px 10px 0; color:var(--text-dim); font-size:15.5px;
}
.nextq b{color:var(--text)}
.nextq::before{
  content:"다음 문제"; display:block; font-family:var(--mono); font-size:11px;
  letter-spacing:1.2px; text-transform:uppercase; color:var(--accent); margin-bottom:5px;
}

```

`.stack` 의 CSS 는 **여기서 넣지 않는다.** 이 태스크에는 `.stack` 마크업이 아직 하나도 없어서 Step 8 의 `check_dead_css.py` 가 죽은 CSS 로 잡는다. 첫 `.stack` 이 등장하는 4번 태스크(2장)가 가져온다.

다만 마크업 형태는 여기서 확정한다. `.stack` 은 `<details class="stack">` 로 쓴다. 접을 수 있어야 "접어도 논지가 끊기지 않는다"는 기준을 독자가 직접 확인할 수 있고, `tools/test_defensive_document.py` 의 `iter_stack_blocks` 도 `<details>` 를 찾는다.

- [ ] **Step 5: 개요와 빈 섹션 열여덟 개를 넣는다**

`<main id="content">` 안에 위 장 목록 순서 그대로 넣는다. 본문은 아직 제목과 `.nextq` 만 있어도 된다.

```html
<section id="intro" data-title="개요" class="hero">
  <h1>하나가 죽었을 때<br><span class="g">전체가 죽지 않게</span></h1>
  <p class="lead">오늘 메인페이지가 통째로 오류를 냈습니다. 로그에는 이 스택트레이스가 남았습니다.</p>

  <pre class="trace"><code>javax.el.PropertyNotFoundException:
    Property [bannerImageList] not found on type [java.lang.String]
    at javax.el.BeanELResolver$BeanProperties.get(BeanELResolver.java:253)
    at javax.el.BeanELResolver.property(BeanELResolver.java:322)
    at javax.el.BeanELResolver.getValue(BeanELResolver.java:93)
    at org.apache.jasper.el.JasperELResolver.getValue(JasperELResolver.java:123)
    at org.apache.el.parser.AstValue.getValue(AstValue.java:160)
    at org.apache.el.ValueExpressionImpl.getValue(ValueExpressionImpl.java:149)
    at org.apache.jasper.runtime.PageContextImpl.proprietaryEvaluate(PageContextImpl.java:655)
    at org.apache.jsp...mainSections_jsp._jspx_meth_c_005fset_005f141(mainSections_jsp.java:9946)
    at org.apache.jsp...mainSections_jsp._jspx_meth_c_005fif_005f43(mainSections_jsp.java:9832)
    at org.apache.jsp...mainSections_jsp._jspService(mainSections_jsp.java:743)</code></pre>

  <p class="lead"><b>이 안에 범인이 있을까요.</b> 없습니다. 이 문서는 그 사실에서 출발합니다.</p>

  <div class="map-grid" id="radiusMap"><!-- Step 6 --></div>
</section>

<section id="trace" data-title="스택트레이스는 범인이 아니다">
  <div class="sec-head"><span class="kicker">1장</span></div>
  <h2>🧨 스택트레이스가 가리키는 곳은 범인이 아니다 <span class="lvl">🟢</span></h2>
  <div class="nextq">그러면 그 값은 어디에서 문자열이 되었을까요. <b>그런데 우리는 아직 그것을 모릅니다.</b></div>
</section>
```

나머지 열일곱 개도 같은 모양으로 넣는다. `.nextq` 문구는 각 태스크에서 확정하되, 이 단계에서는 장 목록 표의 다음 장 제목을 한 문장으로 바꾼 임시 문구를 넣어 검사기를 통과시킨다.

`<pre class="trace">` 의 CSS 를 더한다.

```css
.trace{
  margin:20px 0; padding:16px 18px; border-radius:12px; overflow-x:auto;
  background:#0a0f18; border:1px solid var(--border);
  font-family:var(--mono); font-size:12.5px; line-height:1.85; color:var(--text-dim);
}
.trace code{color:inherit; background:none; border:0; padding:0}
```

- [ ] **Step 6: 반경 지도를 그린다**

`#radiusMap` 을 여섯 칸으로 채운다. 각 칸은 반경 하나이고, "이 층에서 막을 수 있었던 것"과 "그래도 남는 구멍"을 한 줄씩 담는다. 15장이 같은 데이터로 회수하므로 **배열 하나에서 그린다.**

```js
// ==== 반경 지도 — 개요와 15장이 같은 배열에서 그린다 ====
const RADIUS = [
  {n:'한 줄',        ch:'1·2·3', can:'그 값이 이상하다는 것을 그 자리에서 알린다',
                     hole:'알려도 그 섹션은 여전히 빈 화면이다'},
  {n:'한 함수',      ch:'4',     can:'경계에서 한 번 검사해 안쪽을 신뢰할 수 있게 만든다',
                     hole:'검사를 통과한 뒤에도 객체가 이상해질 수 있다'},
  {n:'한 객체',      ch:'5',     can:'그런 상태를 애초에 가질 수 없게 만든다',
                     hole:'객체가 옳아도 조립이 틀릴 수 있다'},
  {n:'한 모듈',      ch:'6·7·8', can:'실패를 섹션 경계에서 멈춰 세운다',
                     hole:'죽지 않고 느려지면 이 방어는 통하지 않는다'},
  {n:'프로세스 경계',ch:'9·10',  can:'느린 의존을 끊고 그 자리를 대신 채운다',
                     hole:'무엇으로 채울지는 여전히 정해져 있지 않다'},
  {n:'요구사항',     ch:'11~14', can:'무엇을 보여 줄지 문서에 문장으로 남긴다',
                     hole:'여기가 종착지다'},
];

function paintRadius(root, withHoles){
  root.innerHTML = RADIUS.map((r, i) => `
    <div class="map-card">
      <div class="top"><span class="no">반경 ${i+1}</span><b>${r.n}</b><span class="dim">${r.ch}장</span></div>
      <p>${r.can}</p>
      ${withHoles ? `<p class="hole">↳ ${r.hole}</p>` : ''}
    </div>`).join('');
}
paintRadius($('#radiusMap'), false);
```

`.hole` CSS 를 더한다.

```css
.map-card .hole{color:var(--text-mut); font-size:13.5px; margin-top:6px}
.map-card .top .dim{margin-left:auto; font-family:var(--mono); font-size:11.5px; color:var(--text-mut)}
```

- [ ] **Step 7: 검사기를 돌려 통과를 확인한다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py -v
```
Expected: `check_tutorial.py` 는 `OK`, pytest 는 전부 PASS.

`[glossary] GLOSSARY에 없는 용어` 가 뜨면 이식 과정에서 남은 `.term` 이 있다는 뜻이다. 지우거나 용어집에 넣는다.

- [ ] **Step 8: 죽은 CSS 를 확인한다**

Run: `python3 tools/check_dead_css.py defensive_programming.html`
Expected: 이식 직후에는 auth 전용 컴포넌트의 CSS 가 다수 남아 있다. **전부 지운다.** 이 문서에서 쓸 것만 남긴다. 다시 돌려 통과할 때까지 반복한다.

- [ ] **Step 9: 커밋**

```bash
git add defensive_programming.html tools/test_defensive_document.py
git commit -m "방어적 프로그래밍: 껍데기와 열여덟 섹션, 그리고 세 계약을 지키는 검사기

각색 규칙·사슬 규칙·.stack 규칙은 눈으로 보면 통과라고 말하기 쉬워서
tools/test_defensive_document.py 가 기계로 잡는다. check_tutorial.py 는
8편 공통 규칙만 들고 있어야 하므로 건드리지 않았다."
```

---

### Task 2: D6 메인 조립 시뮬레이터 엔진

세 장(6 · 9 · 10)이 같은 데모로 돌아온다. 엔진이 흔들리면 세 장이 함께 흔들리므로 **화면보다 먼저 엔진을 완성한다.**

**Files:**
- Modify: `defensive_programming.html` (`<script>` 안, 데모 구역)
- Create: `tools/test_defensive_behavior.py`

**Interfaces:**
- Consumes: 없음. 이 엔진은 순수 함수다.
- Produces: `window.Assembly` 에 다음을 노출한다.
  - `Assembly.SECTIONS` — `[{id, name, critical}]` 여덟 개
  - `Assembly.DEFAULT_STRATEGY` — `{isolate, timeoutMs, bulkhead, breaker, fallback}`
  - `Assembly.assemble(faults, strategy)` → `{rendered:[{id,name,state,ms}], pageState:'ok'|'partial'|'error', totalMs:number, failedAt:string|null}`
  - `state` 의 값은 `'ok'` · `'empty'` · `'slow'` · `'hide'` · `'cache'` · `'skeleton'` · `'blank'` · `'open'` 중 하나다.
  - 8장의 D8, 10장의 폴백 비교, 9장의 격벽 실험이 전부 이 함수를 부른다.

- [ ] **Step 1: 엔진 테스트를 먼저 쓴다**

`tools/test_defensive_behavior.py` 를 만든다.

```python
#!/usr/bin/env python3
"""데모 엔진의 동작 테스트. 브라우저가 없으면 skip 하지 않고 실패한다.

이 문서의 데모 셋(EL · Pipeline · Assembly)은 화면이 아니라 순수 함수다. 화면을
클릭해서 검사하면 무엇이 깨졌는지 알 수 없지만, 함수를 직접 부르면 알 수 있다.
그래서 셋 다 window 에 노출되어 있고 여기서 그 함수를 부른다.

특히 Assembly 는 6·9·10 세 장이 공유한다. 여기가 물러서면 세 장의 논지가 동시에
근거를 잃으므로, 브라우저가 없을 때 skip 하지 않는다. 고치는 법은 한 줄이다:

    python3 -m playwright install chromium

사용법: python3 -m pytest tools/test_defensive_behavior.py -v
"""
import os

import pytest

try:
    from playwright import sync_api as playwright_api
except ImportError as exc:                    # pragma: no cover - 설치 안 된 기계
    playwright_api = None
    IMPORT_ERROR = exc

NO_BROWSER = ('데모 엔진 테스트는 브라우저를 요구한다 — %s.\n'
              '6·9·10장이 공유하는 Assembly 를 강제하는 곳이 여기뿐이라 skip 하지 않는다.\n'
              '설치: python3 -m playwright install chromium')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = 'file://' + os.path.join(ROOT, 'defensive_programming.html')


@pytest.fixture(scope='module')
def page():
    if playwright_api is None:
        pytest.fail(NO_BROWSER % IMPORT_ERROR)
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:              # pragma: no cover - 브라우저 미설치
            pytest.fail(NO_BROWSER % exc)
        pg = browser.new_page()
        pg.goto(DOC)
        yield pg
        browser.close()


def assemble(page, faults, **strategy):
    """Assembly.assemble 을 기본 전략 위에 덮어써서 부른다."""
    return page.evaluate(
        '([f, s]) => Assembly.assemble(f, Object.assign({}, Assembly.DEFAULT_STRATEGY, s))',
        [faults, strategy])


def test_the_engine_is_exposed(page):
    assert page.evaluate('typeof Assembly.assemble') == 'function'
    assert page.evaluate('Assembly.SECTIONS.length') == 8


def test_a_healthy_page_renders_every_section(page):
    r = assemble(page, {})
    assert r['pageState'] == 'ok'
    assert [s['state'] for s in r['rendered']] == ['ok'] * 8


def test_one_broken_section_takes_the_whole_page_when_nothing_isolates(page):
    """오늘 일어난 일 그대로다. 이 테스트가 6장의 논지다."""
    r = assemble(page, {'best': 'throw'}, isolate=False)
    assert r['pageState'] == 'error'
    assert r['failedAt'] == 'best'
    assert len(r['rendered']) < 8


def test_isolation_keeps_the_page_and_leaves_one_hole(page):
    r = assemble(page, {'best': 'throw'}, isolate=True, fallback='hide')
    assert r['pageState'] == 'partial'
    assert len(r['rendered']) == 8
    assert [s for s in r['rendered'] if s['id'] == 'best'][0]['state'] == 'hide'


def test_a_critical_section_takes_the_page_down_even_with_isolation(page):
    """열두 질문 중 여섯 번째의 코드판이다. 없으면 화면을 띄우면 안 되는 부분이 있다."""
    r = assemble(page, {'hero': 'throw'}, isolate=True, fallback='hide')
    assert r['pageState'] == 'error'
    assert r['failedAt'] == 'hero'


def test_an_empty_section_is_not_a_failure(page):
    """빈 것과 깨진 것은 다르다. 3장의 비대칭이 여기서도 성립해야 한다."""
    r = assemble(page, {'reco': 'empty'}, isolate=False)
    assert r['pageState'] == 'ok'
    assert [s for s in r['rendered'] if s['id'] == 'reco'][0]['state'] == 'empty'


def test_a_slow_section_without_a_timeout_costs_the_whole_page_its_time(page):
    r = assemble(page, {'reco': 'slow'}, timeoutMs=None, bulkhead=False)
    assert r['totalMs'] >= 3000


def test_a_timeout_caps_what_one_slow_section_can_cost(page):
    r = assemble(page, {'reco': 'slow'}, timeoutMs=300, bulkhead=False, isolate=True)
    assert r['totalMs'] < 1000


def test_a_bulkhead_stops_one_slow_section_from_adding_to_everyone(page):
    serial = assemble(page, {'reco': 'slow'}, timeoutMs=None, bulkhead=False)
    walled = assemble(page, {'reco': 'slow'}, timeoutMs=None, bulkhead=True)
    assert walled['totalMs'] < serial['totalMs']


def test_an_open_breaker_still_cannot_skip_a_critical_section(page):
    """회로가 열려도 없으면 안 되는 자리를 건너뛰면 페이지는 성립하지 않는다.

    푸터에는 사업자 정보가 실린다. 그것이 빠진 상거래 페이지는 띄우면 안 된다.
    회로를 섹션마다 걸지 않고 하나로 걸면 이 일이 조용히 일어난다 — 화면은
    '일부만 비었다'고 말하는데 실제로는 띄우면 안 되는 페이지가 나간다."""
    r = assemble(page, {'best': 'throw', 'new': 'throw'},
                 isolate=True, breaker=True, fallback='cache')
    assert r['pageState'] == 'error'
    assert r['failedAt'] == 'footer'


def test_the_breaker_stops_calling_after_repeated_failures(page):
    r = assemble(page, {'best': 'throw', 'new': 'throw', 'brand': 'throw'},
                 isolate=True, breaker=True, fallback='cache')
    states = {s['id']: s['state'] for s in r['rendered']}
    assert states['brand'] == 'open'
    assert [s for s in r['rendered'] if s['id'] == 'brand'][0]['ms'] == 0
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m pytest tools/test_defensive_behavior.py -v`
Expected: FAIL. `typeof Assembly.assemble` 이 `"undefined"` 다.

브라우저가 없다는 실패가 나면 먼저 설치한다: `python3 -m playwright install chromium`.

- [ ] **Step 3: 엔진을 구현한다**

`<script>` 안 데모 구역에 넣는다.

```js
/* ==== D6 · 메인 조립 시뮬레이터 엔진 ==============================
   6·9·10장이 같은 함수를 부른다. 화면이 아니라 순수 함수로 둔 이유는
   tools/test_defensive_behavior.py 가 이 함수를 직접 부르기 때문이다.
   ================================================================== */
const Assembly = (() => {
  // critical 은 '없으면 화면을 띄우면 안 되는 자리'다. 12장의 여섯 번째 질문이
  // 실제로 정하는 값이며, 개발자가 혼자 정할 수 없는 값이기도 하다.
  // 푸터가 여기 들어가는 이유가 그 점을 잘 보여 준다. 디자인 요소라서가 아니라
  // 사업자 정보와 통신판매업 신고번호가 거기 실리기 때문이다. 그것이 빠진 상거래
  // 페이지는 띄우면 안 된다. 개발자가 코드만 보고 정할 수 있는 값이 아니다.
  const SECTIONS = [
    {id:'hero',   name:'메인 배너',   critical:true },
    {id:'quick',  name:'퀵 메뉴',     critical:false},
    {id:'best',   name:'베스트 상품', critical:false},
    {id:'new',    name:'신상품',      critical:false},
    {id:'brand',  name:'브랜드 위크', critical:false},
    {id:'reco',   name:'추천 상품',   critical:false},
    {id:'event',  name:'이벤트 배너', critical:false},
    {id:'footer', name:'푸터',        critical:true },
  ];

  const OK_MS   = 40;    // 정상 응답
  const SLOW_MS = 3000;  // 느려진 의존이 실제로 무는 시간
  const BREAKER_THRESHOLD = 2;  // 이만큼 실패하면 다음부터는 부르지 않는다

  const DEFAULT_STRATEGY = {
    isolate: false,      // 섹션 경계에서 실패를 멈추는가
    timeoutMs: null,     // 기다림의 상한 (null 이면 끝까지 기다린다)
    bulkhead: false,     // 섹션마다 자기 몫의 자원을 쓰는가
    breaker: false,      // 반복 실패한 의존을 잠시 끊는가
    fallback: 'none',    // 'none' | 'hide' | 'cache' | 'skeleton'
  };

  function assemble(faults, st){
    faults = faults || {};
    st = Object.assign({}, DEFAULT_STRATEGY, st || {});

    const rendered = [];
    let totalMs = 0, failures = 0, open = false;

    for(const s of SECTIONS){
      if(open && st.breaker){
        // 회로가 열렸으면 부르지 않는다. 부르지 않았으므로 시간도 들지 않는다.
        // 다만 없으면 안 되는 자리까지 끊으면 페이지는 여전히 성립하지 않는다.
        // 회로를 섹션마다 걸지 않고 하나로 걸었을 때 실제로 나는 사고이며,
        // 9장이 이 자리를 그대로 쓴다.
        if(s.critical){
          return {rendered, pageState:'error', totalMs, failedAt:s.id};
        }
        rendered.push({id:s.id, name:s.name, state:'open', ms:0});
        continue;
      }

      const fault = faults[s.id] || 'ok';
      let ms = OK_MS, state = 'ok';

      if(fault === 'slow'){
        ms = st.timeoutMs === null ? SLOW_MS : Math.min(SLOW_MS, st.timeoutMs);
        state = st.timeoutMs === null ? 'slow' : 'timeout';
      }else if(fault === 'throw'){
        state = 'throw';
      }else if(fault === 'empty'){
        // 빈 것은 실패가 아니다. 3장의 비대칭이 여기서도 성립한다.
        state = 'empty';
      }

      // 격벽이 없으면 한 섹션의 시간이 다음 섹션의 시간에 그대로 더해진다.
      // 격벽이 있으면 섹션들이 자기 몫으로 나란히 도므로 가장 느린 하나가 값이다.
      totalMs = st.bulkhead ? Math.max(totalMs, ms) : totalMs + ms;

      if(state === 'throw' || state === 'timeout'){
        failures++;
        // 없으면 안 되는 자리이거나, 멈춰 세울 경계가 없으면 페이지가 죽는다.
        // 오늘 일어난 일이 뒤쪽 경우다.
        if(s.critical || !st.isolate){
          return {rendered, pageState:'error', totalMs, failedAt:s.id};
        }
        state = st.fallback === 'none' ? 'blank' : st.fallback;
        if(failures >= BREAKER_THRESHOLD) open = true;
      }

      rendered.push({id:s.id, name:s.name, state, ms});
    }

    return {rendered, pageState: failures ? 'partial' : 'ok', totalMs, failedAt:null};
  }

  return {SECTIONS, DEFAULT_STRATEGY, assemble};
})();
window.Assembly = Assembly;
```

- [ ] **Step 4: 테스트를 돌려 통과를 확인한다**

Run: `python3 -m pytest tools/test_defensive_behavior.py -v`
Expected: 열 개 전부 PASS.

`test_the_breaker_stops_calling_after_repeated_failures` 가 실패하면 임계값과 열리는 시점을 확인한다. `best` 와 `new` 가 실패한 뒤에 `brand` 차례에서 열려 있어야 한다.

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming.html tools/test_defensive_behavior.py
git commit -m "D6 조립 엔진: 화면보다 먼저 순수 함수로 세운다

6·9·10장이 같은 함수를 부르므로 엔진이 흔들리면 세 장이 함께 흔들린다.
window.Assembly 로 노출해 브라우저 테스트가 화면을 흉내 내지 않고 함수를
직접 부르게 했다. critical 섹션이 격리를 뚫고 페이지를 죽이는 규칙이
12장 여섯 번째 질문의 코드판이다."
```

---

### Task 3: 1장 · 스택트레이스가 가리키는 곳은 범인이 아니다 (D1 · EL 리졸버 시뮬레이터)

**Files:**
- Modify: `defensive_programming.html` (`#trace` 섹션, `<script>` 데모 구역)
- Modify: `tools/test_defensive_behavior.py` (EL 엔진 테스트 추가)

**Interfaces:**
- Consumes: `wirePicker(sel, onPick)` (Task 1)
- Produces: `window.EL` — `EL.VALUES` (다섯 후보) · `EL.resolve(kind, prop)` → `{result:'value'|'empty'|'throw', text}`. 3장이 이 함수를 다시 쓴다.

- [ ] **Step 1: EL 엔진 테스트를 쓴다**

`tools/test_defensive_behavior.py` 끝에 붙인다.

```python
def el(page, kind, prop='bannerImageList'):
    return page.evaluate('([k, p]) => EL.resolve(k, p)', [kind, prop])


def test_a_dto_with_the_getter_resolves(page):
    assert el(page, 'dto')['result'] == 'value'


def test_a_map_with_the_key_resolves(page):
    """MapELResolver 가 BeanELResolver 보다 먼저 도므로 키만 있으면 통과한다.
    통과한다는 것이 문제다 — 타입은 이 자리에서 이미 사라졌다."""
    assert el(page, 'map')['result'] == 'value'


def test_null_resolves_to_nothing_and_says_nothing(page):
    """EL 은 null 을 빈 문자열로 렌더한다. 조용한 쪽이 더 위험하다는 3장의 근거다."""
    assert el(page, 'null')['result'] == 'empty'


def test_a_string_throws_because_it_has_no_such_getter(page):
    """오늘 난 예외 그 자체다."""
    r = el(page, 'string')
    assert r['result'] == 'throw'
    assert 'PropertyNotFoundException' in r['text']
    assert 'java.lang.String' in r['text']


def test_an_empty_list_throws_too(page):
    """리스트에 정수가 아닌 프로퍼티를 물으면 결국 BeanELResolver 로 떨어진다."""
    assert el(page, 'list')['result'] == 'throw'
```

- [ ] **Step 2: 테스트를 돌려 실패를 확인한다**

Run: `python3 -m pytest tools/test_defensive_behavior.py -k "resolves or throws" -v`
Expected: FAIL — `EL is not defined`.

- [ ] **Step 3: EL 엔진을 구현한다**

```js
/* ==== D1 · EL 리졸버 시뮬레이터 ====================================
   ${section.bannerImageList} 를 평가할 때 section 에 무엇이 들어 있느냐에 따라
   EL 이 무엇을 하는지. 3장이 이 함수의 비대칭을 다시 쓴다.
   ================================================================== */
const EL = (() => {
  const VALUES = [
    {k:'dto',    label:'SectionVO 객체',      hint:'getBannerImageList() 가 있다'},
    {k:'map',    label:'Map (키 있음)',       hint:'MapELResolver 가 먼저 돈다'},
    {k:'null',   label:'null',                hint:'값이 아예 없다'},
    {k:'string', label:'문자열',             hint:'오늘 그 자리에 있던 것. 내용은 아직 모른다'},
    {k:'list',   label:'빈 리스트',           hint:'정수 인덱스가 아니다'},
  ];

  function resolve(kind, prop){
    if(kind === 'dto')  return {result:'value', text:'[이미지 3장]'};
    if(kind === 'map')  return {result:'value', text:'[이미지 3장]'};
    // EL 은 null 을 오류로 보지 않는다. 화면에는 아무것도 찍히지 않고,
    // 로그에도 아무것도 남지 않는다. 이것이 이 문서가 말하는 '조용한 실패'다.
    if(kind === 'null') return {result:'empty', text:'(빈 문자열로 렌더된다)'};
    const type = kind === 'string' ? 'java.lang.String' : 'java.util.ArrayList';
    return {result:'throw',
            text:`javax.el.PropertyNotFoundException: Property [${prop}] not found on type [${type}]`};
  }

  return {VALUES, resolve};
})();
window.EL = EL;
```

- [ ] **Step 3-1: 이 문서에 처음 등장하는 컴포넌트의 CSS 를 이식한다**

이 태스크가 이 문서의 **첫 데모와 첫 퀴즈**를 놓는다. 1번 태스크는 마크업이 없는 CSS 를
남길 수 없었으므로(전역 제약), 그 컴포넌트들의 CSS 가 지금 필요하다. `auth_basics.html` 의
`<style>` 블록들에서 아래 규칙을 **그대로** 이식한다. 새로 디자인하지 않는다.

`.demo` · `.demo .demo-tag` · `.demo input[type="text"]` · `.demo input[type="range"]` ·
`.demo label` · `.picker` · `.pick` · `.pick:hover` · `.pick.on` · `.verdict` ·
`.verdict .badge` · `.oneline` · `.quiz .q-head` · `.quiz .opt .mk` ·
`.quiz .opt.correct .mk` · `.quiz .opt.wrong .mk`

(`.quiz` · `.quiz .opt` · `.quiz .explain` · `.term` · `.nextq` · `.trace` 는 1번 태스크가
이미 넣어 두었다. 중복해서 넣지 않는다.)

**`.kv` 만은 그대로 옮기면 안 된다.** `auth_basics.html` 의 `.kv` 는 `<dt>`/`<dd>` 를 전제하는데
이 문서의 데모는 `<span class="k">` 를 쓴다. 다음으로 넣는다.

```css
.kv{display:grid; grid-template-columns:auto 1fr; gap:8px 16px; margin:14px 0;
  font-size:14px; align-items:baseline}
.kv .k{font-family:var(--mono); font-size:12.5px; color:var(--accent); white-space:nowrap}
```

이식이 끝나면 `python3 tools/check_dead_css.py defensive_programming.html` 이 통과해야 한다.
통과하지 않으면 이 태스크가 쓰지 않는 규칙까지 가져온 것이므로 그것을 지운다.

- [ ] **Step 4: 데모 마크업과 배선을 넣는다**

`#trace` 섹션 안에 넣는다.

```html
<div class="demo" id="elLab">
  <span class="demo-tag">EL 이 실제로 하는 일</span>
  <p style="margin:0 0 10px">JSP 가 <code>${section.bannerImageList}</code> 를 만났습니다.
  <code>section</code> 자리에 무엇이 들어 있느냐에 따라 결과가 갈립니다. 하나씩 눌러 보세요.</p>
  <div class="picker" id="elPicker"></div>
  <div id="elOut" aria-live="polite"></div>
</div>
```

```js
(() => {
  const picker = $('#elPicker'), out = $('#elOut');
  picker.innerHTML = EL.VALUES.map((v, i) =>
    `<button class="pick${i ? '' : ' on'}" data-k="${v.k}">${v.label}</button>`).join('');

  function render(k){
    const v = EL.VALUES.find(x => x.k === k);
    const r = EL.resolve(k, 'bannerImageList');
    const tone = r.result === 'throw' ? 'bad' : r.result === 'empty' ? 'warn' : 'good';
    const verdict = r.result === 'throw' ? '예외가 던져지고, 여기서 페이지가 끝난다'
                  : r.result === 'empty' ? '아무 일도 일어나지 않는다 — 그것이 문제다'
                  : '값이 나온다';
    out.innerHTML = `
      <div class="kv"><span class="k">section 에 들어 있는 것</span><span>${v.label} <span class="dim">— ${v.hint}</span></span></div>
      <pre class="trace"><code>${r.text}</code></pre>
      <div class="verdict ${tone}">${verdict}</div>`;
  }
  wirePicker('#elPicker', render);
  render('dto');
})();
```

`.verdict` 에 `good` · `warn` · `bad` 색이 없으면 CSS 를 더한다.

```css
.verdict.good{border-color:var(--accent); color:var(--text)}
.verdict.warn{border-color:#fbbf24; color:var(--text)}
.verdict.bad{border-color:#fb7185; color:var(--text)}
```

- [ ] **Step 5: 본문을 쓴다**

`#trace` 에 다음 논지를 순서대로 담는다. 설계 문서 7장의 1장 항목이 근거다.

1. 예외 한 줄을 낱말 단위로 해부한다. `Property [bannerImageList]` 는 찾던 것, `not found` 는 못 찾았다는 것, `on type [java.lang.String]` 은 **어디에서** 못 찾았는지다. 마지막 조각이 전부다.
2. EL 이 하는 일: 런타임에 리플렉션으로 `getBannerImageList()` 를 찾는다. **컴파일러는 이 경로를 한 번도 보지 않았다.**
3. 데모(위)로 다섯 경우를 직접 눌러 보게 한다.
4. 스택트레이스를 위에서 아래로 읽으며, 이 열 줄이 전부 **렌더링 중에 일어난 일**임을 확인한다. `mainSections_jsp.java:9946` 과 `_005fset_005f141` 이 말해 주는 것은 하나다. 한 파일 안에 `<c:set>` 이 **적어도** 141개 있다. (번호가 증명하는 것은 하한이다. 6장도 같은 어법을 쓴다.).
5. 발현 지점과 발원 지점의 거리를 그림으로 못 박는다. 그 값이 문자열이 된 자리는 이 열 줄 어디에도 없다.
6. **그 문자열이 무엇이었는지는 쓰지 않는다.** 이 예외가 보증하는 범위는 타입까지다. 내용을 아는 것처럼
   쓰면 2장이 성립하지 않는다. 데모의 네 번째 칸도 "빈 문자열"이 아니라 그냥 "문자열"이다. 이 장은
   "그 자리에 문자열이 있었다"까지만 확인하고, "무슨 문자열이었나"는 2장에 넘긴다.
6. 용어 `<span class="term" data-t="EL">`, `<span class="term" data-t="리플렉션">` 을 심고 `GLOSSARY` 에 정의를 넣는다.
7. `.nextq`: 그러면 그 값은 어디에서 문자열이 되었을까. **그런데 우리는 아직 그것을 모른다.**

퀴즈 하나를 넣는다. `data-qid="q-trace"`.

```html
<div class="quiz" data-qid="q-trace" data-answer="d">
  <div class="q-head">✅ 체크포인트</div>
  <div class="q">이 스택트레이스만 보고 <b>확실하게</b> 말할 수 있는 것은?</div>
  <button class="opt" data-opt="a"><span class="mk">A</span> JSP 9946번째 줄에 버그가 있다</button>
  <button class="opt" data-opt="b"><span class="mk">B</span> 데이터를 준 API 가 잘못된 응답을 내려보냈다</button>
  <button class="opt" data-opt="c"><span class="mk">C</span> 캐시가 값을 잘못 저장했다</button>
  <button class="opt" data-opt="d"><span class="mk">D</span> 렌더링 시점에 그 자리에 문자열이 있었다는 것 하나뿐이다</button>
  <div class="explain"><b>정답 D.</b> …</div>
</div>
```

해설에서 A · B · C 가 왜 추측인지 각각 한 문단으로 적는다. **이 추측들이 2장의 출발점이다.**

- [ ] **Step 6: 검사기와 테스트를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py tools/test_defensive_behavior.py -v
python3 tools/check_dead_css.py defensive_programming.html
```
Expected: 전부 통과.

- [ ] **Step 7: 커밋**

```bash
git add defensive_programming.html tools/test_defensive_behavior.py
git commit -m "1장: 스택트레이스를 해부하고, EL 이 값의 타입마다 무엇을 하는지 눌러 보게 한다

EL.resolve 를 순수 함수로 노출해 다섯 경우를 테스트가 직접 검사한다.
null 이 조용히 통과하고 문자열이 던지는 비대칭은 3장이 다시 쓴다."
```

---

### Task 4: 2장 · 그런데 우리는 아직 원인을 모른다 (D2 · 로그 취조실)

**Files:**
- Modify: `defensive_programming.html` (`#unknown` 섹션)

**Interfaces:**
- Consumes: `wireTogs(sel, onChange)` (Task 1)
- Produces: 없음. 이 데모는 이 장에서만 쓴다.

- [ ] **Step 1: 데모 마크업과 배선을 넣는다**

맥락 다섯 개를 토글로 켜고 끄면, 남는 로그 한 줄과 **원인에 도달하기까지 남은 조사 단계 수**가 함께 바뀐다.

```html
<div class="demo" id="logLab">
  <span class="demo-tag">무엇을 담았어야 알 수 있었나</span>
  <p style="margin:0 0 10px">예외에 담을 맥락을 하나씩 켜 보세요. 아래 로그 한 줄과, 그 로그만 손에 쥔 사람이
  원인에 닿기까지 <b>더 해야 하는 조사</b>가 함께 바뀝니다.</p>
  <div class="cl-togs" id="logTogs">
    <button class="tog" data-k="which">어느 섹션인지</button>
    <button class="tog" data-k="prop">어떤 키를 찾았는지</button>
    <button class="tog" data-k="got">실제로 들어 있던 타입</button>
    <button class="tog" data-k="peek">그 값의 앞 40자</button>
    <button class="tog" data-k="src">그 값을 만든 곳</button>
  </div>
  <div id="logOut" aria-live="polite"></div>
</div>
```

```js
(() => {
  // 켜진 맥락이 없으면 오늘 우리가 손에 쥔 것과 같다. 하나씩 켤 때마다
  // '더 해야 하는 조사'가 줄어드는 것이 이 데모의 전부다.
  const STEPS = {
    which: '어느 섹션에서 났는지 알아내려고 JSP 9946줄 근처의 <c:set> 141개를 센다',
    prop:  '어떤 값을 찾다가 났는지 알아내려고 EL 표현식을 역추적한다',
    got:   '무엇이 들어 있었는지 알아내려고 같은 요청을 재현해 본다',
    peek:  '그 문자열이 무엇이었는지 알아내려고 상류 응답을 뒤진다',
    src:   '누가 그 값을 넣었는지 알아내려고 호출 경로를 전부 읽는다',
  };
  const LINE = {
    which: 'section=brandWeek',
    prop:  'property=bannerImageList',
    got:   'actualType=java.lang.String',
    peek:  'valuePeek="{\\"code\\":\\"E0021\\",\\"mes…"',
    src:   'source=SectionContentCache#get',
  };
  const out = $('#logOut');
  let on = {};

  function render(){
    const keys = Object.keys(LINE).filter(k => on[k]);
    const line = 'ERROR 섹션 렌더링 실패 ' +
      (keys.length ? keys.map(k => LINE[k]).join(' ') : '(맥락 없음)') +
      ' — javax.el.PropertyNotFoundException';
    const left = Object.keys(STEPS).filter(k => !on[k]);
    out.innerHTML = `
      <pre class="trace"><code>${line}</code></pre>
      <div class="kv"><span class="k">남은 조사</span><span>${left.length}단계</span></div>
      ${left.length
        ? `<ul class="todo">${left.map(k => `<li>${STEPS[k]}</li>`).join('')}</ul>`
        : `<div class="verdict good">로그 한 줄로 끝난다. 재현도, 역추적도 필요 없다.</div>`}
      ${on.peek ? `<div class="verdict warn">값을 통째로 담지 않고 앞 40자만 담았습니다.
        전부 담으면 개인정보가 로그로 새어 나갈 수 있습니다.</div>` : ''}`;
  }
  wireTogs('#logTogs', st => { on = st; render(); });
  render();
})();
```

`.todo` 와 `.tog` CSS 가 없으면 더한다.

```css
.todo{margin:10px 0 0; padding-left:20px; color:var(--text-mut); font-size:14.5px; line-height:1.9}
```

**이 장에 이 문서의 첫 `.stack` 블록이 들어간다**(Step 2 의 8번). 1번 태스크는 마크업 없는
CSS 를 남길 수 없었으므로 그 CSS 도 여기서 함께 넣는다.

```css
/* 스프링·라이브러리 이름만 담는 블록. 접어도 논지가 끊기지 않아야 한다. */
.stack{
  margin:22px 0; border:1px dashed var(--border-2); border-radius:12px;
  background:var(--bg-soft); overflow:hidden;
}
.stack > summary{
  cursor:pointer; list-style:none; padding:11px 16px; font-size:13.5px;
  color:var(--text-mut); font-family:var(--mono);
}
.stack > summary::-webkit-details-marker{display:none}
.stack > summary::before{content:"🧰 "}
.stack[open] > summary{border-bottom:1px dashed var(--border-2); color:var(--text-dim)}
.stack .sbody{padding:14px 18px; font-size:15px; color:var(--text-dim)}
.stack .sbody code{color:var(--accent-2)}
```

이 CSS 를 넣으면 `tools/test_defensive_document.py` 의
`test_the_stack_parser_still_matches_the_markup` 이 처음으로 0 이 아닌 수를 대조하게 된다.
`class="stack"` 의 등장 횟수와 파서가 찾은 블록 수가 어긋나면 그 자리에서 실패한다.

- [ ] **Step 2: 본문을 쓴다**

논지 순서는 설계 문서 7장의 2장 항목을 따른다.

1. 1장 퀴즈의 오답 셋(A · B · C)을 다시 꺼낸다. 셋 다 그럴듯하지만 **이 로그로는 어느 것도 확인할 수 없다.**
2. 이 스택트레이스가 말해 주지 않는 것을 목록으로 세운다. 어느 섹션인지, 그 문자열이 무엇이었는지, 어디에서 왔는지.
3. **실패를 막는 것과 실패를 설명하는 것은 다른 일이고, 둘 다 방어다.** 이 문장이 이 장의 축이다.
4. 예외에 담아야 하는 것 셋: 무엇을 하려다가(연산), 무엇에 대해(식별자), 무엇을 받았는지(타입과 요약).
5. `cause` 를 잃지 않기. 감쌀 때 원본을 버리면 스택트레이스가 거짓말을 시작한다.
6. 담지 말아야 할 것. 개인정보와 자격 증명은 요약과 타입까지만 담는다. `auth_basics.html` 을 링크로 잇는다.
7. 데모(위).
8. `<details class="stack">` 에 스프링 이름을 넣는다. 로깅 파사드, MDC 로 요청 단위 식별자를 붙이는 방법, `@ControllerAdvice` 에서 남기는 것. **개념은 본문에서 이미 다 말했고 여기서는 이름만 잇는다.**
9. `.nextq`: 담을 맥락을 정하려면 애초에 **무엇이 잘못인지** 정의되어 있어야 한다. 그런데 이 값은 정말로 잘못된 값이었을까.

퀴즈 `data-qid="q-unknown"` 을 넣는다. 주제는 "예외를 감싸면서 `cause` 를 버린 코드가 무엇을 잃는가".

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py -v
python3 tools/check_dead_css.py defensive_programming.html
```
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "2장: 원인을 모른다는 사실을 재료로 쓴다 — 진단 가능성도 방어다

맥락을 하나씩 켤 때마다 남은 조사 단계가 줄어드는 것을 눌러 보게 했다.
값 전체가 아니라 앞 40자만 담는 이유도 데모 안에서 말한다."
```

---

### Task 5: 3장 · null은 조용하고 잘못된 타입은 시끄럽다 (D3 · 조용한 실패 카운터)

**Files:**
- Modify: `defensive_programming.html` (`#silent` 섹션)

**Interfaces:**
- Consumes: `EL.resolve` (Task 3), `wireTogs` (Task 1)
- Produces: 없음.

- [ ] **Step 1: 데모를 넣는다**

파이프라인 네 단계(응답 파싱 · 캐시 · 모델 조립 · 뷰)를 놓고, 각 단계를 "조용히 넘김"과 "즉시 터뜨림"으로 토글한다. 결과로 **최종 화면**과 **문제를 알아차린 시점**이 함께 바뀐다.

```js
(() => {
  const STAGES = [
    {k:'parse', name:'응답 파싱',  quiet:'파싱 실패를 잡고 원문 문자열을 그대로 담는다'},
    {k:'cache', name:'캐시 저장',  quiet:'타입을 보지 않고 저장한다'},
    {k:'model', name:'모델 조립',  quiet:'Map 에 넣는다 — 무엇이든 들어간다'},
    {k:'view',  name:'화면 렌더',  quiet:'없다 — 여기서는 조용할 수가 없다'},
  ];
  const out = $('#silentOut');
  let loud = {};

  function render(){
    // 처음으로 시끄러운 단계가 문제를 알아차리는 자리다. 아무 단계도
    // 시끄럽지 않으면 뷰까지 가서 터진다 — 오늘 일어난 일이 그것이다.
    const first = STAGES.find(s => loud[s.k]);
    const at = first || STAGES[STAGES.length - 1];
    const cost = STAGES.indexOf(at);
    out.innerHTML = `
      <div class="kv"><span class="k">문제를 알아차린 곳</span><span><b>${at.name}</b></span></div>
      <div class="kv"><span class="k">그때까지 통과한 단계</span><span>${cost}개</span></div>
      <div class="kv"><span class="k">사용자가 보는 것</span><span>${
        first ? '그 섹션만 비어 있고 나머지는 정상' : '페이지 전체가 오류 화면'}</span></div>
      <div class="verdict ${first ? 'good' : 'bad'}">${
        first
          ? `${at.name} 에서 멈췄으므로, 로그가 가리키는 곳과 잘못된 곳이 같습니다.`
          : `아무도 항의하지 않아 값이 화면까지 갔습니다. 로그가 가리키는 곳은 JSP 9946줄이지만, 잘못된 곳이 어디였는지는 이 화면으로도 알 수 없습니다.`}</div>`;
  }
  wireTogs('#silentTogs', st => { loud = st; render(); });
  render();
})();
```

마크업은 D2 의 `.cl-togs` 패턴을 따르되, 버튼 라벨은 "응답 파싱에서 터뜨린다" 처럼 **켜면 시끄러워지는** 방향으로 적는다.

- [ ] **Step 2: 본문을 쓴다**

1. 1장 데모의 비대칭을 다시 꺼낸다. `null` 은 빈 문자열로 렌더되고 문자열은 던진다. **오늘 터진 것은 오히려 운이 좋은 쪽이다.**
2. 조용한 실패의 목록을 짓는다. 빈 컬렉션 반환 · 기본값 대입 · `Optional.orElse(기본값)` · 잡고 로그만 남기기 · `catch (Exception ignored)`. 각각이 언제 옳고 언제 은폐인지 한 줄씩 붙인다.
3. **방어적 프로그래밍의 첫 번째 오해를 여기서 깬다.** 목적은 예외가 나지 않게 하는 것이 아니다. 목적은 **잘못된 상태가 멀리 가지 못하게 하는 것**이고, 예외는 그 목적의 수단이지 적이 아니다.
4. 데모(위).
5. 그러나 모든 곳에서 터뜨릴 수는 없다. 뷰에서 터뜨리면 페이지가 죽고, 어디서나 터뜨리면 사소한 결함이 전부 장애가 된다.
6. `.nextq`: 그럼 **어디에서** 터뜨려야 하나.

용어 `조용한 실패` · `fail-fast` 를 심는다(`fail-fast` 의 본격적인 정의는 8장이지만, 여기서 처음 이름을 부른다).

퀴즈 `data-qid="q-silent"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "3장: 조용한 실패가 더 위험하다 — 예외는 목적의 수단이지 적이 아니다

네 단계를 시끄럽게 켜 볼수록 알아차리는 시점이 앞당겨지는 것을 보여 준다.
아무 단계도 시끄럽지 않을 때가 오늘 일어난 일이다."
```

---

### Task 6: 4장 · 검사는 곳곳이 아니라 선 위에서 한다 (D4 · 검증 지점 이동기)

**Files:**
- Modify: `defensive_programming.html` (`#boundary` 섹션)
- Modify: `tools/test_defensive_behavior.py`

**Interfaces:**
- Consumes: `wirePicker` (Task 1)
- Produces: `window.Pipeline` — `Pipeline.STAGES` · `Pipeline.run(guardAt)` → `{caughtAt, frames:[string], message}`

- [ ] **Step 1: 테스트를 쓴다**

```python
def pipeline(page, guard_at):
    return page.evaluate('g => Pipeline.run(g)', guard_at)


def test_guarding_late_leaves_a_long_trace(page):
    r = pipeline(page, 'view')
    assert len(r['frames']) >= 8
    assert 'PropertyNotFoundException' in r['message']


def test_guarding_at_the_boundary_leaves_a_short_one(page):
    """검증을 앞으로 옮길수록 스택트레이스가 짧아지고 메시지가 정확해진다."""
    early = pipeline(page, 'parse')
    late = pipeline(page, 'view')
    assert len(early['frames']) < len(late['frames'])
    assert early['caughtAt'] == 'parse'


def test_the_early_message_names_what_was_wrong(page):
    r = pipeline(page, 'parse')
    assert 'bannerImageList' in r['message']
    assert 'String' in r['message']
```

- [ ] **Step 2: 실패를 확인한다**

Run: `python3 -m pytest tools/test_defensive_behavior.py -k guarding -v`
Expected: FAIL — `Pipeline is not defined`.

- [ ] **Step 3: 엔진과 데모를 구현한다**

```js
/* ==== D4 · 검증 지점 이동기 ========================================
   같은 잘못된 값을 흘리되 검증을 어디에 두느냐만 바꾼다. 스택트레이스의
   길이와 메시지의 정확도가 검증 위치의 함수라는 것을 보여 준다.
   ================================================================== */
const Pipeline = (() => {
  const STAGES = [
    {k:'parse', name:'응답 파싱',   frame:'SectionResponseParser.parse(SectionResponseParser.java:41)'},
    {k:'cache', name:'캐시 저장',   frame:'SectionContentCache.put(SectionContentCache.java:88)'},
    {k:'model', name:'모델 조립',   frame:'MainPageAssembler.toModel(MainPageAssembler.java:112)'},
    {k:'view',  name:'화면 렌더',   frame:'PageContextImpl.proprietaryEvaluate(PageContextImpl.java:655)'},
  ];
  // 검증이 없을 때 실제로 쌓이는 프레임. 뷰까지 가면 EL 내부 프레임이 더 얹힌다.
  const EL_FRAMES = [
    'javax.el.BeanELResolver$BeanProperties.get(BeanELResolver.java:253)',
    'javax.el.BeanELResolver.property(BeanELResolver.java:322)',
    'javax.el.BeanELResolver.getValue(BeanELResolver.java:93)',
    'org.apache.jasper.el.JasperELResolver.getValue(JasperELResolver.java:123)',
    'org.apache.el.parser.AstValue.getValue(AstValue.java:160)',
  ];

  function run(guardAt){
    const idx = STAGES.findIndex(s => s.k === guardAt);
    const at = idx < 0 ? STAGES.length - 1 : idx;
    const frames = STAGES.slice(0, at + 1).map(s => s.frame);
    if(STAGES[at].k === 'view'){
      // 검증이 없으면 EL 안쪽까지 들어가서 터진다. 프레임이 길어질수록
      // 그 안에 원인이 없을 확률도 함께 커진다.
      return {caughtAt:'view', frames: EL_FRAMES.concat(frames),
              message:'javax.el.PropertyNotFoundException: Property [bannerImageList] not found on type [java.lang.String]'};
    }
    return {caughtAt: STAGES[at].k, frames,
            message:`SectionContentException: brandWeek 섹션의 bannerImageList 가 List 여야 하는데 String 이 왔다 (앞 40자: {"code":"E0021","mes…)`};
  }

  return {STAGES, run};
})();
window.Pipeline = Pipeline;
```

데모 마크업은 `.picker` 로 네 단계를 고르게 하고, 고를 때마다 프레임 목록과 메시지를 `<pre class="trace">` 로 그린다. 프레임 수를 `.kv` 로 함께 보여 준다.

**이 데모의 메시지에 나오는 `brandWeek`·`bannerImageList`·`E0021` 은 전부 가정이다.** 이른 검증이 남겼을 로그가 어떤 모양인지 보여 주려면 구체적인 값이 필요하지만, 우리는 오늘 어느 섹션이었는지도 그 문자열이 무엇이었는지도 모른다. 데모를 감싸는 본문이 그 가정을 명시해야 한다(전역 제약 참조). 2장이 "이 다섯 가지 맥락이 있었다고 가정하고" 로 한 것과 같은 방식이면 된다.

- [ ] **Step 4: 본문을 쓴다**

1. 신뢰 경계의 정의. **밖에서 들어온 것**과 **안에서 만든 것**을 가른다. 밖의 범위에는 외부 API, 데이터베이스, 캐시, 사용자 입력, 그리고 **다른 팀의 코드**가 들어간다.
2. 이번 사건의 경계 후보 넷을 놓고, 원인을 모르는 세 경로(응답 파싱 실패 · 캐시 역직렬화 실패 · 상류의 빈 값)를 나란히 그린다. **셋 다 같은 답을 준다**: 선은 응답이 우리 타입이 되는 자리에 있다.
3. 데모(위).
4. 경계 안쪽에서 다시 검사하지 않기 위한 조건. 경계를 통과한 값의 타입이 보장되어야 한다. 보장되지 않으면 안쪽 전부가 경계가 되고, 그것이 "곳곳에 null 체크"의 정체다.
5. 방어적 복사. 경계를 넘어온 컬렉션과 가변 객체를 그대로 들고 있지 않는다.
6. `<details class="stack">`: Bean Validation 과 `@Valid` 가 서는 자리, `Objects.requireNonNull`, 역직렬화에서 알 수 없는 필드를 어떻게 다루도록 설정하는지.
7. `.nextq`: 경계를 통과한 뒤에도 객체가 이상한 상태가 될 수 있다.

용어 `신뢰 경계` · `방어적 복사` 를 심는다. 퀴즈 `data-qid="q-boundary"`.

- [ ] **Step 5: 검사기와 테스트를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py tools/test_defensive_behavior.py -v
python3 tools/check_dead_css.py defensive_programming.html
```
Expected: 전부 통과.

- [ ] **Step 6: 커밋**

```bash
git add defensive_programming.html tools/test_defensive_behavior.py
git commit -m "4장: 검증 위치를 옮기면 스택트레이스가 짧아진다

Pipeline.run 을 순수 함수로 노출해 프레임 수와 메시지의 정확도가 검증
위치의 함수임을 테스트가 직접 잰다. 원인을 모르는 세 경로가 같은 답을
준다는 것이 이 장의 결론이다."
```

---

### Task 7: 5장 · 애초에 그런 값을 가질 수 없게 만든다 (D5 · 불변식 실험대)

**Files:**
- Modify: `defensive_programming.html` (`#invariant` 섹션)

**Interfaces:**
- Consumes: `wirePicker` (Task 1)
- Produces: 없음.

- [ ] **Step 1: 데모를 넣는다**

같은 잘못된 데이터를 세 가지 모델(`Map<String,Object>` · 검증 없는 DTO · 생성자에서 강제하는 DTO)로 다룰 때, 오류가 **드러나는 시점**을 나란히 보여 준다.

```js
(() => {
  const MODELS = [
    {k:'map',   label:'Map<String,Object>',
     caught:'화면 렌더',   when:'요청 처리가 거의 끝난 뒤',
     why:'담을 때 아무 조건이 없다. 무엇이든 들어가고, 꺼내는 쪽이 처음으로 항의한다'},
    {k:'dto',   label:'검증 없는 DTO',
     caught:'모델 조립',   when:'역직렬화 직후',
     why:'필드 타입이 있으므로 역직렬화가 항의한다. 다만 값의 의미는 아무도 보지 않는다'},
    {k:'strict',label:'생성자에서 강제하는 DTO',
     caught:'응답 파싱',   when:'객체가 만들어지는 순간',
     why:'조건을 만족하지 못하는 객체는 애초에 존재할 수 없다. 이후 코드는 검사할 것이 없다'},
  ];
  // 세 줄의 차이는 '검사를 더 했는가'가 아니라 '검사할 필요가 없는 타입을
  // 만들었는가'다. 마지막 줄에는 검사하는 코드가 오히려 가장 적다.
  const out = $('#invOut');
  function render(k){
    const m = MODELS.find(x => x.k === k);
    out.innerHTML = `
      <div class="kv"><span class="k">오류가 드러나는 곳</span><span><b>${m.caught}</b></span></div>
      <div class="kv"><span class="k">시점</span><span>${m.when}</span></div>
      <div class="verdict ${k === 'strict' ? 'good' : k === 'dto' ? 'warn' : 'bad'}">${m.why}</div>`;
  }
  wirePicker('#invPicker', render);
  render('map');
})();
```

- [ ] **Step 2: 본문을 쓴다**

1. 불변식의 정의. 그 객체가 살아 있는 동안 항상 참인 것.
2. 생성자에서 강제하기. 조건을 만족하지 못하는 객체를 **만들 수 없게** 한다.
3. **`Map<String,Object>` 모델이 치르는 대가.** 이번 사건의 급소다. 모델에 담기는 순간 타입이 사라지고, 그때부터 EL 까지 아무도 항의하지 않는다.
4. 데모(위).
5. 사전조건 · 사후조건 · 불변식을 구분하고 각각을 어디에 두는지 정한다. 사전조건은 경계에, 사후조건은 만든 쪽에, 불변식은 타입 안에.
6. 값 타입과 불변 객체. `int` 대신 `Quantity`, `String` 대신 `SectionId`.
7. **검사하는 코드와 검사할 필요가 없는 타입의 차이.** 후자가 항상 이긴다. 검사하는 코드는 빠뜨릴 수 있지만 타입은 빠뜨릴 수 없다.
8. `<details class="stack">`: 레코드, 정적 팩터리 메서드, 설정 바인딩에서 생성자를 쓰는 방법.
9. `.nextq`: 객체 하나하나가 옳아도 **조립**이 틀릴 수 있다.

용어 `불변식` · `사전조건` · `사후조건` · `값 타입` 을 심는다. 퀴즈 `data-qid="q-invariant"`. 난이도는 🔵.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "5장: 검사하는 코드보다 검사할 필요가 없는 타입이 이긴다

같은 데이터를 세 모델로 다룰 때 오류가 드러나는 시점을 나란히 놓았다.
Map<String,Object> 에서 타입이 사라지는 자리가 이번 사건의 급소다."
```

---

### Task 8: 6장 · 섹션 하나가 죽어서 메인이 죽었다 (D6 첫 등장 · 격리 없음)

**Files:**
- Modify: `defensive_programming.html` (`#assembly` 섹션)

**Interfaces:**
- Consumes: `Assembly.assemble` · `Assembly.SECTIONS` (Task 2)
- Produces: `window.renderAssembly(rootSel, opts)` — 조립 결과를 화면으로 그리는 함수. 9장과 10장이 다시 쓴다. `opts` 는 `{controls:['fault'|'isolate'|'timeout'|'bulkhead'|'breaker'|'fallback'], preset:{}}`.

- [ ] **Step 1: 화면 렌더러를 구현한다**

엔진은 이미 있다(Task 2). 이 태스크는 **화면**을 붙이는 일이다. 세 장이 같은 렌더러를 쓰되 노출하는 조작만 다르므로, `opts.controls` 로 조작 목록을 받는다.

```js
/* ==== D6 화면 · 6·9·10장이 같은 렌더러를 쓴다 ======================
   엔진(Assembly)은 순수 함수고, 여기는 그 결과를 그리기만 한다.
   장마다 노출하는 조작만 다르다 — opts.controls 가 그것을 정한다.
   ================================================================== */
const SECTION_STATE = {
  ok:       {cls:'s-ok',   label:'정상'},
  empty:    {cls:'s-dim',  label:'데이터 없음'},
  slow:     {cls:'s-warn', label:'느림'},
  hide:     {cls:'s-gone', label:'숨김'},
  cache:    {cls:'s-cache',label:'직전 값'},
  skeleton: {cls:'s-skel', label:'골격'},
  blank:    {cls:'s-gone', label:'빈자리'},
  open:     {cls:'s-open', label:'호출 안 함'},
};

function renderAssembly(rootSel, opts){
  const root = $(rootSel);
  const state = {faults:{}, strategy:Object.assign({}, Assembly.DEFAULT_STRATEGY, opts.preset || {})};
  const screen = $('.asm-screen', root), meter = $('.asm-meter', root);

  function paint(){
    const r = Assembly.assemble(state.faults, state.strategy);
    if(r.pageState === 'error'){
      // 오늘 사용자가 본 화면이다. 조립하다 만 것이 아니라 아무것도 없다.
      const who = Assembly.SECTIONS.find(s => s.id === r.failedAt);
      screen.innerHTML = `<div class="asm-500">500 Internal Server Error
        <span>${who.name} 에서 예외가 났고, 그것을 멈춰 세울 경계가 없었습니다.</span></div>`;
    }else{
      screen.innerHTML = r.rendered.map(s => {
        const st = SECTION_STATE[s.state];
        return `<div class="asm-sec ${st.cls}"><b>${s.name}</b><span>${st.label}</span></div>`;
      }).join('');
    }
    meter.innerHTML = `
      <div class="kv"><span class="k">페이지</span><span>${
        r.pageState === 'error' ? '오류' : r.pageState === 'partial' ? '일부 비어 있음' : '정상'}</span></div>
      <div class="kv"><span class="k">응답 시간</span><span>${r.totalMs}ms</span></div>`;
  }

  // 조작 배선은 opts.controls 에 있는 것만 만든다. 없는 조작의 버튼은 그리지 않는다.
  buildControls(root, opts.controls, state, paint);
  paint();
  return {paint, state};
}
window.renderAssembly = renderAssembly;
```

조작 배선을 구현한다. **`opts.controls` 에 있는 조작만 만든다** — 6장은 결함 주입만, 9장은 타임아웃·격벽·회로 차단까지, 10장은 폴백까지 노출한다.

```js
function buildControls(root, controls, state, paint){
  const bar = $('.asm-ctl', root);
  const FAULTS = [
    {k:'ok',    label:'정상'},
    {k:'throw', label:'예외를 던진다'},
    {k:'slow',  label:'느려진다'},
    {k:'empty', label:'데이터가 없다'},
  ];
  const togRow = (k, label) =>
    `<div class="ctl-row"><span class="ctl-k">${label}</span>
       <button class="tog" data-tog="${k}">끔</button></div>`;
  const pickRow = (r, label, opts) =>
    `<div class="ctl-row"><span class="ctl-k">${label}</span>
       <span class="picker" data-pick="${r}">${opts.map((o, i) =>
         `<button class="pick${i ? '' : ' on'}" data-k="${o.k}">${o.label}</button>`).join('')}</span></div>`;

  const parts = [];
  if(controls.includes('fault')){
    // 어느 섹션을 건드릴지 고르고, 그 섹션에 무엇이 일어나는지 고른다.
    // '없으면 안 되는 자리'라는 표시가 8장의 판단과 12장의 여섯 번째 질문으로 이어진다.
    parts.push(`<div class="ctl-row"><span class="ctl-k">결함을 넣을 섹션</span>
      <select class="ctl-sel">${Assembly.SECTIONS.map(s =>
        `<option value="${s.id}">${s.name}${s.critical ? ' · 없으면 안 되는 자리' : ''}</option>`).join('')}</select></div>`);
    parts.push(pickRow('fault', '그 섹션에 무엇이 일어나는가', FAULTS));
  }
  if(controls.includes('isolate'))  parts.push(togRow('isolate',  '섹션 경계에서 실패를 멈춘다'));
  if(controls.includes('timeout'))  parts.push(pickRow('timeout', '얼마나 기다리는가',
    [{k:'', label:'끝까지'}, {k:'1000', label:'1000ms'}, {k:'300', label:'300ms'}]));
  if(controls.includes('bulkhead')) parts.push(togRow('bulkhead', '섹션마다 자기 몫의 자원을 쓴다'));
  if(controls.includes('breaker'))  parts.push(togRow('breaker',  '반복 실패한 의존을 잠시 끊는다'));
  if(controls.includes('fallback')) parts.push(pickRow('fallback', '빈자리에 놓는 것',
    [{k:'none', label:'아무것도'}, {k:'hide', label:'숨김'}, {k:'cache', label:'직전 값'},
     {k:'skeleton', label:'골격'}]));
  bar.innerHTML = parts.join('');

  const sel = $('.ctl-sel', bar);
  const target = () => sel ? sel.value : Assembly.SECTIONS[0].id;

  $$('.picker', bar).forEach(pk => {
    pk.addEventListener('click', e => {
      const b = e.target.closest('.pick');
      if(!b) return;
      $$('.pick', pk).forEach(x => x.classList.toggle('on', x === b));
      const kind = pk.dataset.pick, v = b.dataset.k;
      if(kind === 'fault')        state.faults[target()] = v;
      else if(kind === 'timeout') state.strategy.timeoutMs = v === '' ? null : Number(v);
      else                        state.strategy[kind] = v;
      paint();
    });
  });

  $$('.tog', bar).forEach(b => {
    // 이 전략들은 켜고 끄는 것뿐이라 토글 하나로 충분하다. 상태는 strategy 에 있고
    // 버튼의 글자는 그 상태를 비추기만 한다.
    const k = b.dataset.tog;
    const paintTog = () => {
      b.classList.toggle('on', !!state.strategy[k]);
      b.textContent = state.strategy[k] ? '켬' : '끔';
    };
    b.addEventListener('click', () => { state.strategy[k] = !state.strategy[k]; paintTog(); paint(); });
    paintTog();   // preset 으로 이미 켜져 있을 수 있다 — 9·10장이 그렇다
  });

  if(sel) sel.addEventListener('change', () => {
    // 섹션을 바꾸면 버튼이 그 섹션의 현재 결함을 가리키게 맞춘다. 맞추지 않으면
    // 화면은 '예외'라고 말하는데 실제로는 다른 섹션의 값인 상태가 된다.
    const cur = state.faults[target()] || 'ok';
    const pk = $('.picker[data-pick="fault"]', bar);
    if(pk) $$('.pick', pk).forEach(x => x.classList.toggle('on', x.dataset.k === cur));
  });
}
```

마크업은 세 칸이다. 6·9·10장이 같은 모양을 쓰고 id 만 다르다.

```html
<div class="demo" id="asmLab">
  <span class="demo-tag">메인 조립 시뮬레이터</span>
  <p style="margin:0 0 10px">메인페이지는 전시 섹션 여덟 개를 위에서부터 조립합니다.
  섹션 하나에 결함을 넣어 보세요.</p>
  <div class="asm-ctl"></div>
  <div class="asm-screen"></div>
  <div class="asm-meter"></div>
</div>
```

6장에서는 결함 주입만 넘긴다.

```js
renderAssembly('#asmLab', {controls:['fault']});
```

CSS 를 더한다.

```css
.asm-screen{display:grid; gap:8px; padding:14px; background:#0a0f18; border:1px solid var(--border); border-radius:12px; min-height:260px}
.asm-sec{display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:9px; border:1px solid var(--border); background:var(--panel); font-size:14.5px}
.asm-sec span{margin-left:auto; font-family:var(--mono); font-size:11.5px; color:var(--text-mut)}
.asm-sec.s-ok{border-color:var(--border-2)}
.asm-sec.s-dim{opacity:.55}
.asm-sec.s-warn{border-color:#fbbf24}
.asm-sec.s-gone{border-style:dashed; opacity:.4}
.asm-sec.s-cache{border-color:#38bdf8}
.asm-sec.s-skel{background:repeating-linear-gradient(90deg, var(--panel) 0 18px, var(--panel-2) 18px 36px)}
.asm-sec.s-open{border-color:#c084fc; opacity:.7}
.asm-500{display:flex; flex-direction:column; gap:8px; align-items:center; justify-content:center;
  min-height:230px; color:#fb7185; font-family:var(--mono); font-size:18px; text-align:center}
.asm-500 span{font-family:var(--sans); font-size:14px; color:var(--text-mut); max-width:420px}
.asm-ctl{display:grid; gap:8px; margin-bottom:12px}
.ctl-row{display:flex; align-items:center; gap:10px; flex-wrap:wrap; font-size:14px; color:var(--text-dim)}
.ctl-k{min-width:170px; color:var(--text-mut); font-size:13.5px}
.ctl-sel{background:var(--panel); color:var(--text); border:1px solid var(--border-2);
  border-radius:8px; padding:6px 10px; font-family:var(--sans); font-size:13.5px}
.asm-meter{margin-top:10px}
```

- [ ] **Step 2: 6장 본문을 쓴다**

1. Hero 회수. 조립 구조를 그린다. 화면에서는 섹션이 독립적으로 보이지만 코드에서는 하나의 렌더링 흐름이다.
2. `mainSections_jsp.java:9946` 과 `_005fset_005f141` 을 다시 읽는다. 한 파일에 `<c:set>` 이 141개 있다는 것은 **섹션 사이에 경계가 하나도 없다**는 뜻이다.
3. **격리 단위와 조립 단위가 어긋나 있다.** 이 장의 문장이다.
4. 뷰 렌더링 중 예외의 특수성. 응답 버퍼가 이미 커밋되었다면 오류 페이지로 넘기는 것조차 불가능하고, 잘린 HTML 이 그대로 나간다.
5. 데모(위). `controls: ['fault']` 로 섹션 하나에 결함을 주입하면 화면 전체가 500 이 되는 것을 직접 확인하게 한다.
6. `<details class="stack">`: JSP 에서 include 를 나누는 방법, `<c:catch>` 가 무엇을 할 수 있고 무엇을 못 하는지 이름만 잇는다. 자세한 것은 부록 B.
7. `.nextq`: 그러면 그 예외를 **어디에서** 잡아야 하나.

용어 `응답 커밋` 을 심는다. 퀴즈 `data-qid="q-assembly"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py tools/test_defensive_behavior.py -v
python3 tools/check_dead_css.py defensive_programming.html
```
Expected: 전부 통과. 특히 `test_one_broken_section_takes_the_whole_page_when_nothing_isolates` 가 이 장의 논지이므로 반드시 초록이어야 한다.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "6장: 격리 단위와 조립 단위가 어긋나 있었다

Task 2 의 엔진에 화면을 붙였다. renderAssembly 는 9·10장이 다시 쓰므로
조작 목록을 opts.controls 로 받는다. 6장은 결함 주입만 노출한다."
```

---

### Task 9: 7장 · 예외를 삼킬 자격이 있는 층은 따로 있다 (D7 · 삼킬 자격 실험)

**Files:**
- Modify: `defensive_programming.html` (`#swallow` 섹션)

**Interfaces:**
- Consumes: `wirePicker` (Task 1)
- Produces: 없음.

- [ ] **Step 1: 데모를 넣는다**

같은 예외를 네 층에서 잡았을 때 **사용자가 보는 화면**과 **로그에 남는 것**을 나란히 놓는다.

```js
(() => {
  const LAYERS = [
    {k:'parse',  name:'응답 파서',   screen:'그 섹션이 잘못된 값으로 그려진다',
     log:'없음', can:false,
     why:'파서는 이 값 대신 무엇을 쓸지 모른다. 대안이 없는 층이 잡으면 그것은 삼킴이다'},
    {k:'service',name:'섹션 서비스', screen:'그 섹션이 빈 채로 그려진다',
     log:'경고 한 줄', can:true,
     why:'이 층은 "이 섹션은 비운다"는 대안을 가질 수 있다. 다만 비우는 것이 맞는지는 이 층이 정할 일이 아니다'},
    {k:'assembler',name:'페이지 조립기', screen:'그 섹션만 빠지고 나머지는 정상',
     log:'섹션 식별자와 함께 경고', can:true,
     why:'대안을 가진 층이다. 무엇으로 채울지는 요구사항이 정하고, 이 층은 그 결정을 실행한다'},
    {k:'global', name:'전역 처리기',  screen:'페이지 전체가 오류 화면',
     log:'스택트레이스 전체', can:false,
     why:'여기까지 왔다는 것은 이미 페이지 전체가 실패했다는 뜻이다. 마지막 그물이지 방어가 아니다'},
  ];
  const out = $('#swallowOut');
  function render(k){
    const l = LAYERS.find(x => x.k === k);
    out.innerHTML = `
      <div class="kv"><span class="k">사용자가 보는 것</span><span>${l.screen}</span></div>
      <div class="kv"><span class="k">로그에 남는 것</span><span>${l.log}</span></div>
      <div class="verdict ${l.can ? 'good' : 'bad'}">${l.can ? '삼킬 자격이 있다' : '삼킬 자격이 없다'} — ${l.why}</div>`;
  }
  wirePicker('#swallowPicker', render);
  render('parse');
})();
```

- [ ] **Step 2: 본문을 쓴다**

1. `try-catch` 를 아무 데나 넣으면 왜 나빠지는가. 잡은 층이 대안을 모르면 그것은 방어가 아니라 삼킴이다.
2. **삼킬 자격의 조건**: 그 실패에 대한 **대안을 가진 층**만 삼킬 수 있다. 이 장의 문장이다.
3. 데모(위).
4. 예외 설계. 무엇을 검사 예외로 두고 무엇을 비검사로 둘지. 판단 기준은 하나다. **호출자가 그것에 대해 할 수 있는 일이 있는가.**
5. 예외 타입이 곧 호출자의 선택지다. 전부 `RuntimeException` 으로 던지면 호출자는 고를 것이 없다.
6. 전역 예외 처리기는 마지막 그물이지 방어가 아니다.
7. `<details class="stack">`: `@ControllerAdvice` · `@ExceptionHandler` 가 서는 자리, 트랜잭션 경계에서 예외를 잡으면 무엇이 달라지는지.
8. `.nextq`: 잡을지 말지를 **무엇을 기준으로** 정하나.

퀴즈 `data-qid="q-swallow"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "7장: 대안을 가진 층만 예외를 삼킬 수 있다

같은 예외를 네 층에서 잡았을 때 화면과 로그가 어떻게 갈리는지 나란히
놓았다. 전역 처리기는 마지막 그물이지 방어가 아니라는 것이 결론이다."
```

---

### Task 10: 8장 · 빨리 죽을 자리와 버틸 자리 (D8 · 판단 연습)

문서의 중심 장이다.

**Files:**
- Modify: `defensive_programming.html` (`#failfast` 섹션)

**Interfaces:**
- Consumes: `Store.get` · `Store.set` (Task 1)
- Produces: 없음. 채점 결과는 `Store` 의 `judge` 키에 저장한다.

- [ ] **Step 1: 판단 연습 데모를 넣는다**

상황 카드 여덟 장. 고르면 채점하고, 근거는 항상 같은 기준 하나로 환원한다.

```js
(() => {
  // 답의 근거는 늘 같다: 잘못된 결과를 보여 주는 대가와, 아무것도 보여 주지
  // 못하는 대가 중 무엇이 더 큰가. 카드마다 그 저울이 어느 쪽으로 기우는지만 다르다.
  const CARDS = [
    {q:'메인페이지의 추천 상품 섹션이 응답하지 않는다',        a:'soft',
     why:'추천이 없어도 메인은 성립한다. 아무것도 못 보여 주는 대가가 훨씬 크다'},
    {q:'결제 금액을 계산하는 중 할인율 조회가 실패했다',        a:'fast',
     why:'틀린 금액을 청구하는 대가가 결제가 안 되는 대가보다 비교할 수 없이 크다'},
    {q:'상품 상세의 재고 수량 조회가 타임아웃됐다',             a:'fast',
     why:'없는 재고를 팔면 주문을 취소해야 한다. 조용히 옛 수량을 보여 주는 것이 더 나쁘다'},
    {q:'상품 목록의 위시리스트 하트 표시를 가져오지 못했다',    a:'soft',
     why:'하트가 비는 것과 목록이 안 뜨는 것 중에는 앞이 낫다'},
    {q:'로그인한 사용자의 등급별 가격을 가져오지 못했다',       a:'fast',
     why:'기본가로 보여 주면 사용자는 우리가 약속한 값을 못 받는다. 틀린 값이 빈 값보다 나쁘다'},
    {q:'메인 배너 이미지를 가져오지 못했다',                    a:'fast',
     why:'배너가 화면의 첫 절반을 차지한다면 그것이 빈 페이지는 성립하지 않는다. 무엇이 필수인지는 요구사항이 정한다'},
    {q:'주문 완료 후 알림 발송이 실패했다',                     a:'soft',
     why:'주문은 이미 성공했다. 알림 실패로 주문을 되돌리면 더 큰 손해가 난다'},
    {q:'배송지 주소의 우편번호 형식이 맞지 않는다',             a:'fast',
     why:'경계에서 잡지 않으면 배송이 실패한다. 그때는 되돌릴 수 없다'},
  ];
  // 카드 하나에 두 버튼, 고르면 즉시 채점하고 근거를 편다. 점수는 Store 에 남긴다.
  // 여섯 번째 카드가 이 장에서 가장 중요하다 — 답이 '요구사항이 정한다'로 끝난다.
})();
```

마크업은 카드마다 `<div class="jcard">` 에 질문과 버튼 둘(`빨리 죽는다` · `버틴다`), 그리고 접혀 있는 근거를 둔다.

- [ ] **Step 2: 본문을 쓴다**

1. fail-fast 와 fail-soft 의 정의. 우아한 저하.
2. **판단 기준 하나**: 잘못된 결과를 보여 주는 대가와, 아무것도 보여 주지 못하는 대가 중 무엇이 더 큰가.
3. 데모(위). 여덟 장을 다 고르게 한 뒤 채점을 보여 준다.
4. **이번 사건을 이 축 위에 놓는다.** 경계에서 늦게 죽었고(1~5장), 조립에서 버티지 못했다(6~7장). **두 가지를 동시에 틀렸다.**
5. 그래서 문서의 명제가 나온다. **경계에서는 엄격하게 검사해서 빨리 죽이고, 조립하는 자리에서는 부분 실패를 흡수해서 버텨라.** 이 문장을 화면에서 눈에 띄게 둔다.
6. 같은 `try-catch` 가 한쪽에서는 방어이고 다른 쪽에서는 은폐라는 것을 여섯 번째 카드로 확인한다. **무엇이 필수인지는 개발자가 정할 수 없다.** 이것이 3부로 가는 첫 번째 못이다.
7. `.nextq`: 섹션이 **죽지 않고 느려지면** 이 전략은 통하지 않는다.

용어 `fail-soft` · `우아한 저하` 를 심는다. 퀴즈 `data-qid="q-failfast"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "8장: 문서의 명제를 못 박는다 — 경계에서 빨리 죽고 조립에서 버텨라

여덟 장의 판단 카드는 전부 같은 기준 하나로 환원된다. 여섯 번째 카드가
'무엇이 필수인지는 요구사항이 정한다'로 끝나면서 3부로 가는 첫 못이 된다."
```

---

### Task 11: 9장 · 죽는 것보다 느린 것이 위험하다 (D6 재방문 · 타임아웃·격벽·회로 차단)

**Files:**
- Modify: `defensive_programming.html` (`#slowdown` 섹션)

**Interfaces:**
- Consumes: `renderAssembly` (Task 8) · `Assembly` (Task 2)
- Produces: 없음.

- [ ] **Step 1: 데모를 재사용한다**

```js
renderAssembly('#slowLab', {
  controls: ['fault', 'timeout', 'bulkhead', 'breaker'],
  preset: {isolate:true, fallback:'hide'},
});
```

6장과 달리 격리는 이미 켜 둔다. 이 장의 질문은 "격리했는데도 왜 느려지나"이기 때문이다.

- [ ] **Step 2: 본문을 쓴다**

1. 격리를 했는데도 전체가 죽는 경우. 섹션이 **죽지 않고 느려지면** 예외가 없으므로 격리가 발동하지 않는다.
2. 스레드 풀 고갈과 전염. 느린 섹션 하나가 요청 하나를 붙잡고, 요청이 쌓이면 풀이 마르고, 그러면 **멀쩡한 섹션의 요청도 처리되지 않는다.**
3. 데모(위). 타임아웃 없이 느린 섹션 하나를 주입하면 응답 시간이 3초를 넘는 것을 확인한다. 타임아웃을 켜면 상한이 생기고, 격벽을 켜면 다른 섹션의 시간에 더해지지 않는다.
4. **타임아웃 값을 정하는 방법.** 관행적인 3초가 아니라 상위 요청의 예산에서 거꾸로 나눈다. 메인페이지가 1초 안에 끝나야 한다면 섹션 여덟 개가 나눠 쓸 예산은 그 안에 있다.
5. 회로 차단기. 반복해서 실패하는 의존을 잠시 부르지 않는다. **부르지 않았으므로 시간도 들지 않는다.**
   그리고 곧바로 그 대가를 보여 준다. 데모에서 결함을 둘 넣어 회로를 열면 **푸터까지 끊기고
   페이지가 죽는다.** 회로를 섹션마다 걸지 않고 하나로 걸었기 때문이다. 여기서 한 문장이 나온다.
   **방어 수단 자체가 새로운 실패 모드를 만든다.** 그리고 푸터가 왜 없으면 안 되는 자리인지는
   개발자가 정한 것이 아니라는 사실로 11장에 다리를 놓는다.
6. 재시도와 그 위험. 상류가 이미 무너졌는데 재시도가 부하를 곱한다. 지수 백오프와 지터, 그리고 재시도해도 되는 연산의 조건인 멱등성.
7. `<details class="stack">`: Resilience4j 의 `TimeLimiter` · `Bulkhead` · `CircuitBreaker` · `Retry`, HTTP 클라이언트의 타임아웃이 **연결과 읽기 둘**이라는 사실.
8. `.nextq`: 버티기로 했다면, **비어 있는 그 자리에 무엇을 놓나.**

용어 `격벽` · `회로 차단기` · `멱등성` · `지수 백오프` · `지터` 를 심는다. 퀴즈 `data-qid="q-slowdown"`. 난이도는 🔵.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py tools/test_defensive_behavior.py -v
python3 tools/check_dead_css.py defensive_programming.html
```
Expected: 전부 통과. `test_a_bulkhead_stops_one_slow_section_from_adding_to_everyone` 과 `test_the_breaker_stops_calling_after_repeated_failures` 가 이 장의 논지다.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "9장: 격리했는데도 느려지면 다시 전체가 죽는다

같은 조립 시뮬레이터에 타임아웃·격벽·회로 차단을 얹었다. 타임아웃 값은
관행이 아니라 상위 요청의 예산에서 거꾸로 나눈다는 것이 실무 요지다."
```

---

### Task 12: 10장 · 비어 있는 자리에 무엇을 놓나 (D6 재방문 · 폴백)

**Files:**
- Modify: `defensive_programming.html` (`#fallback` 섹션)

**Interfaces:**
- Consumes: `renderAssembly` (Task 8)
- Produces: 없음.

- [ ] **Step 1: 데모를 재사용한다**

```js
renderAssembly('#fbLab', {
  controls: ['fault', 'fallback'],
  preset: {isolate:true, timeoutMs:300, bulkhead:true},
});
```

- [ ] **Step 2: 본문을 쓴다**

1. 폴백 전략 넷을 놓는다. 직전 캐시 값 · 기본 배너 · 섹션 숨기기 · 골격만 남기기.
2. 데모(위)로 넷을 눌러 가며 화면이 어떻게 달라지는지 본다.
3. **폴백의 위험**: 조용히 오래된 것을 보여 주는 문제. 배너는 괜찮지만 **가격과 재고는 치명적이다.** 2장의 조용한 실패가 여기서 되돌아온다.
4. 화면을 숨기는 것과 비우는 것의 차이. 레이아웃이 무너지는 문제.
5. **"얼마나 오래된 것까지 괜찮은가"는 개발자가 답할 수 있는 질문이 아니다.** 배너는 하루, 가격은 0초. 그 값을 아는 사람은 코드 밖에 있다.
6. 이 장에서 개발자가 혼자 고를 수 있는 것이 하나도 없음을 확인한다. 격리도, 타임아웃도, 회로 차단도 전부 **어떻게** 의 문제였지만 폴백은 **무엇을** 의 문제다.
7. `.nextq`: 그 무엇을 아는 사람은 누구인가. **기획자다.**

용어 `폴백` 을 심는다. 퀴즈 `data-qid="q-fallback"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 11 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "10장: 폴백은 '어떻게'가 아니라 '무엇을'의 문제다

앞의 넷은 개발자가 정할 수 있었지만 이것은 아니다. 얼마나 오래된 값까지
괜찮은지를 아는 사람은 코드 밖에 있다는 것이 3부로 가는 다리다."
```

---

### Task 13: 11장 · 기획서에는 정상 경로만 있다

**Files:**
- Modify: `defensive_programming.html` (`#specgap` 섹션)

**Interfaces:**
- Consumes: 없음.
- Produces: 없음. 이 장은 데모 없이 본문과 그림으로 간다.

- [ ] **Step 1: 본문을 쓴다**

1. 요건 문서의 구조적 편향. 화면 정의서는 "잘 됐을 때"의 그림이고, 정책서는 "정상적으로 판단할 때"의 규칙이다. 실패 화면에는 시안이 없다.
2. 실패 요건이 빠지는 이유 셋:
   - 기획자는 실패 모드를 모른다. 타임아웃이라는 것이 있는 줄 모르면 그것을 물을 수 없다.
   - 개발자는 그것이 자기 일이라고 생각해서 묻지 않는다. 그리고 실제로 매번 다르게 정한다.
   - 실패 요건은 화면이 없어서 검수 대상에도 오르지 않는다. 아무도 확인하지 않으므로 없어도 티가 나지 않는다.
3. **이번 사건**: "섹션 하나가 비면 무엇을 보여 준다"는 문장은 어디에도 없었다. 그래서 코드에도 없었다. 코드에 없는 이유가 개발자의 부주의가 아니라 **결정이 존재하지 않았다는 것**이다.
4. 실제 기획 문서의 한 문단을 각색해서 보여 주고, 그 안에 없는 결정을 형광펜으로 세어 본다.
5. 개발자만이 이것을 발견할 수 있는 위치에 있다. 기획자는 실패 모드를 볼 수 없고, QA 는 요건에 없는 것을 검사하지 않는다.
6. `.nextq`: 그러면 **무엇을** 물어야 하나.

퀴즈 `data-qid="q-specgap"`.

- [ ] **Step 2: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 3: 커밋**

```bash
git add defensive_programming.html
git commit -m "11장: 코드에 없었던 이유는 부주의가 아니라 결정이 없었다는 것이다

요건 문서가 정상 경로로만 채워지는 구조적 이유 셋을 짚었다. 실패 요건은
화면이 없어서 검수 대상에도 오르지 않는다."
```

---

### Task 14: 12장 · 개발자가 기획에게 물어야 할 열두 가지 (D9 · 질문 카드)

**Files:**
- Modify: `defensive_programming.html` (`#questions` 섹션)

**Interfaces:**
- Consumes: `Store` (Task 1)
- Produces: `window.QUESTIONS` — 열두 질문 배열. 13장의 요건 문장 빌더와 부록 C 가 **같은 배열을 쓴다.** 세 곳에 따로 적으면 하나만 고쳤을 때 아무 표시가 없다.

- [ ] **Step 1: 질문 배열을 만든다**

```js
/* ==== 열두 질문 — 12장·13장·부록 C 가 같은 배열을 쓴다 ==============
   세 곳에 따로 적으면 하나만 고쳤을 때 화면에는 아무 표시가 없다.
   ================================================================== */
const QUESTIONS = [
  {id:'q1',  axis:'데이터', q:'이 데이터가 하나도 없으면 화면에 무엇이 보입니까. 비웁니까, 숨깁니까, 대체물을 넣습니까',
   blocks:'빈 목록에 그려진 헤더만 남아 레이아웃이 무너지는 화면', ch:10, sec:'fallback'},
  {id:'q2',  axis:'데이터', q:'이 값이 오래된 것이어도 괜찮습니까. 몇 분까지 괜찮습니까',
   blocks:'품절된 상품이 재고 있음으로 보이는 캐시 폴백', ch:10, sec:'fallback'},
  {id:'q3',  axis:'데이터', q:'예상보다 많이 오면 어떻게 합니까. 상한이 있습니까',
   blocks:'응답 하나가 수만 건이 되어 메모리를 삼키는 조회', ch:4, sec:'boundary'},
  {id:'q4',  axis:'연동',   q:'이 정보를 주는 쪽이 응답하지 않으면 얼마나 기다립니까. 기다린 뒤에는 무엇을 합니까',
   blocks:'타임아웃 없는 호출 하나가 스레드 풀을 말리는 전염', ch:9, sec:'slowdown'},
  {id:'q5',  axis:'연동',   q:'그쪽이 틀린 값을 주면 우리는 어떻게 알아차립니까',
   blocks:'오늘 그 장애 — 문자열이 뷰까지 흘러간 경로', ch:4, sec:'boundary'},
  {id:'q6',  axis:'연동',   q:'이 화면에서 어느 부분이 없어도 화면이 성립합니까. 어느 부분이 없으면 화면을 띄우면 안 됩니까',
   blocks:'섹션 하나의 실패가 페이지 전체를 데려가는 조립', ch:8, sec:'failfast'},
  {id:'q7',  axis:'행위',   q:'이 버튼이 두 번 눌리면 어떻게 됩니까',
   blocks:'같은 주문이 두 건 들어가는 중복 제출', ch:9, sec:'slowdown'},
  {id:'q8',  axis:'행위',   q:'사용자가 중간에 이탈하면 이미 시작된 처리는 어떻게 됩니까',
   blocks:'결제는 됐는데 주문이 없는 상태', ch:7, sec:'swallow'},
  {id:'q9',  axis:'행위',   q:'절반만 성공하면 성공입니까 실패입니까. 사용자에게 무엇이라고 말합니까',
   blocks:'세 건 중 두 건만 담긴 장바구니에 뜬 "완료" 메시지', ch:8, sec:'failfast'},
  {id:'q10', axis:'한계',   q:'이 기능이 감당해야 하는 최대치는 얼마입니까. 넘으면 어떻게 합니까',
   blocks:'행사 시작 직후 몰린 요청에 전체가 멈추는 상황', ch:9, sec:'slowdown'},
  {id:'q11', axis:'한계',   q:'이 값이 0이거나 음수이거나 아주 크면 무엇이 맞습니까',
   blocks:'수량 0으로 계산된 금액과 음수 재고', ch:5, sec:'invariant'},
  {id:'q12', axis:'한계',   q:'실패했을 때 사용자에게 무엇을 보여 주고, 우리는 무엇을 남깁니까',
   blocks:'어느 섹션이었는지 적히지 않아 원인을 못 찾는 로그', ch:2, sec:'unknown'},
];
window.QUESTIONS = QUESTIONS;
```

- [ ] **Step 2: 질문 카드 데모를 만든다**

카드를 넘기며 각 질문이 막는 장애와 이 문서의 어느 장으로 이어지는지 보여 준다. 읽은 카드는 `Store` 에 남겨 다시 열었을 때 표시한다.

```js
(() => {
  const root = $('#qCards');
  root.innerHTML = QUESTIONS.map(q => `
    <div class="qcard" data-id="${q.id}">
      <div class="top"><span class="no">${q.axis}</span><a class="link" data-sec="${q.sec}">${q.ch}장</a></div>
      <p class="qq">${q.q}</p>
      <p class="qb">이 질문이 막는 것 — ${q.blocks}</p>
    </div>`).join('');
  // 앵커는 템플릿 보간이 아니라 여기서 붙인다. 보간으로 href 를 만들면
  // check_tutorial.py 의 앵커 검사가 `#${...}` 라는 문자열을 죽은 앵커로 읽는다.
  // 대신 이 링크들이 진짜 장을 가리키는지는 아래 Step 2 의 테스트가 본다.
  $$('a.link[data-sec]', root).forEach(a => a.setAttribute('href', '#' + a.dataset.sec));
})();
```

- [ ] **Step 2-1: 링크가 진짜 장을 가리키는지 보는 테스트를 더한다**

`tools/test_defensive_behavior.py` 끝에 붙인다.

```python
def test_every_question_points_at_a_real_chapter(page):
    """카드의 장 링크는 setAttribute 로 붙으므로 check_tutorial.py 의 앵커
    검사가 보지 못한다. 죽은 앵커를 놓치지 않도록 여기서 본다."""
    missing = page.evaluate(
        'QUESTIONS.map(q => q.sec).filter(s => !document.getElementById(s))')
    assert missing == []
```

- [ ] **Step 3: 본문을 쓴다**

1. 질문을 던지는 자리와 시점. 요건 리뷰이지 개발 착수 후가 아니다.
2. 네 축(데이터 · 연동 · 행위 · 한계)으로 묶은 이유. 축이 있으면 빠뜨린 것이 보인다.
3. 데모(위).
4. **여섯 번째 질문이 이 장의 급소다.** 이 질문 하나만 던졌어도 오늘 장애는 없었다. 8장의 여섯 번째 판단 카드와 `Assembly` 의 `critical` 이 전부 이 질문의 다른 얼굴이다.
5. 열두 번째 질문이 2장을 회수한다. 무엇을 남길지도 요건이다.
6. 질문을 던질 때의 태도. 심문이 아니라 결정을 요청하는 것이다. **"이건 어떻게 하죠"가 아니라 "이건 이렇게 하려는데 맞습니까"** 로 묻는다.
7. `.nextq`: 물었는데 **"그건 개발에서 알아서 해 주세요"** 라는 답이 오면.

퀴즈 `data-qid="q-questions"`.

- [ ] **Step 4: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과. 앵커 검사가 `CH_ID` 로 만든 링크를 잡으므로 열다섯 개 id 가 전부 존재해야 한다.

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming.html
git commit -m "12장: 열두 질문을 한 배열에 두고 12장·13장·부록 C 가 같이 쓴다

세 곳에 따로 적으면 하나만 고쳤을 때 화면에 아무 표시가 없다. 여섯 번째
질문은 8장의 판단 카드와 Assembly 의 critical 과 같은 것의 다른 얼굴이다."
```

---

### Task 15: 13장 · 답을 요건 문장으로 굳히는 법 (D10 · 요건 문장 빌더)

**Files:**
- Modify: `defensive_programming.html` (`#wording` 섹션)

**Interfaces:**
- Consumes: `QUESTIONS` (Task 14)
- Produces: 없음.

- [ ] **Step 1: 요건 문장 빌더를 만든다**

정상 경로 문장 하나를 놓고, 질문을 골라 답을 채우면 방어 요건 문장이 완성된다. 완성된 문장은 복사할 수 있어야 한다.

```js
(() => {
  // 네 칸을 채우면 문장이 된다. 칸이 비어 있으면 그 자리에 무엇이 빠졌는지
  // 그대로 보이게 둔다 — 빈칸이 보이는 것이 이 데모의 목적이다.
  const SLOTS = [
    {k:'when',  label:'조건',           ph:'예: 브랜드 위크 섹션의 데이터를 2초 안에 받지 못하면'},
    {k:'do',    label:'행동',           ph:'예: 그 섹션은 숨긴다'},
    {k:'show',  label:'사용자가 보는 것',ph:'예: 아무것도 표시하지 않고 아래 섹션이 올라온다'},
    {k:'keep',  label:'우리가 남기는 것',ph:'예: 섹션 식별자와 소요 시간을 경고로 남긴다'},
  ];
  const out = $('#wordOut');
  const val = {};

  function sentence(){
    const g = k => val[k] || `〈${SLOTS.find(s => s.k === k).label}〉`;
    return `${g('when')}, ${g('do')}. 사용자에게는 ${g('show')}. 시스템은 ${g('keep')}.`;
  }
  function render(){
    const filled = SLOTS.filter(s => val[s.k]).length;
    out.innerHTML = `
      <div class="reqout">${sentence()}</div>
      <div class="kv"><span class="k">채워진 칸</span><span>${filled} / 4</span></div>
      ${filled === 4
        ? `<button class="sm ghost" id="reqCopy">📋 문장 복사</button>
           <div class="verdict good">이 문장은 그대로 인수 조건이 되고, 그대로 테스트 이름이 됩니다.</div>`
        : `<div class="verdict warn">빈칸이 남아 있습니다. 빈칸으로 배포하면 그 결정은 코드를 쓰는 사람이 혼자 내리게 됩니다.</div>`}`;
    if(filled === 4){
      $('#reqCopy').addEventListener('click', () => {
        // 클립보드 API 는 file:// 에서 막히는 브라우저가 있다. 실패하면 선택으로 물러선다.
        const t = sentence();
        try{ navigator.clipboard.writeText(t); }catch(e){ window.getSelection().selectAllChildren($('.reqout', out)); }
      });
    }
  }
  // 각 칸은 <input> 이고 입력할 때마다 다시 그린다. 12장의 질문을 고르면
  // 그 질문에 해당하는 예시가 자리 표시자로 들어간다.
})();
```

- [ ] **Step 2: 본문을 쓴다**

1. **구두 합의는 방어가 아니다.** 문서에 남지 않은 결정은 다음 담당자에게 전달되지 않고, 다음 장애에서 다시 없는 상태가 된다.
2. 문장 형식을 하나로 고정한다.
   > 〈조건〉일 때 〈영역·기능〉은 〈행동〉한다. 사용자에게는 〈무엇〉을 보여 준다. 시스템은 〈무엇〉을 남긴다.
3. 예시를 이번 사건으로 든다. "브랜드 위크 섹션의 데이터를 2초 안에 받지 못하면 그 섹션은 숨긴다. 사용자에게는 아무것도 표시하지 않는다. 시스템은 섹션 식별자와 소요 시간을 경고 수준으로 남긴다."
4. 데모(위).
5. 인수 조건에 실패 케이스를 넣는 방법. Given/When/Then 으로 옮기면 **요건 문장이 그대로 테스트 이름이 된다.**
6. 협상 전략 셋:
   - **기본값을 제안한다.** "정해 주지 않으면 이렇게 하겠습니다"를 문서로 보낸다. 침묵이 반대가 아니라 승인이 되게 만든다.
   - **비용으로 말한다.** 추상적인 안정성이 아니라 오늘 있었던 일로 말한다.
   - **범위로 말한다.** 방어 요건은 추가 기능이 아니라 그 기능의 완성 조건이다.
7. `.nextq`: 이것을 **매번 개인이 기억해야 하나.**

퀴즈 `data-qid="q-wording"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과. `navigator.clipboard` 는 `check_tutorial.py` 의 네트워크 호출 목록에 없으므로 걸리지 않는다. 걸리면 그 자리에서 선택 방식으로 바꾼다.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "13장: 빈칸이 보이게 만든다 — 구두 합의는 방어가 아니다

네 칸을 채우면 요건 문장이 되고, 그 문장이 그대로 인수 조건과 테스트
이름이 된다. 빈칸으로 두면 그 결정은 코드를 쓰는 사람이 혼자 내린다."
```

---

### Task 16: 14장 · 팀의 절차로 만들기

**Files:**
- Modify: `defensive_programming.html` (`#process` 섹션)

**Interfaces:**
- Consumes: `QUESTIONS` (Task 14) · `Store` (Task 1)
- Produces: 없음.

- [ ] **Step 1: 체크리스트를 넣는다**

기존 튜토리얼의 `.ckl` 패턴을 쓴다(진행 상태를 `Store` 의 `ckl` 키에 저장한다). 항목은 완료 정의 · 설계 리뷰 · 회고 셋으로 묶는다.

- [ ] **Step 2: 본문을 쓴다**

1. 개인의 성실함에 기대는 방어는 사람이 바뀌면 사라진다.
2. 완료 정의에 넣을 항목: **"이 기능의 실패 요건 문장이 있는가."** 없으면 완료가 아니다.
3. 설계 리뷰의 고정 질문 목록. 12장의 열두 질문을 리뷰 템플릿으로 옮긴다.
4. **장애 회고의 산출물은 코드 수정이 아니라 요건 문장이어야 한다.** 코드만 고치면 다음 기능에서 같은 구멍이 다시 생긴다.
5. 이번 장애에서 나와야 할 요건 문장을 실제로 작성해 본다. 13장의 형식을 그대로 쓴다.
6. 어디서 멈추나. 열두 질문을 모든 기능에 다 던지면 아무것도 못 만든다. **던지는 기준**을 준다: 밖에서 데이터가 들어오는가, 그 화면이 여러 조각으로 조립되는가, 실패했을 때 되돌릴 수 없는 일이 일어나는가.
7. `.nextq`: 여기까지 왔으니 처음의 그 스택트레이스로 돌아간다.

난이도는 🔵. 퀴즈 `data-qid="q-process"`.

- [ ] **Step 3: 검사기와 테스트를 돌린다**

Run: Task 4 Step 3 과 같은 세 줄.
Expected: 전부 통과.

- [ ] **Step 4: 커밋**

```bash
git add defensive_programming.html
git commit -m "14장: 회고의 산출물은 코드 수정이 아니라 요건 문장이다

열두 질문을 모든 기능에 던지면 아무것도 못 만들므로, 언제 던지는지의
기준 셋을 함께 줬다."
```

---

### Task 17: 15장과 부록 A·B·C

**Files:**
- Modify: `defensive_programming.html` (`#recap` · `#ap-java` · `#ap-jsp` · `#ap-cards`)

**Interfaces:**
- Consumes: `RADIUS` · `paintRadius` (Task 1) · `QUESTIONS` (Task 14)
- Produces: 없음.

- [ ] **Step 1: 15장을 쓴다**

1. Hero 의 스택트레이스를 다시 띄운다. 이번에는 열 줄 옆에 **각 층이 무엇을 했어야 하는지**를 붙인다.
2. 반경 지도를 다시 그린다. 이번에는 구멍까지 함께 그린다.

```js
paintRadius($('#recapMap'), true);
```

3. 층마다 "여기서 막았다면 무엇이 달라졌는가"를 한 문단씩 회수한다.
4. **과잉 방어의 신호.** 모든 메서드가 인자를 검사하고, 모든 호출이 `try-catch` 에 싸여 있고, 모든 값이 `Optional` 이고, 테스트는 없는데 방어만 있는 상태. 방어가 코드를 읽을 수 없게 만들면 그것 자체가 장애 요인이다.
5. 멈추는 기준. **경계에서만 검사하고 안쪽은 신뢰한다.** 안쪽에서 또 검사하고 있다면 경계가 제 일을 못 하고 있다는 신호다.
6. 한 문장 정의로 닫는다.
7. 다음에 읽을 것으로 시리즈의 다른 문서를 잇는다. `auth_basics.html`(로그에 무엇을 담지 말아야 하는가) · `network_basics.html`(타임아웃이 실제로 무엇을 기다리는가).

15장은 사슬 밖이므로 `.nextq` 를 넣지 않는다. 검사기가 그것을 전제하고 있다.

- [ ] **Step 2: 부록 A · 자바·스프링 대응표를 쓴다**

개념 → 자바·스프링에서의 이름 → 한 줄 설명 → 그 개념을 다룬 장. 표 하나로 끝낸다. 개념을 다시 가르치지 않는다.

항목: `Objects.requireNonNull` · Bean Validation 과 `@Valid` · `@ControllerAdvice` 와 `@ExceptionHandler` · `Optional` 을 반환 타입으로만 쓰는 규칙 · 레코드와 정적 팩터리 · Resilience4j 의 `TimeLimiter` · `Bulkhead` · `CircuitBreaker` · `Retry` · HTTP 클라이언트의 연결 타임아웃과 읽기 타임아웃 · 트랜잭션 경계와 예외의 관계.

- [ ] **Step 3: 부록 B · JSP·EL 환경에서의 방어를 쓴다**

1. EL 이 `null` 과 타입 불일치를 다르게 대하는 규칙. 1장 데모의 다섯 경우를 표로 정리한다.
2. `<c:catch>` 가 할 수 있는 것과 못 하는 것. 태그 안에서 난 예외는 잡지만, **이미 나간 출력은 되돌리지 못한다.**
3. include 단위로 섹션을 가르는 방법과 그 대가.
4. 응답 버퍼 커밋과 오류 페이지의 관계. 버퍼 크기를 키우면 미룰 수 있지만 없앨 수는 없다.
5. 뷰에서 방어하는 것이 왜 마지막 수단인지. 여기까지 온 값은 이미 네 단계를 통과했다.

- [ ] **Step 4: 부록 C · 질문 카드를 쓴다**

`QUESTIONS` 배열에서 그린다. 인쇄해서 쓸 수 있게 `@media print` 를 더한다.

```css
@media print{
  #sidebar, .menu-btn, .demo, .quiz, #glossary, .scrim{display:none !important}
  #ap-cards{display:block}
  body{background:#fff; color:#000}
  .qcard{break-inside:avoid; border:1px solid #999; margin:0 0 8px; padding:10px}
}
```

- [ ] **Step 5: 검사기와 테스트를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py tools/test_defensive_behavior.py -v
python3 tools/check_dead_css.py defensive_programming.html
```
Expected: 전부 통과.

- [ ] **Step 6: 커밋**

```bash
git add defensive_programming.html
git commit -m "15장과 부록 셋: 반경 지도를 구멍까지 그려 회수하고, 멈출 지점을 준다

과잉 방어의 신호와 멈추는 기준을 마지막에 뒀다. 안쪽에서 또 검사하고
있다면 경계가 제 일을 못 하고 있다는 신호다."
```

---

### Task 18: 용어집 완성, 각색 전수 검색, 완주 검사

**Files:**
- Modify: `defensive_programming.html`

**Interfaces:**
- Consumes: 앞의 모든 태스크
- Produces: 없음.

- [ ] **Step 1: 용어집을 채운다**

`GLOSSARY` 에 다음을 넣는다. `// @GLOSSARY_END` 앞이다.

신뢰 경계 · 불변식 · 사전조건 · 사후조건 · 방어적 복사 · 값 타입 · fail-fast · fail-soft · 우아한 저하 · 조용한 실패 · 격벽 · 회로 차단기 · 멱등성 · 지수 백오프 · 지터 · 폴백 · 진단 가능성 · 응답 커밋 · EL · 리플렉션.

정의는 한 문단으로 쓰되, **그 용어가 이 문서의 어느 장에서 쓰이는지**를 마지막 문장에 넣는다.

- [ ] **Step 2: 각색 규칙을 전수 검색한다**

Run:
```bash
grep -ni -E 'cheil|ssfshop|dspcnr|conttimg|includemultimaincontents|securevalueexpression|전시 ?코너' defensive_programming.html
```
Expected: 출력 없음. 하나라도 나오면 그 자리에서 고친다.

Run:
```bash
grep -c -E 'javax\.el|BeanELResolver|9946|_005fset_005f141' defensive_programming.html
```
Expected: 0 이 아니다. 각색하다가 증거까지 지웠는지 확인한다.

- [ ] **Step 3: 전체 검사를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 tools/check_dead_css.py defensive_programming.html
python3 -m pytest tools/test_defensive_document.py tools/test_defensive_behavior.py -v
```
Expected: `OK`, 죽은 CSS 없음, pytest 전부 PASS.

- [ ] **Step 4: 완주 검사를 한다**

브라우저에서 `defensive_programming.html` 을 열고 처음부터 끝까지 스크롤한다. 확인할 것:

- 목차가 열여덟 개 항목으로 자동 생성되고, 스크롤에 따라 현재 장이 표시되는가
- 진행률이 올라가고, 새로고침해도 남는가
- D1~D10 을 전부 조작해도 콘솔에 오류가 없는가
- **D6 이 6·9·10장에서 각각 다른 조작만 노출하는가**, 그리고 한 장에서 조작한 것이 다른 장의 상태를 건드리지 않는가
- 용어에 마우스를 올리면 설명이 뜨고, 용어집 서랍이 열리는가
- 퀴즈 열네 개가 채점되고 해설이 펼쳐지는가
- `.stack` 블록을 전부 접은 채로 읽어도 논지가 끊기지 않는가
- 좁은 화면(모바일 폭)에서 사이드바가 접히고 데모가 넘치지 않는가

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming.html
git commit -m "용어집 스무 항목, 각색 전수 검색, 완주 검사

각색 규칙을 grep 으로 전수 확인했고, 남겨야 하는 증거가 지워지지
않았는지도 반대 방향으로 확인했다."
```

---

### Task 19: index.html 에 아홉 번째 카드를 단다

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: 없음.
- Produces: 없음.

- [ ] **Step 1: 색 변수를 더한다**

`:root` 에 이 문서의 색을 더한다. 기존 여덟 개와 겹치지 않는 색을 고른다.

```css
--defp:#f472b6;
```

- [ ] **Step 2: 카드를 넣는다**

기존 카드와 같은 구조로, **마지막 자리**에 넣는다. 이 문서는 시리즈의 다른 문서를 전제하지 않으므로 순서상 앞에 둘 이유가 없고, 가장 최근 문서라는 표시가 자연스럽다.

```html
<a class="card" href="defensive_programming.html" style="--c:var(--defp)">
  <div class="top">
    <span class="ic">🛡️</span>
    <span class="no">Defensive</span>
    <span class="new">NEW</span>
  </div>
  <h2>방어적 프로그래밍 — 하나가 죽었을 때 전체가 죽지 않게</h2>
  <p><b>전시 섹션 하나가 오류를 내서 메인페이지 전체가 죽었습니다.</b>
  스택트레이스가 가리키는 곳에는 범인이 없다는 사실에서 출발해,
  방어의 반경을 한 줄에서 요구사항까지 여섯 번 넓혀 갑니다.
  <code>try-catch</code>를 더 뿌리는 이야기가 아니라
  <b>어느 경계에서 실패를 멈출지 정하는 설계</b>의 이야기이고,
  마지막 파트에서는 코드를 떠나 기획 요건에 방어 조항을 넣는 데까지 갑니다.</p>
  <div class="tags">
    <i>신뢰 경계</i><i>조용한 실패</i><i>불변식</i><i>실패 격리</i>
    <i>fail-fast · fail-soft</i><i>타임아웃 · 격벽</i><i>폴백</i><i>요건 문장</i>
  </div>
  <span class="go">열어 보기 <span class="ar">→</span></span>
</a>
```

- [ ] **Step 3: 머리말의 문서 개수를 고친다**

`🗂️ 8개 문서` 를 `🗂️ 9개 문서` 로 바꾼다. `<meta name="description">` 의 목록에도 방어적 프로그래밍을 더한다.

- [ ] **Step 4: 검사를 돌린다**

Run:
```bash
python3 tools/check_tutorial.py index.html defensive_programming.html
python3 tools/check_dead_css.py index.html
```
Expected: 둘 다 `OK`.

브라우저에서 `index.html` 을 열어 카드가 다른 여덟 개와 같은 모양으로 서고, 링크가 열리는지 확인한다.

- [ ] **Step 5: 커밋**

```bash
git add index.html
git commit -m "허브에 아홉 번째 카드 — 방어적 프로그래밍

문서 개수와 meta description 도 함께 고쳤다."
```

---

## 자체 점검 기록

**1. 설계 문서 대조.** 설계 문서의 절마다 담당 태스크가 있다.

| 설계 문서 | 담당 |
|---|---|
| 2절 척추 · Hero | Task 1 |
| 3절 각색 규칙 | Task 1(검사기) · Task 18(전수 검색) |
| 4절 `.stack` 규칙 | Task 1(CSS·검사기) · Task 4·6·7·9·11 이후 각 장 |
| 5절 두 축 | Task 10(8장에서 명제로 못 박음) |
| 7절 1~15장 | Task 3~17 |
| 7절 부록 A·B·C | Task 17 |
| 8절 데모 D1~D10 | D1·D4·D6 은 순수 함수(Task 2·3·6), 나머지는 각 장 |
| 9절 문서 구조 | Task 1 |
| 10절 통과 기준 | Task 1·2 의 테스트 파일과 Task 18 |
| 11절 작업 순서 확인 지점 셋 | Task 1 끝 · Task 2 끝 · Task 15 끝 |

**2. 자리 표시자.** `TBD` · `TODO` · "적절히" · "나중에" 는 없다. 본문 산문은 논지 목록으로 지정했다. 산문은 코드가 아니므로 문장을 그대로 박지 않고 담아야 할 논지와 순서를 못 박았으며, 각 항목의 근거는 설계 문서 7절에 있다.

**3. 이름 일관성.** 태스크를 가로지르는 이름을 대조했다.

- `Assembly.assemble(faults, strategy)` — Task 2 에서 정의, Task 8·11·12 에서 사용. 반환의 `pageState` · `rendered` · `totalMs` · `failedAt` 이 테스트와 렌더러에서 같은 철자다.
- `renderAssembly(rootSel, opts)` — Task 8 에서 정의, Task 11·12 에서 `opts.controls` 와 `opts.preset` 으로 사용.
- `EL.resolve(kind, prop)` — Task 3 에서 정의, Task 5(3장)에서 논지로 재사용.
- `Pipeline.run(guardAt)` — Task 6 에서 정의.
- `QUESTIONS` — Task 14 에서 정의(`id`·`axis`·`q`·`blocks`·`ch`·`sec`), Task 15·17 에서 사용. `sec` 는 섹션 id 문자열이고 `test_every_question_points_at_a_real_chapter` 가 그것이 실재하는 장인지 대조한다.
- `RADIUS` · `paintRadius(root, withHoles)` — Task 1 에서 정의, Task 17 에서 `withHoles=true` 로 재사용.
- 섹션 id 열여덟 개 — Task 1 의 표가 유일한 출처이고 `tools/test_defensive_document.py` 의 `CHAPTERS` 가 그것을 강제한다.
- 저장소 키 — 전부 `defprog:` 접두사. Task 1 에서 정하고 검사기가 확인한다.
