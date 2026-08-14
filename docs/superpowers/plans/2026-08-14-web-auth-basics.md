# 웹 애플리케이션 인증 기초 튜토리얼 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `https_tutorial.html`과 `oauth2_tutorial.html` 사이의 빈 층을 채우는 단일 HTML 튜토리얼 `auth_basics.html`을 만든다. 무상태 HTTP에서 출발해 세션·쿠키·클러스터링·JWT를 문제의 사슬로 잇고, OAuth 문서로 인계한다.

**Architecture:** 외부 의존성 0인 단일 HTML 파일. `aws_network_security.html`의 골격(사이드바·목차 자동생성·진행률·스크롤스파이·용어사전·퀴즈)만 발췌해 옮기고, 그 문서 전용 컴포넌트는 가져오지 않는다. 본문은 프레임워크 중립으로 쓰고 Spring은 각 장 끝의 접이식 `.spring` 블록으로 분리한다.

**Tech Stack:** 순수 HTML/CSS/JS(ES2015+), 임베딩 Prism(core+clike+bash+java), `localStorage`. 빌드 도구 없음. 검증은 `tools/check_tutorial.py`(기존)와 `tools/check_dead_css.py`(이 계획에서 신규).

**Spec:** [`docs/superpowers/specs/2026-08-14-web-auth-basics-design.md`](../specs/2026-08-14-web-auth-basics-design.md)

**Facts:** [`docs/superpowers/notes/2026-08-14-auth-facts.md`](../notes/2026-08-14-auth-facts.md) — **사실을 서술하기 전에 반드시 읽는다.**

---

## Global Constraints

이 절의 모든 항목은 **모든 태스크의 요구사항에 암묵적으로 포함된다.**

- **외부 의존성 0.** `<script src>`, `<link href>`, `@import`, `url(https://...)`, `fetch`, `XMLHttpRequest`, `new Image()`, `new WebSocket`, `navigator.sendBeacon` 전부 금지. `file://`로 열어도 완전히 동작해야 한다.
- **저장소 키 접두어는 `authbasic:`.** 다른 문서의 키와 충돌하면 안 된다.
- **모든 `<section>`은 `id`와 `data-title`을 가진다.** 목차가 이것으로 자동 생성된다.
- **모든 `id`는 문서 안에서 유일하다.**
- **퀴즈는 `.quiz[data-qid][data-answer]` 형태이고, `data-answer` 값에 해당하는 `.opt[data-opt]`가 실제로 있어야 하며, `.explain`이 있어야 한다.**
- **`class="term"`인 요소의 `data-t` 값은 전부 `GLOSSARY`에 있어야 한다.** `GLOSSARY` 객체는 `// @GLOSSARY_END` 마커로 끝난다.
- **`<title>`과 `<meta name="description">`이 있어야 한다.**
- **사실 서술은 facts 파일을 근거로 한다.** 특히 아래 넷은 **통념이 틀린 곳**이라 기억으로 쓰면 안 된다.
  - Spring Session 기본 쿠키명은 **`SESSION`** (`JSESSIONID` 아님)
  - `SameSite` 미지정 기본값은 **"일부" 브라우저만 `Lax`**이고, 기본 적용된 `Lax`는 명시한 `Lax`보다 **느슨하다**(설정 후 2분 내 교차 사이트 `POST` 허용)
  - CSRF 보호 대상 메서드가 **서블릿(`GET`·`TRACE`·`HEAD`·`OPTIONS` 제외 전부)과 리액티브(`PUT`·`POST`·`DELETE`)에서 다르다**
  - Spring Security 6의 `requireExplicitSave` 기본값은 **true** (`SecurityContextHolderFilter`는 읽기 전용)
- **서술 금지 항목** (확인 실패 — facts 파일 V1 후반·V8):
  - JWT 관련 **CVE 번호, 특정 라이브러리 이름, 버전**을 쓰지 않는다
  - Spring **내장 폼 로그인 필터가 컨텍스트를 저장하는 내부 경로**를 서술하지 않는다
- **난이도 배지**: `<span class="lvl must">🟢 필수</span>` / `<span class="lvl adv">🔵 심화</span>`
- **접근성**: `:focus-visible` 아웃라인과 `prefers-reduced-motion` 대응을 골격에서 물려받고 깨뜨리지 않는다.

### 매 태스크의 검증 명령 (이하 "표준 검증")

```bash
python3 tools/check_tutorial.py --allow-missing-anchors auth_basics.html
python3 tools/check_dead_css.py auth_basics.html
```

`--allow-missing-anchors`는 문서를 장별로 쌓는 동안 아직 없는 섹션을 가리키는 링크를 유예한다. **Task 13에서 이 플래그를 뗀다.**

---

## File Structure

| 파일 | 책임 | 상태 |
|---|---|---|
| `auth_basics.html` | 문서 전체 (마크업·스타일·스크립트) | 신규 |
| `tools/check_dead_css.py` | CSS에 정의됐지만 안 쓰이는 클래스 검출 | 신규 |
| `index.html` | 시리즈 목록에 카드 추가 | 수정 |
| `docs/superpowers/notes/2026-08-14-known-issues.md` | 남은 것 기록 | Task 15에서 수정 |

`auth_basics.html` 내부 구획 (골격 이식 후 고정):

| 구획 | 내용 |
|---|---|
| `<style id="prism-theme">` | Prism 테마. **손대지 않는다.** |
| `<style>` #1 | 디자인 시스템 — 토큰·레이아웃·사이드바·타이포·데모/퀴즈/용어사전 공용 |
| `<style>` #2 | 이 문서 전용 컴포넌트 (`.spring` 포함). **장별 태스크가 여기에만 추가한다.** |
| `<body>` | `.menu-btn` → `.layout`(`#sidebar` + `#content`) → `#scrim` → `#glossary` → `#tooltip` |
| `<script>` #1 | 임베딩 Prism. **손대지 않는다.** |
| `<script>` #2 | `GLOSSARY` → 런타임(목차·진행률·스파이·툴팁·용어사전·퀴즈·`wireTogs`/`wirePicker`) → 장별 데모 IIFE |

---

### 왜 "복제 후 삭제"가 아니라 "발췌 이식"인가

계획 수립 중 골격 파일을 실측했다. `aws_network_security.html`은 CSS 클래스 **226개를 정의하고 95개만 쓴다 — 131개(58%)가 사장 코드다.** known-issues 노트가 적어 둔 "약 34%"보다 크다.

그대로 복제하면 그 131개를 그대로 물려받고, 이후 어느 시점에도 무엇이 새 문서의 것이고 무엇이 딸려 온 것인지 구분할 수 없게 된다. **그래서 Task 1은 복제가 아니라 발췌다.** 그리고 같은 일이 조용히 반복되지 않도록 검사기를 하나 추가한다.

---

## Task 1: 골격 이식 + 사장 CSS 검사기

**Files:**
- Create: `tools/check_dead_css.py`
- Create: `auth_basics.html`
- Reference (읽기 전용): `aws_network_security.html`

**Interfaces:**
- Produces: `auth_basics.html`의 고정 구획(위 표), 저장소 접두어 `authbasic:`, 전역 헬퍼 `$`, `$$`, `LS`, `esc`, `wireTogs(sel, onChange)`, `wirePicker(sel, onPick)`. 이후 모든 장 태스크가 이것들을 쓴다.
- Produces: `python3 tools/check_dead_css.py <file>` — 미사용 클래스가 있으면 종료 코드 1.

- [ ] **Step 1: 사장 CSS 검사기를 만든다**

`tools/check_dead_css.py`:

```python
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
```

- [ ] **Step 2: 검사기가 기존 파일의 문제를 실제로 잡는지 확인한다**

Run: `python3 tools/check_dead_css.py --report aws_network_security.html`

Expected: `WARN aws_network_security.html: 정의 226 · 사용 95 · 미사용 131` 그리고 `.ar-col` `.ladder` `.esc-grid` `.tag-card` 등이 목록에 있다.

**숫자가 다르면 멈추고 검사기를 고친다.** 이 수치가 Task 1의 나머지 판단 기준이다.

- [ ] **Step 3: 골격을 발췌해 `auth_basics.html`을 만든다**

`aws_network_security.html`에서 **아래 것만** 옮긴다.

*그대로 옮기는 것:*
- `<style id="prism-theme">` 블록 전체 (8~10행)
- 디자인 시스템 CSS 중 **공용 부분만**: `:root` 토큰, `*`/`html`/`body` 기본, `.layout`, `#sidebar`, `.brand`, `.logo`, `.dot`, `.sub`, `.progress-wrap`, `.progress-line`, `.progress-bar`, `#toc`(및 그 하위), `.side-tools`, `.sm`, `.ghost`, `.menu-btn`, `#content`, `.sec-head`, `.kicker`, `h2.sec-title`, `.lead`, `.hero`, `.chips`, `.chip`, `.callout`(+`.why` `.must` `.adv` `.myth`), `.kv`, `.map-grid`, `.map-card`, `.ic`, `.demo`, `.demo-tag`, `.picker`, `.pick`, `.quiz`, `.q-head`, `.q`, `.opt`, `.mk`, `.explain`, `.correct`, `.wrong`, `.term`, `#tooltip`(`.tip` `.tt`), `#glossary`(`.g-head` `.g-body`), `#scrim`, `.ckl`, `.ck`, `.ck-score`, `.done`, `.diag`, `.d-item`, `.d-txt`, `.d-yes`, `.diag-result`, `.lvl`(+`.must` `.adv`), `.link`, `.mono`, `.dim`, `.oneline`, `.badge`, `.verdict`, `.ok`, `.bad`, `.warn`, `.on`, `.open`, `.active`, `.show`
- **`@media(max-width:980px)` 블록 전체** — `#sidebar`의 `z-index:160`이 여기 있다. **이것이 모바일 드로어 버그가 고쳐진 유일한 곳이다. 값을 바꾸지 않는다.** (`#scrim`은 150, `.menu-btn`은 60)
- 그 밖의 `@media` 블록 중 위 목록의 클래스에 걸리는 것
- `<body>` 뼈대: `.menu-btn#menuBtn` → `.layout`(`#sidebar` + `#content`) → `#scrim` → `#glossary` → `#tooltip`
- 임베딩 Prism `<script>` 블록
- 런타임 JS 전부: `$`, `$$`, `LS`, `esc`, 목차 자동생성, `markVisited`, `IntersectionObserver` 스파이, `solved`/`updateProgress`, 툴팁, 용어사전 드로어, 키보드 핸들러, `wireTogs`, `wirePicker`

*옮기지 않는 것:*
- 장별 데모 IIFE 전부
- 사장 CSS 131개 (Step 2의 목록)
- AWS 문서 전용 컴포넌트: `.cc-*` `.ol-*` `.m-row` `.m-txt` `.m-x` `.vmodel` `.vres` `.vwhy` `.ct` `.cb` `.cmp2` `.cmp-col` `.flow-step` `.tog` `.tog-col` `.seg-chip` `.std` `.t` `.d` — **쓸 자리가 생기면 그때 새로 쓴다**

*바꾸는 것:*
- `LS`의 접두어 `"netsec:"` → `"authbasic:"`
- `<title>`: `웹 애플리케이션 인증 기초 — 서버는 나를 어떻게 기억하는가`
- `<meta name="description">`: `서버를 두 대로 늘렸더니 자꾸 로그아웃되는 이유에서 출발하는 웹 인증 인터랙티브 튜토리얼. 무상태 HTTP·세션·쿠키·CSRF·세션 클러스터링·JWT가 왜 차례로 필요해졌는지 직접 눌러 확인합니다.`
- 사이드바 `.brand`: 로고 `AUTH·BASICS`, `<h1>웹 애플리케이션 인증 기초</h1>`, `.sub`는 `무상태 · 세션 · 쿠키 · 클러스터링 · JWT`
- Prism 컴포넌트에 `java` 추가 (core+clike+bash+java)
- `GLOSSARY`를 빈 객체로 비우되 **`// @GLOSSARY_END` 마커는 남긴다**
- `#content`에는 임시로 `<section id="intro" data-title="개요" class="hero"><h2 class="sec-title">임시</h2></section>` 하나만 둔다

- [ ] **Step 4: 이 문서 전용 컴포넌트 `.spring`을 두 번째 `<style>` 블록에 추가한다**

```css
/* ============================================================
   이 문서 전용 컴포넌트
   ============================================================ */

/* Spring 대응 블록 — 접이식. 본문은 프레임워크 중립이고,
   이 블록만 Spring의 이름을 잇는다. 통째로 건너뛰어도 논지가 끊기지 않아야 한다. */
.spring{
  margin:18px 0; border:1px solid var(--border); border-radius:12px;
  background:linear-gradient(180deg, rgba(129,140,248,.06), transparent);
  overflow:hidden;
}
.spring>summary{
  list-style:none; cursor:pointer; padding:11px 15px; font-size:14px; font-weight:700;
  color:var(--text-dim); display:flex; align-items:center; gap:8px;
}
.spring>summary::-webkit-details-marker{display:none}
.spring>summary::before{content:"🍃"; font-size:14px}
.spring>summary::after{content:"▸"; margin-left:auto; transition:transform .18s; color:var(--text-mut)}
.spring[open]>summary::after{transform:rotate(90deg)}
.spring>summary:hover{color:var(--text)}
.spring>summary:focus-visible{outline:2px solid var(--accent); outline-offset:-2px}
.spring .sp-body{padding:2px 15px 14px; font-size:14.5px; color:var(--text-dim); line-height:1.8}
.spring .sp-body>*:first-child{margin-top:0}
.spring .sp-body>*:last-child{margin-bottom:0}
.spring code{font-family:var(--mono); font-size:.88em}
```

사용 형태 (장별 태스크가 이 모양을 그대로 쓴다):

```html
<details class="spring">
  <summary>Spring에서는 이 이름이다</summary>
  <div class="sp-body">
    <p>…</p>
  </div>
</details>
```

- [ ] **Step 5: 표준 검증을 돌린다**

```bash
python3 tools/check_tutorial.py --allow-missing-anchors auth_basics.html
python3 tools/check_dead_css.py auth_basics.html
```

Expected: 양쪽 다 `OK`. **`check_dead_css.py`가 클래스를 하나라도 뱉으면 그것을 지우고 다시 돌린다.** 이 시점에 미사용이 0이어야 이후 장들이 추가하는 것만 감시된다.

- [ ] **Step 6: 브라우저로 골격을 확인한다**

`file://` 경로로 `auth_basics.html`을 연다. 확인할 것:
1. 사이드바가 보이고 목차에 "개요" 한 줄이 있다
2. 개발자 도구 네트워크 탭에 **요청이 0건**이다
3. 창을 900px 이하로 줄이면 `☰ 목차` 버튼이 나타나고, 눌러 연 드로어에서 **"개요" 항목이 실제로 눌린다** (스크림에 가려지지 않는다)
4. 콘솔에 에러가 없다

- [ ] **Step 7: 커밋**

```bash
git add tools/check_dead_css.py auth_basics.html
git commit -m "골격: auth_basics.html 뼈대와 사장 CSS 검사기

aws_network_security.html은 CSS 클래스 226개를 정의하고 95개만 쓴다.
복제하면 그 131개를 그대로 물려받으므로, 복제가 아니라 공용 골격만
발췌해 옮겼다. 같은 일이 조용히 반복되지 않도록 검사기를 함께 넣는다."
```

---

## Task 2: Hero — 증상 제시와 되감기

**Files:**
- Modify: `auth_basics.html` — `#content`의 `#intro` 섹션 교체

**Interfaces:**
- Consumes: Task 1의 `.hero` `.kicker` `.sec-title` `.lead` `.chips` `.chip` `.callout` `.diag` `.d-item` `.d-txt` `.d-yes` `.diag-result` `.pick` `.map-grid` `.map-card` `.ic`, `LS`, `wirePicker`
- Produces: 섹션 `#intro`. 자가진단 데모 `#diag` (저장 키 `diag`). 15장이 이 결과를 회수한다.

- [ ] **Step 1: Hero 섹션 마크업을 쓴다**

`<section id="intro" data-title="개요" class="hero">` 안에 순서대로:

1. `.kicker` — `HTTPS를 아는 개발자 → 로그인을 설계하는 개발자`
2. `h2.sec-title` — `서버를 두 대로 늘렸더니<br>자꾸 로그아웃된다`
3. `.lead` 두 문단. **증상을 구체적으로**: 서버 한 대일 때는 멀쩡했고, 오토스케일로 두 대가 된 뒤부터 사용자들이 "가끔" 로그아웃된다고 한다. 재현이 안 된다. 로그에는 아무것도 없다.
4. `.lead` — 되감기 선언: *"이 증상은 세션이 무엇인지 알면 10초 만에 설명됩니다. 그런데 그 설명은 훨씬 앞에서 시작해야 해요 — **서버는 애초에 나를 어떻게 기억하는가**에서."*
5. `.chips` 다섯 개: `🕳️ 증표가 필요해지기까지 — 1부 6장` / `💥 서버가 여러 대가 되면 — 2부 3장` / `🎫 상태 없는 증표 — 3부 3장` / `🖱️ 쿠키·세션·토큰을 눌러가며 추적` / `🟢 필수 / 🔵 심화 경로 표시`
6. `.callout.why` — 이 튜토리얼의 한 문장: *인증을 안다는 것은 `formLogin()`을 쓸 줄 안다는 뜻이 아니다. **매 요청이 스스로 신원을 증명해야 한다는 제약**과, 그 제약을 푸는 방법들이 각각 무엇을 대가로 치르는지 짝지을 수 있다는 뜻이다.*
7. `<h3>🩺 시작 전 30초 자가진단</h3>` + `.diag#diag`
8. `<h3>무엇을 다루나</h3>` + `.map-grid` (4부 구성)

- [ ] **Step 2: 자가진단 항목 6개를 쓴다**

각 항목은 `<div class="d-item"><div class="d-txt">…</div><button class="pick d-yes" data-w="N">그렇다</button></div>` 형태. 마지막에 `<div class="diag-result" id="diagResult"></div>`.

| 항목 | 가중치 |
|---|---|
| 세션과 JWT 중 무엇을 쓸지 **정하는 기준**을 한 문장으로 말하기 어렵다 | 3 |
| `HttpOnly`·`Secure`·`SameSite`가 **각각 어떤 공격**을 막는지 구분해 말하기 어렵다 | 3 |
| JWT로 **강제 로그아웃**을 어떻게 구현하는지 답하기 어렵다 | 3 |
| `@AuthenticationPrincipal`에 **무엇이 어떻게** 담기는지 설명하기 어렵다 | 2 |
| 세션을 Redis로 옮겨 본 적이 **없다** | 2 |
| CSRF 방어를 **꺼 본 적이 있다** (이유는 정확히 기억나지 않는다) | 1 |

- [ ] **Step 3: 자가진단 채점 IIFE를 쓴다**

`wirePicker`가 아니라 토글이므로 직접 쓴다. 요구사항:
- `.d-yes` 클릭 시 `on` 클래스를 토글하고 `aria-pressed`를 갱신한다
- 켜진 항목의 `data-w` 합계로 `#diagResult` 문구를 바꾼다: `0` → *"이 문서는 복습용입니다. 7~9장부터 보셔도 됩니다."* / `1~5` → *"절반쯤 아는 상태예요. 순서대로 읽으시면 빈 곳이 메워집니다."* / `6~14` → *"이 문서가 정확히 겨냥하는 자리입니다. 1장부터 가세요."*
- 선택 상태를 `LS.set('diag', [...])`로 저장하고, 로드 시 복원한다
- **`aria-pressed`를 반드시 넣는다** — known-issues §4가 지난 문서의 미비점으로 지목한 항목이다

- [ ] **Step 4: 표준 검증**

Expected: 양쪽 `OK`. `check_dead_css.py`에 새 클래스가 뜨면 그 CSS를 쓰거나 지운다.

- [ ] **Step 5: 브라우저 확인**

항목을 눌러 결과 문구가 세 구간 모두에서 바뀌는지, 새로고침 후 선택이 유지되는지 확인한다.

- [ ] **Step 6: 커밋**

```bash
git add auth_basics.html
git commit -m "1장 앞: Hero — 두 대로 늘렸더니 로그아웃되는 증상에서 출발"
```

---

## Task 3: 1장 무상태 · 2장 자격 증명

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 1의 공용 컴포넌트, `wirePicker`
- Produces: 섹션 `#stateless`, `#credentials`. 퀴즈 `q-stateless`, `q-credentials`. 용어 `무상태`, `salt`, `work factor`.

- [ ] **Step 1: 1장 섹션을 쓴다**

`<section id="stateless" data-title="HTTP는 기억하지 못한다">`, kicker `01 · 제약`, 제목 `🕳️ HTTP는 방금 그 사람을 기억하지 못한다 <span class="lvl must">🟢 필수</span>`

말해야 하는 것:
- 요청 둘은 서로 남남이다. 서버 입장에서 두 번째 요청은 첫 번째를 본 적이 없다.
- keep-alive로 TCP 커넥션을 재사용해도 **그것은 신원이 아니다.** 커넥션은 성능의 문제고 신원은 별개다.
- "IP로 구분하면?" — NAT 뒤에서 수천 명이 한 IP를 공유하고, 모바일은 이동하며 IP가 바뀐다.
- 결론: **매 요청이 스스로 신원을 증명해야 한다.** 이것이 이후 모든 장의 제약이다.

- [ ] **Step 2: 1장 데모 `#reqView`를 만든다**

`.demo#reqView`, `.demo-tag` = `서버가 보는 것 전부`

- `.picker`로 요청 3개 선택: `첫 번째 요청` / `두 번째 요청(같은 사람)` / `세 번째 요청(다른 사람)`
- 선택하면 서버가 그 요청에서 볼 수 있는 것을 목록으로 보인다: 메서드, 경로, `Host`, `User-Agent`, `Accept-*`, 출발지 IP·포트, TLS 정보
- **핵심**: 1번과 2번이 **구별 불가능**하게 표시되어야 한다. 출발지 포트만 다르고 그건 매번 바뀐다.
- 하단 판정 문구: *"이 중에 '누구인가'를 말해 주는 것은 없습니다."*

- [ ] **Step 3: 1장 퀴즈를 쓴다**

```html
<div class="quiz" data-qid="q-stateless" data-answer="c">
  <div class="q-head">✅ 체크포인트</div>
  <div class="q">같은 브라우저가 keep-alive 커넥션 하나로 요청을 연달아 두 번 보냈다. 서버가 두 요청을 같은 사람의 것으로 <b>확신</b>할 수 있는 근거는?</div>
  <button class="opt" data-opt="a"><span class="mk">A</span> 출발지 IP가 같다</button>
  <button class="opt" data-opt="b"><span class="mk">B</span> 같은 TCP 커넥션을 썼다</button>
  <button class="opt" data-opt="c"><span class="mk">C</span> 없다 — 요청 스스로가 신원을 담아야 한다</button>
  <button class="opt" data-opt="d"><span class="mk">D</span> User-Agent가 같다</button>
  <div class="explain"><b>정답 C.</b> …</div>
</div>
```

`.explain`에 반드시 담을 것: A는 NAT·프락시 뒤에서 무너진다. **B가 가장 그럴듯해서 위험하다** — 커넥션 재사용은 전송 계층의 최적화일 뿐이고, 프락시나 로드밸런서가 커넥션을 갈아 끼우는 순간 사라진다. D는 위조가 자유롭다.

- [ ] **Step 4: 2장 섹션을 쓴다**

`<section id="credentials" data-title="자격 증명을 확인한다">`, kicker `02 · 첫 시도`, 제목 `🔐 그럼 매 요청에 아이디·비번을 보내면 안 되나 <span class="lvl must">🟢 필수</span>`

말해야 하는 것:
- 실제로 그런 방식이 있다 — HTTP Basic. `Authorization: Basic <base64(id:pw)>`
- **base64는 암호가 아니다.** 되돌리는 데 열쇠가 필요 없다. → HTTPS 문서 회수: 그래서 TLS가 전제다. 다시 설명하지 않고 이름만 부른다.
- 문제 셋: ① 비번이 매 요청마다 네트워크에 흐른다 ② 서버가 매 요청마다 검증해야 한다 ③ **로그아웃이라는 개념이 아예 없다** — 브라우저가 기억하는 것을 지울 방법이 규격에 없다
- ②에서 비밀번호 저장으로: 평문 저장 → 유출 시 전부 끝 → 해시 → **레인보우 테이블** → salt → 그래도 GPU가 초당 수십억 번 → **일부러 느린 해시**(bcrypt·argon2)와 work factor
- **핵심 프레이밍**: *"느린 것이 버그가 아니라 기능이다."*
- facts V2를 근거로: bcrypt는 **work factor를 해시 문자열 안에 함께 저장한다.** 그래서 나중에 강도를 올려도 기존 비밀번호가 깨지지 않는다 — 느림을 운영 가능하게 만드는 설계다.

- [ ] **Step 5: 2장 데모 `#hashLab`을 만든다**

`.demo#hashLab`, `.demo-tag` = `느린 것이 기능이다`

- 비밀번호 입력칸 하나 + 계정 두 개(`alice`, `bob`)가 **같은 비밀번호**를 쓰는 상황
- 토글: `해시 없음` / `SHA-256` / `SHA-256 + salt` / `bcrypt`
- 각 모드에서 두 계정의 저장값을 보인다. **`SHA-256`에서는 두 값이 같고, salt를 넣으면 갈라진다** — 이것이 salt의 전부다.
- work factor 슬라이더(4~14)를 두고, **실제로 지연을 체감시킨다.** 실제 bcrypt를 구현하지 말고, `cost`에 비례한 반복 계산으로 체감 지연만 만든다. 화면에 *"실제 bcrypt가 아니라 비용 곡선만 흉내 낸 것"*이라고 명시한다.
- 저장값 표기에 work factor가 포함되어 보이게 한다 (강도가 해시 안에 저장된다는 사실의 시각화)

**금지**: 실제 암호 구현을 흉내 내면서 진짜인 척하지 않는다. 반드시 흉내임을 화면에 쓴다.

- [ ] **Step 6: 2장 `.spring` 블록과 퀴즈를 쓴다**

`.spring` 내용 (facts V2 근거):
- `PasswordEncoder` 인터페이스, `PasswordEncoderFactories.createDelegatingPasswordEncoder()`
- `BCryptPasswordEncoder` 기본 강도 **10**, 범위 **4~31**, salt **16바이트**를 자체 포함
- 강도가 해시에 저장되므로 나중에 올려도 기존 비번이 안 깨진다
- **`{bcrypt}` 접두어 문자열을 코드로 쓰기 전에 facts V2의 "미확인" 항목을 확인할 것**

퀴즈 `q-credentials`, 정답은 "bcrypt가 느린 것은 의도된 설계다" 취지. `.explain`에 work factor가 해시에 저장된다는 사실을 넣는다.

- [ ] **Step 7: 용어사전에 항목을 추가한다**

`GLOSSARY`에 `"무상태"`, `"salt"`, `"work factor"` 추가. 본문의 첫 등장 자리에 `<span class="term" data-t="salt">salt</span>` 형태로 표시한다.

- [ ] **Step 8: 표준 검증**

Expected: 양쪽 `OK`. **`[glossary] GLOSSARY에 없는 용어`가 뜨면 Step 7을 빠뜨린 것이다.**

- [ ] **Step 9: 브라우저 확인**

`#hashLab`에서 salt 없이는 두 계정 해시가 같고 salt를 켜면 갈라지는지, work factor를 올리면 체감 지연이 생기는지 확인한다.

- [ ] **Step 10: 커밋**

```bash
git add auth_basics.html
git commit -m "1~2장: 무상태 제약과 자격 증명 — 느린 것이 기능이다"
```

---

## Task 4: 3장 증표 · 4장 쿠키

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 1 공용 컴포넌트
- Produces: 섹션 `#token`, `#cookie`. 퀴즈 `q-token`, `q-cookie`. 데모 `#forkMap`, `#cookieLab`. 12장이 `#forkMap`의 갈림길을 회수한다.

- [ ] **Step 1: 3장 섹션을 쓴다**

`<section id="token" data-title="증표를 발급한다">`, kicker `03 · 갈림길`, 제목 `🎟️ 한 번만 확인하고, 그 다음엔 증표를 쓴다 <span class="lvl must">🟢 필수</span>`

- 확인은 1회, 사용은 N회. 비밀번호(자격 증명)와 증표(토큰)는 다른 물건이다 — 증표는 **훔쳐도 유효기간이 있고, 회수할 여지가 있고, 권한을 좁힐 수 있다.**
- **갈림길**: (a) 서버가 기억하고 열쇠만 준다 (b) 증표 자체에 내용을 담는다
- 이 갈림길이 문서 나머지 전부를 결정한다고 못 박고, 12장에서 답한다고 예고한다.
- 어느 쪽이든 남는 공통 요구: **브라우저가 매 요청에 그것을 붙여야 한다.** → 4장

- [ ] **Step 2: 3장 데모 `#forkMap`을 만든다**

`.demo#forkMap`, `.demo-tag` = `두 갈래`

두 갈래를 나란히 놓고, 같은 질문 다섯 개에 각각 어떻게 답하는지 보인다:
`증표에 무엇이 들었나` / `서버가 무엇을 기억하나` / `취소할 수 있나` / `서버가 여러 대면` / `요청마다 조회가 필요한가`

- 이 단계에서는 **답을 다 채우지 않는다.** "?"로 남겨 두고, 해당 장에서 채워진다고 표시한다(각 칸에 `→ 5장`, `→ 9장`, `→ 11장` 같은 앵커 링크).
- 12장에서 이 표가 다 채워진 형태로 다시 나온다.

- [ ] **Step 3: 3장 퀴즈 `q-token`을 쓴다**

정답 취지: **증표가 비밀번호보다 나은 이유는 "짧아서"가 아니라 "회수·만료·범위 제한이 가능해서"다.**

- [ ] **Step 4: 4장 섹션을 쓴다**

`<section id="cookie" data-title="쿠키">`, kicker `04 · 운반`, 제목 `🍪 쿠키 — 브라우저가 알아서 붙여 주는 것 <span class="lvl must">🟢 필수</span>`

- `Set-Cookie`(응답) / `Cookie`(요청)의 왕복. 서버가 한 번 주면 브라우저가 **이후 모든 해당 요청에 자동으로** 붙인다.
- 속성을 정의 순서가 아니라 **각각이 막는 공격 순서**로 배열한다:

| 속성 | 없으면 벌어지는 일 |
|---|---|
| `Secure` | 평문 HTTP 요청에도 쿠키가 실려 나간다 |
| `HttpOnly` | XSS가 나면 `document.cookie`로 통째로 털린다 |
| `SameSite` | 남의 사이트가 만든 요청에도 쿠키가 붙는다 → 6장 |
| `Domain`·`Path` | 의도보다 넓은 범위로 새어 나간다 |
| `Max-Age`·`Expires` | 없으면 세션 쿠키(브라우저 닫으면 소멸) |

- facts V6 근거로 **정확히** 쓸 것:
  - `Secure`는 `https:`에서만 전송되지만 **localhost는 예외다** — 로컬에서 되던 게 배포하면 안 되는 이유 중 하나
  - `SameSite=None`은 **`Secure`가 필수**다
  - **⚠️ "요즘 브라우저는 `SameSite` 기본이 `Lax`"라고 단정하지 않는다.** MDN은 "*some* browsers"라고 쓴다.

- [ ] **Step 5: 4장 데모 `#cookieLab`을 만든다**

`.demo#cookieLab`, `.demo-tag` = `이 요청에 쿠키가 붙나`

- 왼쪽: 쿠키 속성 토글 (`Secure`, `HttpOnly`, `SameSite: 없음/Lax/Strict/None`, `Domain`, `Path`)
- 오른쪽: 요청 시나리오 목록 — `같은 사이트에서 링크 클릭` / `같은 사이트에서 fetch` / `남의 사이트에서 이미지 태그` / `남의 사이트의 폼 POST` / `남의 사이트에서 링크 클릭(최상위 이동)` / `평문 HTTP 요청` / `JS의 document.cookie 접근`
- 각 시나리오에 **붙는다 / 안 붙는다 + 이유 한 줄**을 표시한다
- `SameSite=None`인데 `Secure`가 꺼져 있으면 **쿠키 자체가 거부됨**을 명시한다
- `SameSite` 미지정을 고르면 *"브라우저마다 다릅니다"*라고 표시하고, 기본 적용 `Lax`의 2분 예외를 각주로 붙인다 (6장에서 본격적으로 다룬다고 예고)

- [ ] **Step 6: 4장 `.spring` 블록과 퀴즈를 쓴다**

`.spring`: `server.servlet.session.cookie.http-only` / `.secure` / `.same-site` / `.name`. **Spring Session을 쓰면 이 설정이 아니라 `DefaultCookieSerializer` 쪽으로 옮겨간다는 것과, 기본 쿠키명이 달라진다는 것은 8장에서 다룬다**고만 예고한다(여기서 미리 풀지 않는다).

퀴즈 `q-cookie` 정답 취지: **`HttpOnly`는 XSS로 쿠키를 훔쳐 가는 것을 막지만, XSS 자체를 막지는 않는다.** 공격자는 여전히 그 페이지에서 요청을 보낼 수 있다. `.explain`에 이 구분을 분명히 쓴다 — 12장 `localStorage` 논쟁의 복선이다.

- [ ] **Step 7: 표준 검증 → 브라우저 확인 → 커밋**

브라우저에서 `SameSite=None` + `Secure` 끄기 조합이 "거부됨"으로 나오는지 확인한다.

```bash
git add auth_basics.html
git commit -m "3~4장: 증표의 두 갈래와 쿠키 — 속성을 막는 공격 순서로 배열"
```

---

## Task 5: 5장 세션 · 6장 CSRF

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 4의 `#cookieLab` 개념
- Produces: 섹션 `#session`, `#csrf`. 퀴즈 `q-session`, `q-csrf`. 데모 `#sessionStore`, `#csrfLab`. 7장이 `#sessionStore`를 회수한다.

- [ ] **Step 1: 5장 섹션을 쓴다**

`<section id="session" data-title="세션">`, kicker `05 · 갈래 (a)`, 제목 `🗄️ 세션 — 서버가 기억하는 방식 <span class="lvl must">🟢 필수</span>`

- 쿠키에는 **열쇠만**, 내용은 서버에. 세션 ID는 **뜻이 없는 난수**여야 한다.
- 왜 난수여야 하나: 순번이면 옆 번호를 찍어 남의 세션에 들어간다. 추측 가능성이 곧 전체 붕괴다.
- 서버 안의 `Map<sessionId, 사용자정보>`. **이 Map이 어디에 있느냐가 7장의 전부다** — 복선을 명시적으로 심는다.
- **세션 고정 공격**: 공격자가 자기가 아는 세션 ID를 피해자에게 심어 두고, 피해자가 그 ID로 로그인하면 공격자도 로그인된 상태가 된다. 방어는 **로그인 성공 시 세션 ID를 새로 발급**하는 것.

- [ ] **Step 2: 5장 데모 `#sessionStore`를 만든다**

`.demo#sessionStore`, `.demo-tag` = `서버 안을 들여다보기`

- 화면을 셋으로: 브라우저의 쿠키 상자 / 네트워크에 흐르는 것 / 서버의 세션 Map
- 버튼: `로그인` `요청 보내기` `로그아웃` `서버 재시작`
- 확인시킬 것:
  1. 로그인하면 서버 Map에 항목이 생기고 브라우저에 **ID만** 간다
  2. 네트워크에 흐르는 것은 난수뿐 — **사용자 정보는 한 번도 네트워크에 흐르지 않는다**
  3. `서버 재시작`을 누르면 Map이 비고, 브라우저 쿠키는 그대로인데 로그인이 풀린다
- 3번이 7장으로 가는 다리다. **"메모리에 있다"의 첫 번째 증거.**

- [ ] **Step 3: 세션 고정 재현을 `#sessionStore`에 붙인다**

토글 `세션 고정 방어: 끔/켬`. 끈 상태에서 `공격자가 ID 심기` → `피해자 로그인` 순서를 밟으면 공격자 쪽도 로그인 상태가 되는 것을 보인다. 켜면 로그인 시점에 ID가 바뀌어 공격자 쪽이 무효가 된다.

- [ ] **Step 4: 5장 `.spring`과 퀴즈를 쓴다**

`.spring` (facts V4 근거): `HttpSession`. 세션 고정 방어 전략 셋 — `changeSessionId`(**Servlet 3.1+ 기본**, 컨테이너의 방어를 씀), `newSession`(새 세션, Spring Security 속성만 복사), `migrateSession`(새 세션, 모든 속성 복사). 끄는 것은 권장되지 않는다.

퀴즈 `q-session` 정답 취지: 세션 ID가 유출되면 **비밀번호를 몰라도 그 사람이 된다.** 그래서 ID의 난수성과 전송 보호가 비밀번호만큼 중요하다.

- [ ] **Step 5: 6장 섹션을 쓴다**

`<section id="csrf" data-title="CSRF">`, kicker `06 · 대가`, 제목 `🎣 자동으로 붙는다는 성질의 대가 — CSRF <span class="lvl must">🟢 필수</span>`

- 4장의 편의가 그대로 취약점이 된다. 쿠키는 **누가 그 요청을 만들었든** 붙는다.
- 공격 시나리오를 구체적으로: 피해자가 우리 사이트에 로그인한 채로 공격자 페이지를 연다. 그 페이지의 폼이 우리 사이트로 `POST`를 쏜다. **브라우저는 성실하게 세션 쿠키를 붙인다.** 서버는 정상 요청과 구별할 수 없다.
- 방어 셋:
  1. `SameSite` — 남의 사이트에서 온 요청엔 안 붙인다
  2. **CSRF 토큰(동기화 토큰)** — 쿠키가 아닌 곳(폼 필드·헤더)에 넣는다. 공격자는 그 값을 읽을 수 없다(동일 출처 정책).
  3. `Origin`·`Referer` 검사
- **"`SameSite` 기본값이 생겼으니 CSRF는 끝난 문제"가 왜 틀린가** (facts V6):
  - 미지정 시 기본값은 **"일부" 브라우저만** `Lax`다
  - 그리고 **기본으로 적용된 `Lax`는 명시한 `Lax`보다 느슨하다** — 쿠키가 설정된 지 **2분 이내면 교차 사이트 `POST`에도 붙는다**
  - 즉 기본값에 기대는 것과 명시하는 것은 같지 않다
- **복선**: `Authorization` 헤더 방식에는 왜 이 문제가 없나 — **자동으로 붙지 않기 때문이다.** 12장에서 회수한다.

- [ ] **Step 6: 6장 데모 `#csrfLab`을 만든다**

`.demo#csrfLab`, `.demo-tag` = `공격 페이지 재현`

- 화면 둘: 우리 사이트(로그인 상태) / `evil.example` 페이지
- `evil.example`의 공격 버튼 셋: `이미지 태그로 GET` / `자동 제출 폼으로 POST` / `fetch로 POST`
- 방어 토글 셋: `SameSite=Lax` / `CSRF 토큰` / `Origin 검사`
- 각 조합에서 **공격이 성공하는지, 막히면 무엇이 막았는지** 표시한다
- 반드시 드러나야 하는 것:
  - `fetch`는 CORS 때문에 애초에 응답을 못 읽지만 **요청은 이미 서버에 도달했다** — "읽지 못함"과 "일어나지 않음"은 다르다
  - `SameSite=Lax`만으로도 폼 `POST`는 막히지만, **미지정 기본값에 기댈 때는 2분 예외가 있다**

- [ ] **Step 7: 6장 `.spring`과 퀴즈를 쓴다**

`.spring` (facts V7 근거):
- `@EnableWebSecurity`를 쓰면 CSRF는 **기본 활성**이다. 별도 코드가 필요 없다.
- **보호 대상 메서드가 서블릿과 리액티브에서 다르다**: 서블릿은 `GET`·`TRACE`·`HEAD`·`OPTIONS`를 **제외한** 전부, 리액티브(WebFlux)는 `PUT`·`POST`·`DELETE`. **뭉뚱그리지 않는다.**
- 토큰 저장소 기본값: 서블릿 `HttpSessionCsrfTokenRepository`
- `csrf().disable()`의 정당한 조건은 공식 표현 그대로: *"애플리케이션이 브라우저에서 전혀 쓰이지 않을 때만 권장된다."* → 그래서 "REST API니까 끈다"는 **쿠키로 인증하는 한 틀렸다.**

퀴즈 `q-csrf` 정답 취지: 쿠키 세션을 쓰는 SPA에서 `csrf().disable()`은 위험하다. `.explain`에 "토큰을 `Authorization` 헤더로 보낸다면 사정이 다르다"를 넣어 12장으로 잇는다.

- [ ] **Step 8: 표준 검증 → 브라우저 확인 → 커밋**

```bash
git add auth_basics.html
git commit -m "5~6장: 세션의 정체와 CSRF — 자동으로 붙는다는 성질의 대가"
```

---

## Task 6: 7장 — 서버가 두 대가 되는 순간 (척추 회수)

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 5의 `#sessionStore`(서버 재시작으로 세션이 날아가는 것)
- Produces: 섹션 `#twoservers`, 퀴즈 `q-twoservers`, 데모 `#lbSim`. Task 7이 `#lbSim`을 확장한다.

- [ ] **Step 1: 7장 섹션을 쓴다**

`<section id="twoservers" data-title="서버가 두 대가 되면">`, kicker `07 · 회수`, 제목 `💥 서버를 두 대로 늘렸더니 자꾸 로그아웃된다 <span class="lvl must">🟢 필수</span>`

- **Hero를 명시적으로 되받는다.** "이제 첫 장면의 증상을 설명할 수 있습니다."
- 세션 Map은 **그 서버의 메모리 안에** 있다(5장 회수). LB가 B로 보내면 B는 그 ID를 모른다. 그래서 "가끔" 로그아웃되고, 재현이 안 되고, 로그에 안 남는다.
- 첫 답: **sticky session**(세션 어피니티). LB가 같은 사용자를 같은 서버로 보낸다.
- 그 대가 넷 — **표로 정리한다**:

| 대가 | 언제 드러나나 |
|---|---|
| 서버 하나가 죽으면 그 서버 몫 사용자 전원 로그아웃 | 장애 시 |
| 스케일 아웃해도 기존 사용자는 안 옮겨가 부하가 안 풀린다 | 트래픽 급증 시 |
| **배포할 때마다 전원 로그아웃** | 배포 때마다 — 가장 자주 겪는다 |
| 축소(scale in) 시 연결이 끊긴다 | 오토스케일 축소 시 |

- [ ] **Step 2: 데모 `#lbSim`을 만든다**

`.demo#lbSim`, `.demo-tag` = `LB 뒤의 두 대`

- 위: 사용자, 가운데: LB, 아래: 서버 A·B (각자의 세션 Map을 보인다)
- 모드 토글: `라운드로빈` / `sticky`
- 버튼: `로그인` `요청 ×5` `서버 A 죽이기` `서버 추가` `배포(전체 재시작)`
- 확인시킬 것:
  - 라운드로빈에서는 로그인 직후 요청부터 **절반이 401**
  - sticky에서는 정상. 그러나 `서버 A 죽이기`를 누르면 A에 붙어 있던 사용자가 전부 로그아웃
  - `배포`를 누르면 sticky여도 **전원 로그아웃**
  - `서버 추가`를 눌러도 기존 사용자는 옮겨가지 않는다
- **Task 7이 이 데모에 모드 두 개(`복제`, `중앙 저장소`)를 더 붙인다.** 모드 목록을 배열로 두고 확장 가능하게 쓴다.

- [ ] **Step 3: 퀴즈 `q-twoservers`를 쓴다**

정답 취지: sticky session을 쓰는데도 **배포할 때마다** 로그아웃되는 이유는 세션이 여전히 프로세스 메모리에 있기 때문이다.

- [ ] **Step 4: 표준 검증 → 브라우저 확인 → 커밋**

브라우저에서 라운드로빈 로그인 후 요청 5회 중 절반이 실패하는지, sticky에서 배포 시 전원 로그아웃되는지 확인한다.

```bash
git add auth_basics.html
git commit -m "7장: 척추 회수 — sticky session과 그 네 가지 대가"
```

---

## Task 7: 8장 — 세션 클러스터링과 공유 저장소

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 6의 `#lbSim` (모드 배열을 확장한다)
- Produces: 섹션 `#sharing`, 퀴즈 `q-sharing`, 데모 `#replCost`

**이 태스크는 facts V5에 직접 의존한다. 시작 전에 facts 파일의 V5 절을 읽는다.**

- [ ] **Step 1: 8장 섹션을 쓴다**

`<section id="sharing" data-title="증표를 나눠 갖기">`, kicker `08 · 두 번째 답`, 제목 `🔗 증표를 나눠 갖기 — 세션 클러스터링과 공유 저장소 <span class="lvl must">🟢 필수</span>`

논점은 "무엇이 있나"가 아니라 **"무엇이 어디서 무너지나"**다.

**복제형 (세션 클러스터링)** — facts V5 근거로 정확히:
- all-to-all 방식은 **모든 세션을 다른 모든 노드에** 복제한다
- 노드가 늘면 복제 대상이 대수가 아니라 조합 수로 는다
- **Tomcat 문서 자신이 "4대 남짓을 넘으면 권장하지 않는다"고 쓴다** — 이건 남의 의견이 아니라 만든 쪽의 권고다
- 낭비의 성격을 한 줄로 보이는 사실: all-to-all은 **그 애플리케이션이 배포되지도 않은 노드에까지** 세션을 보낸다
- 백업본을 하나만 두는 방식으로 완화한다. 그쪽은 앱이 배포된 노드에만 보낸다. 그래도 메모리 중복과 GC 압박은 남는다

**중앙 저장소형**:
- 상태를 서버 밖으로 뺀다. 서버가 진짜 무상태가 되고 **7장의 대가 넷이 전부 사라진다** — 배포해도 로그아웃되지 않는다
- 대가: **매 요청마다 원격 조회 한 번**, 직렬화 비용, 그리고 그 저장소가 **새로운 단일 장애점**이 되어 그것도 이중화해야 한다

- [ ] **Step 2: `#lbSim`에 모드 두 개를 추가한다**

Task 6의 모드 배열에 `복제`, `중앙 저장소`를 더한다. 각 모드에서 `배포` 버튼의 결과가 달라야 한다:
- `복제`: 전체 재시작이면 여전히 전원 로그아웃(메모리는 메모리다). 한 대만 재시작하면 살아남는다.
- `중앙 저장소`: 전체 재시작해도 **로그인이 유지된다.** 대신 저장소를 죽이면 전원 로그아웃.
- `저장소 죽이기` 버튼을 중앙 모드에서만 노출한다.

- [ ] **Step 3: 데모 `#replCost`를 만든다**

`.demo#replCost`, `.demo-tag` = `노드가 늘면 무엇이 늘어나나`

- 노드 수 슬라이더 (2~12)
- 세 방식을 나란히: `sticky` / `복제(all-to-all)` / `복제(백업 1개)` / `중앙 저장소`
- 각각에 대해 **두 수치만** 보인다:
  1. **세션 하나가 저장되는 곳의 수**
  2. **요청 하나당 원격 조회 횟수**
- 노드가 5 이상이 되면 all-to-all 열에 경고 표시 + *"Tomcat 문서는 4대 남짓을 넘으면 권장하지 않는다"* 각주

**⚠️ 금지 (facts V5):** 대역폭(MB/s), 지연(ms), CPU 사용률 같은 **절대 수치를 그리지 않는다.** 근거가 없다. "몇 곳에 복사되는가"와 "요청당 조회가 몇 번인가"는 구조에서 나오는 수라 안전하지만, 그 외는 지어낸 것이 된다.

- [ ] **Step 4: 8장 `.spring`을 쓴다 — 이 장의 마무리 함정**

facts V3 근거로:
- Spring Session은 애플리케이션 코드를 거의 바꾸지 않고 저장소만 갈아 끼운다
- **그런데 기본 쿠키 이름이 바뀐다. `JSESSIONID`가 아니라 `SESSION`이다.**
- 그래서 배포 직후 **기존 사용자 전원이 로그아웃된 것처럼 보인다** — 브라우저에는 옛 `JSESSIONID`가 있는데 서버는 `SESSION`을 찾는다
- 부수 기본값: `sameSite`는 `Lax`, `maxAge`는 `-1`(브라우저 닫으면 소멸)
- 레퍼런스에 `setCookieName("JSESSIONID")` 예제가 있는데 **그것은 커스터마이즈 예제이지 기본값이 아니다** — 이 착각이 흔하다

- [ ] **Step 5: 퀴즈 `q-sharing`을 쓴다**

정답 취지: 세션을 Redis로 옮긴 직후 전원이 로그아웃된 것처럼 보이는 가장 흔한 원인은 **쿠키 이름이 바뀐 것**이다. 오답 보기로 "Redis 연결 실패", "직렬화 오류", "세션 만료 시간 변경"을 둔다.

- [ ] **Step 6: 표준 검증 → 브라우저 확인 → 커밋**

`#replCost`에서 노드 12일 때 all-to-all의 저장 위치 수가 12, 백업형이 2, 중앙형이 1로 나오는지 확인한다.

```bash
git add auth_basics.html
git commit -m "8장: 세션 클러스터링과 공유 저장소 — 무엇이 어디서 무너지나"
```

---

## Task 8: 9장 — 전환점

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Produces: 섹션 `#stateless-token`, 퀴즈 `q-trade`, 데모 `#tradeoff`. 11장이 이 장의 "거래"를 회수한다.

**이 장이 문서에서 가장 중요하다.** 대부분의 글이 "MSA니까 JWT"로 뭉개는 자리다. 서두르지 않는다.

- [ ] **Step 1: 9장 섹션을 쓴다**

`<section id="stateless-token" data-title="아무도 기억하지 않게">`, kicker `09 · 전환점`, 제목 `🕊️ 아무도 기억하지 않게 할 수는 없나 <span class="lvl must">🟢 필수</span>`

- 8장의 중앙 저장소는 문제를 **옮겼을 뿐이다.** "누가 기억하나"에 "제3자"라고 답한 것이지, 아무도 안 기억하는 건 아니다.
- 그것으로도 안 되는 지점 넷 — **각각을 구체적 상황으로** 쓴다:
  1. **서버가 수십·수백 대이고 오토스케일한다** — 요청 부하가 곧 저장소 부하가 된다. 앱은 무한히 늘려도 저장소는 그렇지 않다.
  2. **서비스가 여러 개다** — 서비스마다 같은 저장소를 때리면, 그 저장소가 전 조직의 병목이자 **공통 장애점**이 된다. 주문 서비스의 부하가 로그인을 죽인다.
  3. **도메인이 여러 개다** — 쿠키는 도메인에 갇힌다. `a.com`의 쿠키는 `b.com`에 안 간다.
  4. **클라이언트가 브라우저가 아니다** — 모바일 앱·CLI·서버 간 호출에는 쿠키 상자가 없다. 4장의 "브라우저가 알아서 붙여 준다"는 전제 자체가 사라진다.
- **질문을 뒤집는다**: 조회가 필요한 이유는 증표가 **비어 있기** 때문이다. 열쇠만 들고 있으니 자물쇠에 물어봐야 한다. 증표 안에 내용을 담으면 물어볼 일이 없다.
- 그러면 위조가 문제다. **위조를 막는 도구는 이미 배웠다 — 서명.** (HTTPS 문서 회수: 다시 설명하지 않고 이름만 부른다)
- **거래의 값을 미리 명시한다** — 이 문장을 `.callout.why`로 크게 박는다:
  > **조회 없음을 사고, 취소 가능성을 판다.**
- 11장이 이 청구서를 받는다고 예고한다.

- [ ] **Step 2: 데모 `#tradeoff`를 만든다**

`.demo#tradeoff`, `.demo-tag` = `같은 요청, 서버가 하는 일`

- 요청 하나를 세션 방식과 무상태 방식으로 나란히 처리한다
- 세션: 쿠키에서 ID 꺼냄 → **저장소 조회(원격)** → 사용자 정보 획득 → 처리
- 무상태: 헤더에서 토큰 꺼냄 → **서명 검증(로컬 계산)** → payload에서 사용자 정보 획득 → 처리
- 그 다음 **같은 화면에서** 조작 두 개를 준다:
  - `권한 박탈` 버튼 → 세션은 **다음 요청부터 즉시** 막힌다. 무상태는 **만료까지 계속 통과한다.**
  - `서비스 개수` 슬라이더 → 세션은 조회가 서비스 수만큼 늘고, 무상태는 그대로다
- 이 데모 하나로 거래의 양쪽이 다 보여야 한다.

- [ ] **Step 3: 퀴즈 `q-trade`를 쓴다**

정답 취지: JWT가 세션보다 **본질적으로 우월한 것이 아니라**, 조회를 없애는 대신 즉시 취소를 포기하는 거래다. 오답 보기로 "더 안전하다", "더 빠르다", "표준이라서" 같은 흔한 오해를 둔다.

- [ ] **Step 4: 표준 검증 → 브라우저 확인 → 커밋**

```bash
git add auth_basics.html
git commit -m "9장: 전환점 — 조회 없음을 사고 취소 가능성을 판다"
```

---

## Task 9: 10장 JWT · 11장 청구서

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 8의 "거래" 프레이밍
- Produces: 섹션 `#jwt`, `#revocation`. 퀴즈 `q-jwt`, `q-revocation`. 데모 `#jwtLab`, `#expiryLine`.

**시작 전에 facts V8의 서술 제한을 읽는다.**

- [ ] **Step 1: 10장 섹션을 쓴다**

`<section id="jwt" data-title="JWT">`, kicker `10 · 갈래 (b)`, 제목 `🎫 JWT — 증표 안에 내용을 담는다 <span class="lvl must">🟢 필수</span>`

- 구조: `header.payload.signature`, 각각 base64url
- **암호화가 아니다 — 누구나 읽는다.** 2장의 "base64는 암호가 아니다"가 그대로 돌아온다. **JWT에 비밀을 담지 않는다.**
- 서명이 보증하는 것: **위조 불가**(내용을 바꾸면 서명이 안 맞는다)
- 서명이 보증하지 **않는** 것: **비밀 유지**(누구나 읽는다), **최신성**(발급 시점의 사실일 뿐)
- HMAC(대칭) vs RSA·ECDSA(비대칭) — HTTPS 문서 회수. 후자라야 **검증 권한만 나눠 주고 발급 권한은 쥐고 있을 수 있다.** 마이크로서비스 여럿에 검증을 맡길 때 이것이 결정적이다.
- `alg: none` — **검증할 알고리즘을 토큰이 스스로 고르게 두면 검증이 사라진다.** 방어는 서버가 기대 알고리즘을 고정하는 것.
  - **⚠️ facts V8 서술 제한: CVE 번호도, 특정 라이브러리 이름도, 버전도 쓰지 않는다.** 확인에 실패했다. 원리와 방어 원칙만 쓴다.

- [ ] **Step 2: 데모 `#jwtLab`을 만든다**

`.demo#jwtLab`, `.demo-tag` = `해부하고 고쳐 보기`

- 위: 토큰 문자열 (세 부분을 색으로 구분)
- 아래: header / payload 편집기 (JSON), 서명 상태 표시
- 조작:
  - payload의 `sub`나 `role`을 고치면 → **서명 불일치**가 즉시 표시된다
  - `header.alg`를 `none`으로 바꾸고 서명을 지우면 → 두 가지 결과를 토글로 보인다: **검증자가 헤더를 믿을 때(통과)** vs **서버가 알고리즘을 고정했을 때(거부)**
  - `payload`에 비밀을 적으면 → *"이건 누구나 읽습니다"* 경고
- **명시할 것**: 이 데모는 실제 서명 알고리즘이 아니라 **검증의 논리만** 흉내 낸 것이다. 화면에 쓴다.
- **금지**: 특정 라이브러리가 이렇게 동작한다고 쓰지 않는다.

- [ ] **Step 3: 11장 섹션을 쓴다**

`<section id="revocation" data-title="취소할 수 없다">`, kicker `11 · 청구서`, 제목 `⏳ 청구서 — 취소할 수 없다는 것 <span class="lvl must">🟢 필수</span>`

- 발급한 순간 서버의 손을 떠난다. **로그아웃·권한 박탈·비밀번호 변경이 즉시 반영되지 않는다.**
- 대응과 그 값을 하나씩:
  - **짧은 만료 + refresh 토큰** — 노출 창을 줄인다. 대신 갱신 요청이 늘고, refresh 토큰 자체가 새 문제가 된다.
  - **블랙리스트** — 무효화된 토큰 목록을 서버가 들고 매 요청 확인한다. **그 순간 조회가 돌아온다. 9장의 거래가 무효화된다.** 이걸 할 거면 애초에 세션이 낫지 않은지 물어야 한다.
  - **토큰 버전 / `iat` 기준 무효화** — 사용자 레코드에 버전을 두고 토큰의 버전과 비교한다. 조회가 생기지만 블랙리스트보다 작다.
- **refresh 토큰 회전(rotation)과 재사용 탐지**: 갱신할 때마다 새 refresh를 주고 옛것을 버린다. 옛것이 다시 쓰이면 **탈취를 의심하고 그 계정의 토큰 전체를 무효화한다.**
- **refresh 토큰은 어디 두나 → `HttpOnly` 쿠키.** 4장이 돌아온다. 그리고 여기서 재미있는 것 — 무상태를 하겠다고 시작했는데 **결국 쿠키와 서버 측 상태로 돌아온다.**

- [ ] **Step 4: 데모 `#expiryLine`을 만든다**

`.demo#expiryLine`, `.demo-tag` = `언제부터 실제로 막히나`

- 가로 타임라인. 이벤트: `로그인` → (요청들) → **`권한 박탈`** → (요청들) → `만료` → `갱신 시도`
- 설정: 만료 시간 슬라이더(1분~24시간), 대응 방식 토글(`대응 없음` / `짧은 만료+refresh` / `블랙리스트` / `토큰 버전`)
- 표시할 것:
  - **권한 박탈부터 실제 차단까지의 공백 구간**을 붉게 칠한다
  - `블랙리스트`를 켜면 공백이 사라지는 대신 **"요청당 조회 1회"가 표시된다** — 거래가 되돌아온 것을 눈으로 본다
  - 세션 방식과 비교 막대를 나란히 둔다(세션은 공백 0, 조회 1)

- [ ] **Step 5: 퀴즈 두 개를 쓴다**

- `q-jwt` 정답 취지: JWT payload에 개인정보를 담으면 안 되는 이유는 **서명은 위조를 막을 뿐 내용을 가리지 않기** 때문이다.
- `q-revocation` 정답 취지: 블랙리스트를 도입하면 JWT를 쓴 이유(조회 없음)가 사라진다.

- [ ] **Step 6: 표준 검증 → 브라우저 확인 → 커밋**

`#jwtLab`에서 payload를 고치면 서명 불일치가 뜨는지, `alg:none` 토글 두 결과가 다른지 확인한다.

```bash
git add auth_basics.html
git commit -m "10~11장: JWT의 구조와 취소할 수 없다는 청구서"
```

---

## Task 10: 12장 — 그래서 세션이냐 토큰이냐

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 4의 `#forkMap`(빈 표), Task 5의 CSRF 복선, Task 9의 거래
- Produces: 섹션 `#choose`, 퀴즈 `q-choose`, 데모 `#chooser`

- [ ] **Step 1: 12장 섹션을 쓴다**

`<section id="choose" data-title="세션이냐 토큰이냐">`, kicker `12 · 결론`, 제목 `⚖️ 그래서 세션이냐 토큰이냐 <span class="lvl must">🟢 필수</span>`

- **3장의 갈림길을 회수한다.** `#forkMap`의 빈 표를 채워진 형태로 다시 낸다.
- **정직한 결론을 먼저**: 브라우저를 상대하는 단일 서비스라면 **세션이 기본값이다.** JWT는 9장의 넷 중 하나에 해당할 때 고르는 것이지, 기본값이 아니다.
- 흔한 오해 격파:
  - **"SPA니까 JWT"** — 무관하다. SPA도 쿠키 세션을 쓴다. 프런트가 분리된 것과 인증 방식은 다른 축이다.
  - **"MSA니까 JWT"** — 게이트웨이에서 브라우저 세션을 받아 내부용 토큰으로 바꾸는 구성이 흔하다. 바깥은 세션, 안쪽은 토큰.
  - **"JWT가 더 안전하다"** — 취소가 안 되는 쪽이 더 안전할 이유가 없다.
- **`localStorage` vs 쿠키 논쟁의 실체**: XSS가 나면 **둘 다 진다.** `localStorage`는 직접 읽히고, 쿠키는 `HttpOnly`면 못 읽지만 **공격자가 그 페이지에서 요청을 보내는 것은 막지 못한다**(4장 퀴즈 회수). `HttpOnly`가 낫지만 해결책은 아니다. 진짜 해결책은 XSS를 안 내는 것이다.
- **비교표** — CSRF 행에서 6장의 복선을 회수한다: 쿠키는 자동으로 붙어서 CSRF에 노출되고, `Authorization` 헤더는 자동으로 안 붙어서 노출되지 않는다. **대신 헤더 방식은 저장할 곳이 필요해서 XSS 노출이 커진다.** 둘 중 하나를 고르는 게 아니라 **어느 위험을 택할지**의 문제다.

- [ ] **Step 2: 데모 `#chooser`를 만든다**

`.demo#chooser`, `.demo-tag` = `내 상황에는 무엇이 맞나`

질문 5개를 토글로:
1. 클라이언트가 브라우저뿐인가?
2. 서비스가 하나인가?
3. 도메인이 하나인가?
4. 즉시 강제 로그아웃이 필요한가?
5. 서버가 수십 대 이상으로 늘어나나?

답 조합에 따라 권고를 낸다: `세션(단일 저장소)` / `세션(중앙 저장소)` / `게이트웨이에서 세션→토큰 변환` / `무상태 토큰`. **각 권고에 "무엇을 포기하는 것인지" 한 줄을 반드시 붙인다.** 공짜인 선택지를 보이지 않는다.

- [ ] **Step 3: 퀴즈 `q-choose`를 쓴다**

정답 취지: 브라우저용 단일 서비스에 JWT를 쓰면 **얻는 것 없이 취소 가능성만 잃는다.**

- [ ] **Step 4: 표준 검증 → 브라우저 확인 → 커밋**

```bash
git add auth_basics.html
git commit -m "12장: 갈림길 회수 — 세션이 기본값이고 JWT는 조건부다"
```

---

## Task 11: 13장 — 이 검사는 어디에 끼는가

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Produces: 섹션 `#filterchain`, 퀴즈 `q-filterchain`, 데모 `#chainPlay`

**시작 전에 facts V1의 서술 제한을 읽는다.**

- [ ] **Step 1: 13장 섹션을 쓴다**

`<section id="filterchain" data-title="코드 안의 자리">`, kicker `13 · 구조`, 제목 `🚧 이 검사는 요청 처리의 어디에 끼는가 <span class="lvl must">🟢 필수</span>`

- **컨트롤러가 아니다.** 요청이 컨트롤러에 닿기 전에 끝나야 한다. 컨트롤러마다 검사를 넣으면 빠뜨리는 곳이 반드시 생긴다.
- 체인의 순서: **인증(누구냐) → 컨텍스트에 담기 → 인가(해도 되냐) → 컨트롤러**
- 인증과 인가는 다른 질문이다 — 인증이 끝나야 인가를 물을 수 있다. (권한 관리 튜토리얼로 링크)
- **익명 사용자도 하나의 주체다.** "인증 안 됨"은 빈 값이 아니라 익명이라는 상태다. 그래야 "익명은 이것만 볼 수 있다"를 표현할 수 있다.
- **`@AuthenticationPrincipal`에 무엇이 어떻게 담기는가** — 이 문서를 찾아오는 독자의 실제 질문에 답한다: 앞선 필터가 인증을 마치고 컨텍스트에 주체를 넣어 뒀고, 컨트롤러 인자 해석기가 그것을 꺼내 넣어 주는 것이다. **마법이 아니라 앞에서 이미 끝난 일의 결과다.**

- [ ] **Step 2: 데모 `#chainPlay`를 만든다**

`.demo#chainPlay`, `.demo-tag` = `요청이 지나는 길`

- 요청 하나가 필터들을 지나는 것을 단계별로 재생한다
- 시나리오 토글: `쿠키 없음` / `유효한 세션 쿠키` / `만료된 토큰` / `권한 부족` / `CSRF 토큰 없는 POST`
- 각 단계에서 표시: 지금 무엇을 보는가 / 컨텍스트에 무엇이 담겼는가 / 통과인가 중단인가
- 드러나야 하는 것:
  - `쿠키 없음`도 **중단이 아니라 익명으로 통과**한다. 막히는 것은 나중의 인가 단계다.
  - `권한 부족`은 인증은 성공하고 **인가에서** 막힌다 — 401과 403의 차이가 여기서 나온다
  - `CSRF 토큰 없는 POST`는 인증보다 **앞에서** 막힐 수 있다

- [ ] **Step 3: 13장 `.spring`을 쓴다**

facts V1 근거로:
- `SecurityFilterChain` — 필터의 순서가 곧 설정이다
- `SecurityContextHolder` — 현재 요청의 주체를 담아 두는 곳
- **Spring Security 6의 변경**: `SecurityContextPersistenceFilter`(읽고 **쓰던** 것)가 `SecurityContextHolderFilter`(**읽기만** 하는 것)로 바뀌었다. `requireExplicitSave` 기본값이 **true**다.
- 그래서 **직접 `SecurityContextHolder`에 값을 넣는 커스텀 필터나 코드는 `SecurityContextRepository`로 명시적으로 저장해야 한다.** 안 하면 다음 요청에서 사라진다.
- **⚠️ facts V1 서술 제한: 내장 폼 로그인 필터가 어떤 경로로 저장하는지는 서술하지 않는다.** 확정하지 못했다.
- **⚠️ 이 항목은 낡은 블로그 글이 특히 자주 틀린다.** 기억이나 검색 요약으로 고쳐 쓰지 말고 facts 파일의 인용문을 근거로 삼는다.

- [ ] **Step 4: 퀴즈 `q-filterchain`을 쓴다**

정답 취지: 커스텀 필터에서 `SecurityContextHolder.setContext()`만 하고 저장하지 않으면 **그 요청 안에서는 동작하지만 다음 요청에서 사라진다.**

- [ ] **Step 5: 표준 검증 → 브라우저 확인 → 커밋**

```bash
git add auth_basics.html
git commit -m "13장: 필터 체인 — @AuthenticationPrincipal에 무엇이 어떻게 담기나"
```

---

## Task 12: 14장 인계 · 15장 마무리

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Consumes: Task 2의 `#diag` (자가진단 결과를 회수한다)
- Produces: 섹션 `#delegate`, `#wrap`. 퀴즈 `q-delegate`. 체크리스트 `#checklist`. **`oauth2_tutorial.html`로 나가는 링크.**

- [ ] **Step 1: 14장 섹션을 쓴다**

`<section id="delegate" data-title="남에게 맡긴다">`, kicker `14 · 인계`, 제목 `🚪 그런데, 남의 비밀번호를 우리가 받아도 되나 <span class="lvl must">🟢 필수</span>`

- **전제를 드러낸다**: 1~13장 전부가 *"우리 서버가 사용자의 비밀번호를 직접 받는다"* 위에 서 있었다. 한 번도 의심하지 않았다.
- 그 전제가 깨지는 상황 셋:
  1. **사용자가 우리를 믿지 않는다** — 처음 보는 서비스에 왜 비밀번호를 주나
  2. **우리 서비스가 남의 서비스에 있는 데이터에 접근해야 한다** — 사용자의 구글 캘린더를 읽으려면? 구글 비밀번호를 받는다는 건 말이 안 된다
  3. **회사 안에 서비스가 스무 개다** — 스무 번 로그인할 수는 없다
- 인증을 남에게 맡긴다 = **위임.** 그것이 다음 문서다.
- **못을 박고 끝낸다** — 이 문단이 두 문서를 잇는다:
  > 위임해도 4~13장은 그대로다. 남의 인증 서버가 "이 사람 맞다"고 알려 주면, **우리 서버는 그 결과를 받아서 결국 세션이나 토큰을 만든다.** 쿠키를 어떻게 설정할지, 서버가 두 대일 때 어떻게 할지, 강제 로그아웃을 어떻게 할지는 하나도 사라지지 않는다. OAuth는 **로그인 앞단을 남에게 맡기는 것**이지, 인증 설계를 대신해 주는 것이 아니다.
- `oauth2_tutorial.html`로 링크한다.

- [ ] **Step 2: 퀴즈 `q-delegate`를 쓴다**

정답 취지: "구글 로그인을 붙였으니 세션 관리는 신경 안 써도 된다"가 틀린 이유.

- [ ] **Step 3: 15장 섹션과 체크리스트를 쓴다**

`<section id="wrap" data-title="마무리">`, kicker `15 · 정리`, 제목 `🏁 마무리 — 내 서비스는 지금 어느 쪽인가`

`.ckl` 체크리스트 항목 (각각 `data-k` 부여, `LS`에 저장):
- 비밀번호를 일부러 느린 해시로 저장하고 있다
- 세션 쿠키에 `HttpOnly`·`Secure`·`SameSite`를 **명시**했다 (기본값에 기대지 않았다)
- 로그인 성공 시 세션 ID가 새로 발급된다
- CSRF 방어를 껐다면 그 이유를 한 문장으로 말할 수 있다
- 서버를 재시작해도 사용자가 로그아웃되지 않는다
- 강제 로그아웃이 **몇 초 안에** 실제로 반영되는지 안다
- 토큰을 쓴다면 payload에 비밀이 없다

**⚠️ known-issues §4 주의**: 체크리스트 점수가 "9 / 8"처럼 나오는 버그가 지난 문서에 있었다. 저장된 키 목록과 현재 항목 수가 어긋날 때 생긴다. **저장된 키를 읽을 때 현재 존재하는 `data-k`로 걸러낸 뒤 센다.**

- [ ] **Step 4: Hero 자가진단을 회수한다**

15장 끝에서 `#diag`의 선택 결과를 다시 보여 준다: *"시작할 때 이렇게 답하셨습니다"* + 각 항목이 **몇 장에서 다뤄졌는지** 앵커 링크를 단다.

- [ ] **Step 5: 표준 검증 → 브라우저 확인 → 커밋**

체크리스트를 전부 켰다 껐다 하며 점수가 항목 수를 넘지 않는지 확인한다.

```bash
git add auth_basics.html
git commit -m "14~15장: OAuth 문서로 인계, 그리고 마무리 체크리스트"
```

---

## Task 13: 부록 3종 · 용어사전 완성 · 앵커 검사 해제

**Files:**
- Modify: `auth_basics.html`

**Interfaces:**
- Produces: 섹션 `#appendix-spring`, `#appendix-others`, `#appendix-cli`. 완성된 `GLOSSARY`.
- **이 태스크 이후 `--allow-missing-anchors` 없이 검사가 통과해야 한다.**

- [ ] **Step 1: 부록 A — Spring Security 최소 설정 두 벌**

`<section id="appendix-spring" data-title="부록 A · Spring 설정">`, 제목에 `<span class="lvl adv">🔵 심화</span>`

본문의 흩어진 `.spring` 조각들을 한 벌로 합친다. 세션형과 JWT형 두 설정을 Prism `language-java`로.

**작성 전 확인 (facts V1·V2·V7)**:
- Spring Security 6의 람다 DSL 형태를 쓴다
- `{bcrypt}` 접두어 문자열은 **코드로 쓰기 전에 facts V2의 "미확인" 항목을 확인한다.** 확인이 안 되면 `PasswordEncoderFactories.createDelegatingPasswordEncoder()`만 쓰고 접두어 리터럴은 생략한다.
- **내장 필터의 저장 경로를 서술하지 않는다**(V1 제한)

각 설정 아래에 **"이 설정이 켜는 것 / 끄는 것"**을 표로 붙인다. 코드만 던지지 않는다.

- [ ] **Step 2: 부록 B — 다른 이름 같은 이야기**

`<section id="appendix-others" data-title="부록 B · 다른 프레임워크">`

Express `express-session`, Django, Rails에서 같은 개념이 어떤 이름인지 대응표. **이 부록의 목적은 개념이 프레임워크에 묶이지 않았음을 증명하는 것**이다. 각 프레임워크의 세부 동작을 정확히 서술할 자신이 없으면 **대응 이름만 적고 동작 설명은 하지 않는다** — 확인하지 않은 것을 쓰지 않는다는 원칙이 여기에도 적용된다.

- [ ] **Step 3: 부록 C — 진짜로 확인해 보기**

`<section id="appendix-cli" data-title="부록 C · 직접 확인">`

- `curl -v`로 `Set-Cookie` 응답 헤더 관찰하기
- 브라우저 개발자 도구 Application 탭에서 쿠키 속성 실측하기
- 토큰을 손으로 디코드해 보기 (base64url이 그냥 읽힌다는 것을 확인)
- **각 명령이 무엇을 보여 주는지**를 한 줄씩 붙인다

- [ ] **Step 4: 용어사전을 완성한다**

문서 전체에서 `class="term"`인 요소의 `data-t`를 모두 모아 `GLOSSARY`에 대응 항목이 있는지 확인한다.

```bash
python3 tools/check_tutorial.py --allow-missing-anchors auth_basics.html
```

`[glossary]` 문제가 0건이 될 때까지 반복한다. 정의는 한두 문장으로, **본문을 안 읽고도 이해되게** 쓴다.

- [ ] **Step 5: 앵커 검사를 해제하고 전체 검증한다**

```bash
python3 tools/check_tutorial.py auth_basics.html
python3 tools/check_dead_css.py auth_basics.html
```

Expected: 양쪽 `OK`. **`--allow-missing-anchors` 없이** 통과해야 한다. `[anchor] 가리키는 id가 없음`이 뜨면 그 링크의 대상 섹션 id를 확인해 고친다.

- [ ] **Step 6: 커밋**

```bash
git add auth_basics.html
git commit -m "부록 3종과 용어사전 완성 — 앵커 검사 전면 통과"
```

---

## Task 14: index.html 통합

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: 완성된 `auth_basics.html`

- [ ] **Step 1: 색 토큰을 추가한다**

`index.html:14`의 `:root` 토큰 줄에 `--webauth:#818cf8;`을 추가한다. 기존 토큰은 건드리지 않는다.

- [ ] **Step 2: 카드를 삽입한다**

`https_tutorial.html` 카드(현재 155~166행)와 `oauth2_tutorial.html` 카드(현재 168행부터) **사이**에 넣는다. 기존 카드와 같은 구조:

```html
<a class="card" href="auth_basics.html" style="--c:var(--webauth)">
  <div class="top">
    <span class="ic">🔑</span>
    <span class="no">Web Auth</span>
    <span class="new">NEW</span>
  </div>
  <h2>웹 애플리케이션 인증 기초 — 서버는 나를 어떻게 기억하는가</h2>
  <p>"<b>서버를 두 대로 늘렸더니 자꾸 로그아웃된다</b>"에서 출발합니다.
  HTTP가 아무것도 기억하지 못한다는 제약에서 시작해, 쿠키·세션·클러스터링·JWT가
  <b>왜 차례로 필요해졌는지</b>를 답 하나가 다음 문제를 만드는 순서로 따라갑니다.
  HTTPS가 통신을 지키는 이야기라면, 이쪽은 <b>그 위에서 사람을 알아보는</b> 이야기입니다.</p>
  <div class="tags"><i>무상태 HTTP</i><i>비밀번호 저장</i><i>쿠키 속성</i><i>세션</i><i>CSRF</i><i>세션 클러스터링</i><i>JWT</i><i>refresh·회전</i><i>필터 체인</i></div>
  <span class="go">열어 보기 <span class="ar">→</span></span>
</a>
```

- [ ] **Step 3: 문서 수를 갱신한다**

`index.html:133`의 `<span>🗂️ <b>6개 문서</b></span>`를 `7개 문서`로 바꾼다.

- [ ] **Step 4: 검증한다**

```bash
grep -c 'class="card"' index.html      # 7이어야 한다
grep -n '7개 문서' index.html           # 1건
grep -n 'webauth' index.html            # 토큰 정의 1건 + 카드 사용 1건 = 2건
```

브라우저로 `index.html`을 열어 카드 순서가 네트워크 → HTTPS → **웹 인증** → OAuth2 → 권한 → IAM → VPC이고, 왼쪽 색 띠가 인디고인지 확인한다. 카드를 눌러 `auth_basics.html`이 열리는지 확인한다.

- [ ] **Step 5: 커밋**

```bash
git add index.html
git commit -m "시리즈 인덱스: 웹 인증 기초 카드를 HTTPS와 OAuth 사이에 추가"
```

---

## Task 15: 최종 검수

**Files:**
- Modify: `auth_basics.html` (발견된 문제만)
- Modify: `docs/superpowers/notes/2026-08-14-known-issues.md`

- [ ] **Step 1: 자동 검사 전체**

```bash
python3 tools/check_tutorial.py auth_basics.html
python3 tools/check_dead_css.py auth_basics.html
python3 tools/check_tutorial.py --allow-missing-anchors *.html
```

셋째 명령은 **기존 파일의 알려진 결함이 늘지 않았는지** 확인하는 용도다. known-issues §3의 목록과 대조한다. **새 문제가 늘었으면 그것은 이번 작업이 만든 것이다.**

- [ ] **Step 2: 외부 의존성 0 확인**

브라우저 개발자 도구 네트워크 탭을 열고 `file://`로 `auth_basics.html`을 새로 연다. **요청 0건**이어야 한다.

- [ ] **Step 3: 모바일 드로어 확인**

창 너비를 900px 이하로 줄이고:
1. `☰ 목차`를 눌러 드로어를 연다
2. **드로어 안의 목차 항목이 실제로 눌린다** (스크림에 가려지지 않는다)
3. 항목을 누른 뒤 **화면을 덮는 오버레이가 남지 않는다** — known-issues §1이 지적한 두 번째 버그다. TOC 링크 핸들러가 `sidebar.open`과 `scrim.open`을 **둘 다** 지우는지 확인한다.

- [ ] **Step 4: 회수 구조 확인**

설계서 §5의 여덟 쌍이 본문에 실제로 있는지 하나씩 확인한다.

| 심는 곳 | 거두는 곳 | 확인 |
|---|---|---|
| 2장 base64는 암호가 아니다 | 10장 payload를 누구나 읽는다 | |
| 2장 해시·salt | 10장 서명 / 11장 토큰 버전 | |
| 3장 갈림길 | 12장 선택 가이드 | |
| 4장 `HttpOnly` 쿠키 | 11장 refresh 토큰을 어디 두나 | |
| 6장 헤더는 자동으로 안 붙는다 | 12장 비교표 CSRF 행 | |
| 7장 배포하면 전원 로그아웃 | 8장 중앙 저장소의 진짜 이득 | |
| 9장 조회 없음을 사고 취소를 판다 | 11장 블랙리스트가 거래를 무효화 | |
| 1~13장 우리가 비번을 받는다 | 14장 전제가 깨질 때 | |

**빠진 것이 있으면 해당 장에 문장을 넣는다.** 회수가 없으면 단일 파일일 이유가 없다.

- [ ] **Step 5: `.spring` 블록 분리 검증**

브라우저에서 모든 `<details class="spring">`가 **닫힌 상태**로 시작하는지 확인하고, 전부 닫힌 채로 1장부터 15장까지 읽으며 **논지가 끊기는 곳이 없는지** 확인한다. 끊기면 그 내용은 `.spring`이 아니라 본문에 있어야 한다.

- [ ] **Step 6: 사실 서술 대조**

facts 파일을 열고 V1~V8의 각 결론이 본문 서술과 일치하는지 대조한다. **특히 서술 제한 셋**:
- JWT 관련 CVE 번호·라이브러리 이름·버전이 **없는가**
- Spring 내장 폼 로그인 필터의 내부 저장 경로를 **서술하지 않았는가**
- 8장 복제 데모에 대역폭·지연의 **절대 수치가 없는가**

- [ ] **Step 7: known-issues에 이번 작업의 잔여 항목을 기록한다**

`docs/superpowers/notes/2026-08-14-known-issues.md`에 절을 추가한다. 담을 것:
- 이번에 알고도 안 고친 것
- `tools/check_dead_css.py`를 기존 6개 파일에 돌린 결과 (`--report` 모드) — **고치지는 않고 기록만 한다. 별건이다.**
- facts 파일의 미확인 항목 (V2 `{bcrypt}` 접두어, V1 내장 필터 경로, V8 JVM 라이브러리 현황)

- [ ] **Step 8: 최종 커밋**

```bash
git add auth_basics.html docs/superpowers/notes/2026-08-14-known-issues.md
git commit -m "최종 검수: 회수 구조·모바일 드로어·사실 대조 확인"
```

---

## Self-Review 결과

계획을 쓴 뒤 설계서와 대조한 기록이다.

**1. 스펙 커버리지** — 설계서 §4의 15장 + 부록 3이 전부 태스크에 배정되었다. Hero(T2), 1~2장(T3), 3~4장(T4), 5~6장(T5), 7장(T6), 8장(T7), 9장(T8), 10~11장(T9), 12장(T10), 13장(T11), 14~15장(T12), 부록(T13). §6 구현 규약은 T1과 T14, §7 사실 제약은 Global Constraints와 각 장 태스크, §8 완료 기준은 T15에 들어갔다.

**2. 스펙에 없던 추가** — `tools/check_dead_css.py`는 승인된 설계서에 없다. 골격 파일 실측에서 **CSS 클래스 226개 중 131개(58%)가 사장 코드**임이 드러났고(설계서가 인용한 known-issues의 "34%"보다 크다), 설계서의 규약 "사장 CSS를 가져오지 않는다"를 사람 눈으로 지키는 것은 실패할 게 뻔해서 넣었다. **범위 추가이므로 사용자 확인 대상이다.**

**3. 타입·이름 일관성** — 섹션 id는 `intro` `stateless` `credentials` `token` `cookie` `session` `csrf` `twoservers` `sharing` `stateless-token` `jwt` `revocation` `choose` `filterchain` `delegate` `wrap` + 부록 3으로 전부 유일하다. 퀴즈 id는 `q-` 접두어로 15개, 섹션과 1:1이다. 데모 id `#lbSim`은 T6이 만들고 T7이 확장하므로 **T6에서 모드를 배열로 두라고 명시**했다. `#forkMap`(T4)의 빈 표를 T10이 채우는 의존도 양쪽에 적었다. `#diag`(T2)를 T12가 회수하는 것도 양쪽에 적었다.

**4. 플레이스홀더 스캔** — "적절히", "필요하면", "TBD" 없음. 데모는 전부 조작·표시·드러나야 할 것을 명시했다. 다만 **본문 산문 자체는 태스크가 "말해야 하는 것"의 목록으로 지정하고 문장은 구현자가 쓴다** — 15장 분량의 완성 원고를 계획서에 넣는 것은 계획서가 아니라 문서 자체가 된다.
