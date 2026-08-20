# OAuth2 발표 덱 파일럿 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `oauth2_tutorial.html`의 자산을 재사용해 사내 주니어 세미나용 52분 발표 덱 `oauth2_slides.html`(본편 53장 + 부록 14장)을 만들고, 나머지 7편에 재사용할 공용부를 마커로 분리해 둔다.

**Architecture:** 자체완결 단일 HTML. 1280×720 고정 좌표계를 `transform: scale()`로 뷰포트에 맞춘다. 슬라이드 전환과 다이어그램 프레임 전진을 **"비트"라는 하나의 축**으로 합쳐 `→` 키 하나로 발표가 굴러가게 한다. 대본은 `<script type="application/json">` 블록 한 곳에 모아 덱과 검사기가 **같은 바이트를 읽는다.**

**Tech Stack:** 순수 HTML/CSS/JS (빌드 도구 없음, 외부 요청 없음, WebCrypto). 검사기는 Python 3 표준 라이브러리. 브라우저 동작 테스트는 pytest + Playwright(선택).

**Spec:** `docs/superpowers/specs/2026-08-20-tutorial-slides-design.md`

## Global Constraints

- **외부 요청 금지** — 이 저장소의 모든 문서가 지키는 규칙. `tools/check_tutorial.py`가 강제한다. CDN·폰트·이미지 원격 로드, `fetch`/`XMLHttpRequest`/`new Image` 전부 금지.
- **단일 파일** — `oauth2_slides.html` 하나에 CSS·JS·SVG가 전부 들어간다. 외부 파일 참조 없음.
- **`file://`에서 동작해야 한다** — 로컬에서 여는 일이 많다. `localStorage`·`BroadcastChannel`·`fetch`에 의존하지 않는다.
- **대본 속도 상수: 5.5자/초** (= 330자/분). 덱과 검사기가 같은 값을 쓴다.
- **대본 목표: 3120초 ±180초** (52:00 ±3:00).
- **슬라이드당 대본: 25초~110초.**
- **글자 크기 하한(1280 좌표계 기준): 본문 24px, 코드 20px.**
- **언어: 한국어.** 대본은 그대로 읽으면 발표가 되는 완성된 문장(불릿 아님).
- **슬라이드 수: 본편 53장(`s00`~`s52`) + 부록 14장(`a00`~`a13`) = 67장.**

---

## 설계 대비 변경 하나 — `data-sec`를 없앤다

설계 문서 7절은 "슬라이드마다 `data-sec`을 박는다"고 했다. 구현 단계에서 이를 **런타임 계산으로 바꾼다.**

이유는 하나다. `data-sec`을 마크업에 박으면 **대본을 고칠 때마다 두 곳을 고쳐야 하고, 안 고치면 어긋난 채로 조용히 남는다.** 시간 계측기의 존재 이유가 "숫자로 확인하는 것"인데 그 숫자가 대본과 어긋나면 계측기가 거짓말을 한다.

대신 대본을 `<script type="application/json" id="deck-script">` 한 블록에 두고:
- 덱은 `JSON.parse`로 읽어 글자 수 ÷ 5.5로 초를 계산한다
- 검사기는 같은 블록을 `json.loads`로 읽어 같은 계산을 한다

**JS 객체 리터럴이 아니라 JSON인 이유**는 검사기가 정규식으로 JS를 파싱하지 않아도 되기 때문이다. 두 소비자가 같은 바이트를 읽는다.

---

## 파일 구조

| 파일 | 책임 |
|---|---|
| `oauth2_slides.html` (신규) | 덱 전체. 아래 마커로 구획된다 |
| `tools/check_slides.py` (신규) | 덱 구조 불변식 검사기. 표준 라이브러리만 |
| `tools/testdata/deck_*.html` (신규) | 검사기 테스트용 최소 픽스처 |
| `tools/test_check_slides.py` (신규) | 검사기의 pytest 테스트 |
| `tools/test_deck_behavior.py` (신규) | Playwright 동작 테스트 (브라우저 없으면 skip) |

`oauth2_slides.html` 내부 마커 — **이 문자열 그대로** 넣는다. 검사기와 이후 빌더가 이 문자열로 블록을 찾는다:

```
/* ==== DECK:CORE:CSS ==== */ … /* ==== /DECK:CORE:CSS ==== */
/* ==== DECK:STAGE:CSS ==== */ … /* ==== /DECK:STAGE:CSS ==== */
/* ==== ASSET:CSS ← oauth2_tutorial.html ==== */ … /* ==== /ASSET:CSS ==== */
<!-- ==== SLIDES ==== -->  …  <!-- ==== /SLIDES ==== -->
/* ==== DECK:CORE:JS ==== */ … /* ==== /DECK:CORE:JS ==== */
/* ==== ASSET:JS ← oauth2_tutorial.html ==== */ … /* ==== /ASSET:JS ==== */
```

## 원본 자산 좌표 (확인 완료)

`oauth2_tutorial.html` — `<style>` 7~432줄, `<script>` 1925~2546줄.

| 블록 | 원본 줄 | 처리 |
|---|---|---|
| 루트 변수·리셋·기본 타이포 | 7–57 | 이식 (무대용 오버라이드를 덧씌움) |
| Sidebar | 58–87 | **버림** — 덱에 사이드바가 없다 |
| Content | 88–175 | 이식 후 `check_dead_css.py`로 미사용분 제거 |
| Sequence player | 176–268 | 이식 |
| `.dia` | 269–431 | 이식 |

다이어그램 — **`data-at` 최대 인덱스 + 1 == `wireDia` 단계 수**가 10개 전부 일치함을 확인했다. 검사기가 이 불변식을 지킨다.

| id | 원본 줄 | 프레임 | 배치 |
|---|---|---|---|
| `diaDelegate` | 480–562 | 7 | 본편 s03 |
| `diaGate` | 614–671 | 7 | 본편 s07 |
| `diaActors` | 700–774 | 7 | 본편 s10 |
| `diaShape` | 812–870 | 7 | 본편 s13 |
| `diaPassword` | 966–1052 | 6 | 본편 s23 |
| `diaCode` | 1100–1159 | 6 | 본편 s26 |
| `diaPkce` | 1193–1265 | 7 | 본편 s30 |
| `diaChannel` | 1322–1399 | 6 | 본편 s35 |
| `diaStorage` | 1819–1873 | 6 | 본편 s48 |
| `diaSecret` | 1626–1672 | 6 | **부록 a04** |

시퀀스 — `MAIN_STEPS` 16단계(본편 s17·s51), `CC_STEPS` 4(부록 a07), `OIDC_STEPS` 18(**미사용**), `NATIVE_STEPS` 9(부록 a02), `DEVICE_STEPS` 10(부록 a03).

라이브 데모 마운트 — 본편: `#authUrl`(s20), `#stateOut`(s28), `#pkceOut`(s31), `#apiOut`(s38), `#rotOut`(s40), `.jwt-raw`/`.jwt-decoded`/`.jwt-checks`(s44·s45 — Task 6 에서 중복 id 를 클래스로 바꿨다). 부록: `#platPicks`(a05), `#tokenChoiceOut`(a10), `#consoleOut`(a11).

---

## 슬라이드 대장 — 본편 53장

| id | 제목 | 자산 | 비트 |
|---|---|---|---|
| `s00` | 표지 — 로그인 버튼 하나에 일어나는 일 | — | 1 |
| `s01` | 오늘 갈 길 (이정표 5개) | 단계 공개 | 5 |
| `s02` | "내 비밀번호를 남의 앱에 알려줘도 될까?" | — | 1 |
| `s03` | 위임 — 비밀번호 대신 좁은 열쇠 | `diaDelegate` | 7 |
| `s04` | 앱이 받는 건 권한이 좁은 토큰 | — | 1 |
| `s05` | `gh auth login`·`claude` 로그인도 이겁니다 → 부록 | — | 1 |
| `s06` | 검사대가 둘 있다 | — | 1 |
| `s07` | 두 검사대가 묻는 질문 | `diaGate` | 7 |
| `s08` | AuthN / AuthZ 한 장 정리 | — | 2 |
| `s09` | 등장인물 다섯 | — | 5 |
| `s10` | 용어가 아니라 선을 본다 | `diaActors` | 7 |
| `s11` | 비밀번호가 지나는 선은 딱 하나 | — | 1 |
| `s12` | 토큰은 "이미 확인받았다"는 증표 | — | 1 |
| `s13` | 같은 요청, 다른 토큰 모양 | `diaShape` | 7 |
| `s14` | opaque vs JWT 대조 | — | 2 |
| `s15` | 왕복이 사라진 대신 물어볼 곳도 사라졌다 | — | 1 |
| `s16` | 이제 전체를 한 바퀴 | — | 1 |
| `s17` | **16단계 전체 흐름** | `mainSeq` 자동재생 | 1 |
| `s18` | 퀴즈 ① | 퀴즈 | 2 |
| `s19` | 로그인 버튼은 사실 URL을 만든다 | — | 1 |
| `s20` | 인가 요청 URL 라이브 조립 | `#authUrl` | 1 |
| `s21` | 파라미터 여섯이 하는 일 | — | 6 |
| `s22` | 이 화면은 누가 그렸나 | — | 1 |
| `s23` | 비밀번호는 인증 서버에만 | `diaPassword` | 6 |
| `s24` | 동의 화면 항목이 곧 scope | — | 1 |
| `s25` | 돌아오는 건 토큰이 아니다 | — | 1 |
| `s26` | 주소창에 실리면 네 군데에 남는다 | `diaCode` | 6 |
| `s27` | `state` — 위조 방지 도장 | — | 1 |
| `s28` | 정상 응답 / 위조 응답 | `#stateOut` | 1 |
| `s29` | 그럼 코드를 훔치면? | — | 1 |
| `s30` | **PKCE — 자물쇠와 열쇠** | `diaPkce` | 7 |
| `s31` | SHA-256 계산 → 탈취 시도 → 400 | `#pkceOut` | 1 |
| `s32` | 판단 규칙: secret을 숨길 수 있나 → 부록 | — | 1 |
| `s33` | 퀴즈 ② | 퀴즈 | 2 |
| `s34` | 프론트채널과 백채널 | — | 1 |
| `s35` | 브라우저가 그 줄에 있느냐 | `diaChannel` | 6 |
| `s36` | 토큰 응답 본문 | — | 1 |
| `s37` | `Authorization: Bearer` | — | 1 |
| `s38` | scope가 모자라면 403 | `#apiOut` | 1 |
| `s39` | access · id · refresh | — | 3 |
| `s40` | refresh 회전 | `#rotOut` | 1 |
| `s41` | 사람이 없으면 흐름이 다르다 → 부록 | — | 1 |
| `s42` | 그래서 누가 로그인했나 | — | 1 |
| `s43` | OAuth2 / OIDC 두 질문 | — | 2 |
| `s44` | `id_token` 해부 — 정상 생성·검증 | `.jwt-checks` ① | 1 |
| `s45` | 위변조 · nonce 불일치 → 검증 실패 | `.jwt-checks` ②③ | 1 |
| `s46` | 퀴즈 ③ | 퀴즈 | 2 |
| `s47` | 자주 밟는 지뢰 다섯 | — | 5 |
| `s48` | 토큰을 어디에 두나 | `diaStorage` | 6 |
| `s49` | 배포 전 체크리스트 (1/2) | — | 4 |
| `s50` | 배포 전 체크리스트 (2/2) | — | 4 |
| `s51` | **16단계 다시 한 바퀴** | `mainSeq` 자동재생 | 1 |
| `s52` | 한 장 요약 · 부록 안내 · 퀴즈 ④ | 퀴즈 | 3 |

## 슬라이드 대장 — 부록 14장

| id | 제목 | 자산 |
|---|---|---|
| `a00` | 부록 · CLI와 기기는 어떻게 로그인하나 | — |
| `a01` | 루프백 리다이렉트 — 잠깐 로컬 서버를 띄운다 | — |
| `a02` | CLI 로그인 전체 흐름 | `nativeSeq` (9단계) |
| `a03` | 디바이스 코드 — 입력은 폰에서 | `deviceSeq` (10단계) |
| `a04` | 기준은 하나 — secret을 숨길 수 있나 | `diaSecret` (6프레임) |
| `a05` | 웹서버 · SPA · 모바일 · CLI | `#platPicks` |
| `a06` | public 클라이언트가 PKCE로 메우는 자리 | — |
| `a07` | Client Credentials — 서비스의 정식 로그인 | `ccSeq` (4단계) |
| `a08` | client credentials · service token · PAT | — |
| `a09` | PAT가 왜 위험한가 | — |
| `a10` | 어떤 토큰을 써야 하나 | `#tokenChoiceOut` |
| `a11` | 요청·실패 케이스 콘솔 | `#consoleOut` |
| `a12` | 남겨 둔 퀴즈 (1/2) | 퀴즈 |
| `a13` | 남겨 둔 퀴즈 (2/2) | 퀴즈 |

---

## Task 1: 검사기 골격 — 대본 존재와 시간 규칙

먼저 검사기를 만든다. **이후 모든 태스크의 테스트 하네스**이기 때문이다. 덱이 아직 없으므로 `tools/testdata/`의 최소 픽스처로 TDD한다 (`tools/testdata/bad.html`이 쓰는 것과 같은 방식).

**Files:**
- Create: `tools/check_slides.py`
- Create: `tools/test_check_slides.py`
- Create: `tools/testdata/deck_ok.html`, `tools/testdata/deck_no_script.html`, `tools/testdata/deck_too_long.html`

**Interfaces:**
- Consumes: 없음
- Produces:
  - `read_deck(path) -> Deck` — `Deck`은 `namedtuple('Deck', 'html slides script')`. `slides`는 `[str]` (문서 순서의 슬라이드 id), `script`는 `{id: [str]}`.
  - `SPEED = 5.5` (자/초), `TOTAL_TARGET = 3120`, `TOTAL_TOL = 180`, `SLIDE_MIN = 25`, `SLIDE_MAX = 110`
  - `seconds(paras: list[str]) -> float`
  - `check_script_present(deck) -> list[str]`, `check_slide_seconds(deck) -> list[str]`, `check_total(deck) -> list[str]` — 각각 위반 메시지 목록을 돌려준다(빈 목록 = 통과)
  - `main(argv) -> int` — 0 통과 / 1 위반

- [ ] **Step 1: 픽스처 세 개를 만든다**

`tools/testdata/deck_ok.html` — 슬라이드 둘, 대본 둘. 각 슬라이드 대본은 40초 언저리(=220자 남짓).

```html
<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><title>fixture ok</title></head>
<body>
<!-- ==== SLIDES ==== -->
<section class="slide" id="s00"><h2>표지</h2></section>
<section class="slide" id="s01"><h2>둘째 장</h2></section>
<!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">
{
  "s00": ["안녕하세요. 오늘은 OAuth2와 OIDC를 한 시간 안에 훑어보려고 합니다. 로그인 버튼 하나를 누르면 그 뒤에서 무슨 일이 벌어지는지, 열여섯 단계를 전부 따라가 보겠습니다. 오늘 다루는 내용은 전부 실제 서비스에서 매일 도는 것들입니다."],
  "s01": ["먼저 질문 하나로 시작하겠습니다. 내 비밀번호를 남의 앱에 알려줘도 될까요. 사진 인화 서비스가 구글 포토에 있는 사진을 가져오려면 어떻게 해야 할까요. 가장 단순한 답은 아이디와 비밀번호를 그대로 넘겨주는 것입니다. 그런데 그러면 무슨 일이 생길까요."]
}
</script>
</body></html>
```

`tools/testdata/deck_no_script.html` — `deck_ok.html`과 같되 `"s01"` 항목을 JSON에서 뺀다.

`tools/testdata/deck_too_long.html` — `deck_ok.html`과 같되 `"s01"`의 문자열을 같은 문장을 반복해 **700자 이상**으로 늘린다 (700/5.5 ≈ 127초 > 110초 상한).

- [ ] **Step 2: 실패하는 테스트를 쓴다**

`tools/test_check_slides.py`:

```python
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
```

- [ ] **Step 3: 테스트가 실패하는지 확인한다**

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'check_slides'`

- [ ] **Step 4: 검사기를 구현한다**

`tools/check_slides.py`:

```python
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
```

- [ ] **Step 5: 테스트가 통과하는지 확인한다**

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: PASS — 8개 전부

- [ ] **Step 6: 커밋**

```bash
git add tools/check_slides.py tools/test_check_slides.py tools/testdata/deck_ok.html tools/testdata/deck_no_script.html tools/testdata/deck_too_long.html
git commit -m "덱 검사기: 대본 존재·슬라이드별 시간·합계 규칙"
```

---

## Task 2: 덱 골격 — 무대 · 전환 · 타이머

자산 없이 엔진만 먼저 굴린다. **설계 문서 11절의 확인 지점 1.**

**Files:**
- Create: `oauth2_slides.html`

**Interfaces:**
- Consumes: Task 1의 마커 규약 (`<!-- ==== SLIDES ==== -->`, `<script type="application/json" id="deck-script">`)
- Produces:
  - 전역 `Deck` 객체: `Deck.go(i)` 슬라이드 이동, `Deck.index` 현재 슬라이드 번호, `Deck.slides` 슬라이드 `<section>` 배열, `Deck.script` 파싱된 대본, `Deck.secOf(id) -> number`, `Deck.plannedUpTo(i) -> number`(0..i-1 슬라이드 대본 초의 합)
  - CSS 변수 `--stage-w: 1280px`, `--stage-h: 720px`

- [ ] **Step 1: 파일을 만든다 — 무대 스케일링과 슬라이드 전환**

`oauth2_slides.html`. 아래는 전체 골격이다. `ASSET:*` 블록은 비워 두고 마커만 넣는다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OAuth2 / OIDC — 발표 덱</title>
<style>
/* ==== DECK:CORE:CSS ==== */
:root{
  --stage-w:1280px; --stage-h:720px;
  --bg:#070b12; --panel:#111a28; --panel-2:#172133;
  --border:#233046; --border-2:#32425e;
  --text:#e8eef7; --text-dim:#9fb0c6; --text-mut:#8698b3;
  --accent:#2dd4bf; --warn:#fbbf24; --ok:#34d399; --no:#fb7185;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:"Pretendard Variable","Pretendard",-apple-system,BlinkMacSystemFont,system-ui,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#000}
body{font-family:var(--sans);color:var(--text);-webkit-font-smoothing:antialiased}

/* 무대: 1280x720 고정 좌표계를 통째로 확대·축소한다.
   반응형으로 글자가 커졌다 작아지면 뒷자리 가독성이 화면마다 달라진다. */
#viewport{position:fixed;inset:0;display:grid;place-items:center;background:#000}
#stage{
  position:relative;width:var(--stage-w);height:var(--stage-h);
  transform-origin:center center;background:var(--bg);overflow:hidden;
}
.slide{
  position:absolute;inset:0;padding:72px 88px 88px;
  display:flex;flex-direction:column;justify-content:center;
  opacity:0;visibility:hidden;
}
.slide.on{opacity:1;visibility:visible}
.slide h2{font-size:44px;line-height:1.25;letter-spacing:-1px;margin:0 0 28px;font-weight:800}
.slide p{font-size:26px;line-height:1.7;color:var(--text-dim);margin:0 0 16px}
.slide code{font-family:var(--mono);font-size:22px;color:var(--accent)}

/* 상단 진행 바 두 줄 — 위는 위치, 아래는 예정 대비 실제 */
#bars{position:absolute;left:0;right:0;top:0;height:6px;z-index:5}
#barPos,#barTime{position:absolute;left:0;height:3px;transition:width .25s}
#barPos{top:0;background:var(--accent)}
#barTime{top:3px;background:var(--ok)}
#barTime.behind{background:var(--warn)}

#hud{
  position:absolute;right:20px;top:16px;z-index:5;display:flex;gap:14px;align-items:center;
  font-family:var(--mono);font-size:13px;color:var(--text-mut);
}
#hud .clock{color:var(--text-dim)}
#hud .clock.running{color:var(--ok)}
/* ==== /DECK:CORE:CSS ==== */

/* ==== DECK:STAGE:CSS ==== */
/* 무대용 명도 대비 상향. 회의실 조명이 밝아도 뒷자리에서 읽히도록. */
:root{ --bg:#04070d; --text-dim:#c3d1e2; --text-mut:#a3b4c9; }
/* ==== /DECK:STAGE:CSS ==== */

/* ==== ASSET:CSS ← oauth2_tutorial.html ==== */
/* ==== /ASSET:CSS ==== */
</style>
</head>
<body>
<div id="viewport"><div id="stage">
  <div id="bars"><i id="barPos"></i><i id="barTime"></i></div>
  <div id="hud"><span class="clock" id="clock">0:00</span><span id="counter">1 / 1</span></div>

<!-- ==== SLIDES ==== -->
  <section class="slide" id="s00">
    <h2>OAuth2 / OIDC</h2>
    <p>로그인 버튼 하나에 일어나는 열여섯 단계</p>
  </section>
  <section class="slide" id="s01">
    <h2>둘째 장</h2>
    <p>골격 확인용 더미입니다.</p>
  </section>
  <section class="slide" id="s02">
    <h2>셋째 장</h2>
    <p>골격 확인용 더미입니다.</p>
  </section>
<!-- ==== /SLIDES ==== -->
</div></div>

<script type="application/json" id="deck-script">
{
  "s00": ["안녕하세요. 오늘은 OAuth2와 OIDC를 한 시간 안에 훑어보려고 합니다. 로그인 버튼 하나를 누르면 그 뒤에서 무슨 일이 벌어지는지, 열여섯 단계를 전부 따라가 보겠습니다."],
  "s01": ["이 장은 골격을 확인하려고 놓아 둔 더미입니다. 자산을 붙이기 전에 넘김과 타이머가 먼저 도는지 확인하는 자리입니다. 여기까지 확인되면 다음 단계로 넘어갑니다."],
  "s02": ["마지막 더미 장입니다. 오른쪽 화살표로 여기까지 왔다면 슬라이드 전환은 동작하는 것입니다. 이제 자산을 이식할 차례입니다."]
}
</script>

<script>
/* ==== DECK:CORE:JS ==== */
const $=(s,r=document)=>r.querySelector(s);
const $$=(s,r=document)=>Array.from(r.querySelectorAll(s));

// 검사기 tools/check_slides.py 의 SPEED 와 같은 값이어야 한다.
const SPEED=5.5;

const Deck={
  slides:[], script:{}, index:0,
  secOf(id){
    const paras=this.script[id]||[];
    const chars=paras.reduce((n,p)=>n+p.replace(/\s/g,'').length,0);
    return chars/SPEED;
  },
  plannedUpTo(i){
    let s=0; for(let k=0;k<i;k++) s+=this.secOf(this.slides[k].id); return s;
  },
  go(i){
    if(i<0||i>=this.slides.length)return;
    this.slides[this.index].classList.remove('on');
    this.index=i;
    this.slides[i].classList.add('on');
    paint();
  }
};

function fmt(sec){ sec=Math.max(0,Math.round(sec)); return `${Math.floor(sec/60)}:${String(sec%60).padStart(2,'0')}`; }

let t0=null, elapsed=0, ticking=null;
function elapsedSec(){ return elapsed + (t0!==null ? (performance.now()-t0)/1000 : 0); }
function toggleTimer(){
  if(t0!==null){ elapsed=elapsedSec(); t0=null; clearInterval(ticking); ticking=null; }
  else { t0=performance.now(); ticking=setInterval(paint,500); }
  paint();
}

function paint(){
  const n=Deck.slides.length;
  $('#counter').textContent=`${Deck.index+1} / ${n}`;
  $('#barPos').style.width=((Deck.index+1)/n*100)+'%';

  const total=Deck.plannedUpTo(n);
  const planned=Deck.plannedUpTo(Deck.index)+Deck.secOf(Deck.slides[Deck.index].id);
  const el=elapsedSec();
  $('#barTime').style.width=(total?Math.min(100,el/total*100):0)+'%';
  $('#barTime').classList.toggle('behind', el>planned);

  const clock=$('#clock');
  clock.textContent=fmt(el);
  clock.classList.toggle('running', t0!==null);
}

function fitStage(){
  const st=$('#stage');
  const w=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--stage-w'));
  const h=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--stage-h'));
  const k=Math.min(innerWidth/w, innerHeight/h);
  st.style.transform=`scale(${k})`;
}

function onKey(e){
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  switch(e.key){
    case 'ArrowRight': case ' ': case 'PageDown': e.preventDefault(); Deck.go(Deck.index+1); break;
    case 'ArrowLeft': case 'PageUp': e.preventDefault(); Deck.go(Deck.index-1); break;
    case 'ArrowDown': e.preventDefault(); Deck.go(Deck.index+1); break;
    case 'ArrowUp': e.preventDefault(); Deck.go(Deck.index-1); break;
    case 't': case 'T': toggleTimer(); break;
    case 'f': case 'F': if(document.fullscreenElement)document.exitFullscreen(); else document.documentElement.requestFullscreen(); break;
  }
}

function init(){
  Deck.slides=$$('.slide');
  Deck.script=JSON.parse($('#deck-script').textContent);
  Deck.slides[0].classList.add('on');
  addEventListener('keydown',onKey);
  addEventListener('resize',fitStage);
  fitStage(); paint();
}
/* ==== /DECK:CORE:JS ==== */

/* ==== ASSET:JS ← oauth2_tutorial.html ==== */
/* ==== /ASSET:JS ==== */

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
</script>
</body>
</html>
```

- [ ] **Step 2: 검사기를 돌린다**

Run: `python3 tools/check_slides.py oauth2_slides.html`
Expected: 슬라이드 3장을 읽고, **대본 합계가 52:00에 한참 못 미친다는 위반 1건**을 보고하며 종료 코드 1. 이 시점에는 정상이다 — 검사기가 덱을 읽어낸다는 것이 확인된 것이다.

- [ ] **Step 3: 외부 요청 금지 규칙을 확인한다**

Run: `python3 tools/check_tutorial.py oauth2_slides.html`
Expected: 원격 리소스·네트워크 호출 관련 위반 없음. (섹션 `data-title` 등 튜토리얼 전용 규칙 위반은 이 파일에 해당하지 않으므로 무시한다 — 어떤 규칙이 걸리는지 출력을 읽고 판단한다.)

- [ ] **Step 4: 브라우저에서 눈으로 확인한다**

`oauth2_slides.html`을 브라우저로 연다. 확인할 것:
- 창 크기를 바꿔도 슬라이드 비율과 글자 크기 비율이 유지되는가
- `→`로 3장이 넘어가고 `←`로 돌아오는가
- `T`로 시계가 돌기 시작하고 다시 누르면 멈추는가
- 위 진행 바가 슬라이드를 따라 늘어나는가
- `F`로 전체화면이 되는가

- [ ] **Step 5: 커밋**

```bash
git add oauth2_slides.html
git commit -m "덱 골격: 1280x720 무대·슬라이드 전환·진행바·타이머"
```

- [ ] **Step 6: 확인 지점 — 사용자에게 보고하고 멈춘다**

설계 문서 11절의 확인 지점 1이다. 골격이 굴러가는 것을 보고하고, 다음 태스크로 넘어가도 되는지 확인받는다.

---

## Task 3: 비트 시스템 — `→` 하나로 프레임과 슬라이드를 함께

이 덱에서 가장 중요한 조작 로직이다. 원본 `wireDia`는 `setTimeout`으로 스스로 재생하는데, 덱에서는 **덱이 프레임을 몰아줘야** 한다. 그래서 이식하면서 컨트롤러를 반환하도록 고친다.

**Files:**
- Modify: `oauth2_slides.html` (`DECK:CORE:JS`, `DECK:CORE:CSS`, `SLIDES`)
- Create: `tools/test_deck_behavior.py`

**Interfaces:**
- Consumes: Task 2의 `Deck.go(i)`, `Deck.slides`, `paint()`
- Produces:
  - `registerBeats(slideId, controller)` — `controller`는 `{n:number, go(i:number):void}`. `n`은 비트 수, `go(i)`는 0-기반 비트로 이동.
  - `Deck.beat` — 현재 슬라이드 안의 비트 번호(0-기반)
  - `Deck.next()` / `Deck.prev()` — 비트를 소진하면 슬라이드를 넘긴다
  - `.build[data-beat]` — 단계 공개용 요소. `data-beat="2"`면 비트 2부터 보인다. `.build.vis`가 붙으면 보인다.

- [ ] **Step 1: 비트 CSS를 `DECK:CORE:CSS`에 추가한다**

```css
/* 단계 공개 — data-beat 이상이 되면 .vis 가 붙는다 */
.build{opacity:0;transform:translateY(6px);transition:opacity .22s,transform .22s}
.build.vis{opacity:1;transform:none}
```

- [ ] **Step 2: 비트 엔진을 `DECK:CORE:JS`의 `Deck` 객체 아래에 추가한다**

```js
/* ---------- 비트: 슬라이드 안의 단계 ----------
   오른쪽 화살표 하나로 발표가 굴러가야 한다. 프레임 전진과 슬라이드 넘김에
   다른 키를 배정하면 발표자가 발표 중에 어느 키인지를 생각해야 한다. */
const BEATS={};                     // slideId -> {n, go(i)}
const AUTOPLAY={};                  // slideId -> {auto()}  — Task 5 가 채운다
function registerBeats(id,ctrl){ BEATS[id]=ctrl; }

function beatCount(slide){
  const ctrl=BEATS[slide.id];
  const builds=$$('.build',slide).map(el=>+el.dataset.beat||0);
  const fromBuilds=builds.length?Math.max(...builds)+1:1;
  return Math.max(ctrl?ctrl.n:1, fromBuilds);
}

function applyBeat(slide,b){
  $$('.build',slide).forEach(el=>el.classList.toggle('vis',(+el.dataset.beat||0)<=b));
  const ctrl=BEATS[slide.id];
  if(ctrl) ctrl.go(Math.min(b,ctrl.n-1));
}

Deck.beat=0;
Deck.next=function(){
  const slide=this.slides[this.index];
  if(this.beat < beatCount(slide)-1){ this.beat++; applyBeat(slide,this.beat); paint(); return; }
  if(this.index < this.slides.length-1) this.go(this.index+1, 0);
};
Deck.prev=function(){
  const slide=this.slides[this.index];
  if(this.beat>0){ this.beat--; applyBeat(slide,this.beat); paint(); return; }
  if(this.index>0) this.go(this.index-1, 'last');
};
```

- [ ] **Step 3: `Deck.go`가 비트를 초기화하도록 고친다**

Task 2의 `go(i)`를 아래로 교체한다:

```js
  go(i, beat=0){
    if(i<0||i>=this.slides.length)return;
    this.slides[this.index].classList.remove('on');
    this.index=i;
    const slide=this.slides[i];
    slide.classList.add('on');
    this.beat = (beat==='last') ? beatCount(slide)-1 : 0;
    applyBeat(slide,this.beat);
    paint();
  }
```

Task 5 가 이 자리에 자동재생 훅 한 줄을 더한다 — `applyBeat` 다음이다. 지금은 넣지 않는다.

`init()`의 첫 슬라이드 표시도 `Deck.go(0)`을 쓰도록 고친다 — 첫 장의 빌드가 적용되지 않으면 첫 장만 규칙이 다르게 동작한다.

- [ ] **Step 4: 키 처리를 비트로 돌린다**

`onKey`의 네 갈래를 교체한다:

```js
    case 'ArrowRight': case ' ': case 'PageDown': e.preventDefault(); Deck.next(); break;
    case 'ArrowLeft': case 'PageUp': e.preventDefault(); Deck.prev(); break;
    case 'ArrowDown': e.preventDefault(); Deck.go(Deck.index+1); break;   // 슬라이드 통째로
    case 'ArrowUp': e.preventDefault(); Deck.go(Deck.index-1); break;
```

- [ ] **Step 5: 비트 카운터를 HUD에 넣는다**

`paint()`의 카운터 줄을 교체한다:

```js
  const slide=Deck.slides[Deck.index];
  const bn=beatCount(slide);
  $('#counter').textContent = bn>1
    ? `${Deck.index+1} / ${n}  ·  ${Deck.beat+1}/${bn}`
    : `${Deck.index+1} / ${n}`;
```

- [ ] **Step 6: 더미 슬라이드에 빌드를 넣어 손으로 확인할 거리를 만든다**

`s01`을 교체한다:

```html
  <section class="slide" id="s01">
    <h2>비트 확인용</h2>
    <p class="build" data-beat="0">첫째 — 비트 0에서 보입니다.</p>
    <p class="build" data-beat="1">둘째 — 오른쪽 화살표를 한 번 눌러야 나옵니다.</p>
    <p class="build" data-beat="2">셋째 — 여기까지 소진해야 다음 장으로 넘어갑니다.</p>
  </section>
```

- [ ] **Step 7: 동작 테스트를 쓴다**

`tools/test_deck_behavior.py`:

```python
"""덱의 키보드 동작 테스트. Playwright 브라우저가 없으면 통째로 skip 한다.

  python3 -m playwright install chromium   # 한 번만

이 테스트는 슬라이드 '내용'에 기대지 않는다. Task 6·8 을 거치며 덱이 3장에서
67장이 되어도 엔진의 불변식은 그대로여야 하기 때문이다. 특정 슬라이드를
가리키는 대신, 필요한 성질(비트가 둘 이상인 슬라이드 등)을 그때그때 찾아 쓴다.
"""
import os

import pytest

playwright_api = pytest.importorskip('playwright.sync_api')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = 'file://' + os.path.join(ROOT, 'oauth2_slides.html')


@pytest.fixture(scope='module')
def page():
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:                     # 브라우저 바이너리 없음
            pytest.skip('chromium 없음: %s' % exc)
        pg = browser.new_page(viewport={'width': 1440, 'height': 900})
        yield pg
        browser.close()


def state(pg):
    return pg.evaluate('({i: Deck.index, b: Deck.beat, n: Deck.slides.length})')


def at(pg):
    s = state(pg)
    return (s['i'], s['b'])


def goto(pg, i):
    pg.evaluate('i => Deck.go(i)', i)


def first_multi_beat_slide(pg):
    """비트가 둘 이상인 첫 슬라이드의 (번호, 비트 수). 없으면 skip."""
    got = pg.evaluate(
        'Deck.slides.map((s, i) => [i, beatCount(s)]).find(([, n]) => n > 1) || null')
    if not got:
        pytest.skip('비트가 둘 이상인 슬라이드가 아직 없다')
    return got[0], got[1]


def test_starts_on_first_slide_at_beat_zero(page):
    page.goto(DECK)
    assert at(page) == (0, 0)


def test_right_arrow_consumes_every_beat_before_leaving_the_slide(page):
    page.goto(DECK)
    i, n = first_multi_beat_slide(page)
    goto(page, i)
    for expected in range(1, n):
        page.keyboard.press('ArrowRight')
        assert at(page) == (i, expected), '비트를 다 쓰기 전에 슬라이드를 넘겼다'
    page.keyboard.press('ArrowRight')
    assert at(page) == (i + 1, 0), '비트를 다 썼는데 슬라이드를 안 넘겼다'


def test_down_arrow_skips_the_whole_slide_ignoring_beats(page):
    page.goto(DECK)
    i, _ = first_multi_beat_slide(page)
    goto(page, i)
    page.keyboard.press('ArrowDown')
    assert at(page) == (i + 1, 0)


def test_left_arrow_enters_previous_slide_at_its_last_beat(page):
    page.goto(DECK)
    i, n = first_multi_beat_slide(page)
    goto(page, i + 1)
    page.keyboard.press('ArrowLeft')
    assert at(page) == (i, n - 1)


def test_builds_are_visible_exactly_up_to_the_current_beat(page):
    page.goto(DECK)
    i = page.evaluate(
        'Deck.slides.findIndex(s => s.querySelectorAll(".build").length >= 2)')
    if i < 0:
        pytest.skip('.build 가 둘 이상인 슬라이드가 아직 없다')
    goto(page, i)
    for beat in range(3):
        pairs = page.evaluate(
            'i => Array.from(Deck.slides[i].querySelectorAll(".build"))'
            '.map(e => [(+e.dataset.beat || 0), e.classList.contains("vis")])', i)
        for want, shown in pairs:
            assert shown == (want <= beat), \
                '비트 %d 에서 data-beat=%d 의 표시가 틀렸다' % (beat, want)
        page.keyboard.press('ArrowRight')


def test_cannot_advance_past_the_last_slide(page):
    page.goto(DECK)
    n = state(page)['n']
    page.evaluate('n => Deck.go(n - 1)', n)
    for _ in range(6):
        page.keyboard.press('ArrowRight')
    assert state(page)['i'] == n - 1


def test_cannot_go_before_the_first_slide(page):
    page.goto(DECK)
    for _ in range(6):
        page.keyboard.press('ArrowLeft')
    assert at(page) == (0, 0)
```

- [ ] **Step 8: 테스트를 돌린다**

Run: `python3 -m pytest tools/test_deck_behavior.py -v`

Expected — 두 가지 중 하나:
- 브라우저가 설치돼 있으면 7개 PASS
- 없으면 전부 SKIP. 그 경우 **Step 6의 더미 슬라이드로 손으로 확인한다**: `→`를 눌러 s01에서 문단이 하나씩 나타나고, 셋 다 나온 뒤에야 s02로 넘어가는가. `↓`는 문단 상태와 무관하게 장을 통째로 넘기는가.

- [ ] **Step 9: 커밋**

```bash
git add oauth2_slides.html tools/test_deck_behavior.py
git commit -m "비트 시스템: → 하나로 프레임과 슬라이드를 함께 넘긴다"
```

---

## Task 4: 발표자 창 · 노트 서랍 · 개요 그리드

**Files:**
- Modify: `oauth2_slides.html` (`DECK:CORE:CSS`, `DECK:CORE:JS`)
- Modify: `tools/test_deck_behavior.py`

**Interfaces:**
- Consumes: Task 3의 `Deck.next/prev/go`, `Deck.script`, `Deck.secOf`, `paint()`
- Produces: `openPresenter()`, `toggleNotes()`, `toggleOverview()`, `pushPresenter()` — `paint()` 끝에서 호출된다

- [ ] **Step 1: 노트 서랍과 개요 그리드 CSS를 `DECK:CORE:CSS`에 추가한다**

```css
/* 노트 서랍 — 발표자 창을 못 띄울 때의 대체 수단 */
#notes{
  position:absolute;left:0;right:0;bottom:0;max-height:38%;z-index:6;
  background:rgba(7,11,18,.97);border-top:1px solid var(--border-2);
  padding:18px 28px;overflow:auto;font-size:19px;line-height:1.75;color:var(--text-dim);
  transform:translateY(101%);transition:transform .2s;
}
#notes.on{transform:none}
#notes p{margin:0 0 10px;font-size:19px}

/* 개요 그리드 — 글자만 빽빽한 슬라이드를 한눈에 찾아내는 자리 */
#overview{
  position:absolute;inset:0;z-index:7;background:rgba(4,7,13,.98);
  padding:28px;overflow:auto;display:none;
  grid-template-columns:repeat(6,1fr);gap:12px;align-content:start;
}
#overview.on{display:grid}
.ov-cell{
  border:1px solid var(--border);border-radius:8px;background:var(--panel);
  padding:10px;cursor:pointer;font-size:12px;line-height:1.4;color:var(--text-mut);
  min-height:74px;
}
.ov-cell:hover{border-color:var(--accent)}
.ov-cell.cur{border-color:var(--accent);background:var(--panel-2)}
.ov-cell .n{font-family:var(--mono);font-size:10px;color:var(--accent);display:block;margin-bottom:4px}
.ov-cell .t{color:var(--text-dim);display:block;font-weight:600}
.ov-cell .s{font-family:var(--mono);font-size:10px;display:block;margin-top:4px}

#toast{
  position:absolute;left:50%;bottom:36px;transform:translateX(-50%);z-index:8;
  background:var(--panel-2);border:1px solid var(--border-2);border-radius:8px;
  padding:10px 16px;font-size:15px;color:var(--text-dim);opacity:0;transition:opacity .2s;
}
#toast.on{opacity:1}
```

- [ ] **Step 2: 마크업을 `#stage` 안, `SLIDES` 블록 뒤에 추가한다**

```html
  <div id="notes"></div>
  <div id="overview"></div>
  <div id="toast"></div>
```

- [ ] **Step 3: 발표자 창을 `DECK:CORE:JS`에 추가한다**

`file://`에서도 동작해야 하므로 `localStorage`·`BroadcastChannel`을 쓰지 않는다. 자식 창의 DOM을 부모가 직접 갱신한다.

```js
/* ---------- 발표자 창 ----------
   file:// 에서도 돌아야 해서 localStorage·BroadcastChannel 을 쓰지 않는다.
   자식 창의 DOM 을 부모가 직접 갱신한다. */
let pres=null;
const PRES_HTML=`<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<title>발표자 화면</title><style>
body{margin:0;background:#04070d;color:#e8eef7;font-family:system-ui,-apple-system,"Apple SD Gothic Neo",sans-serif}
.wrap{padding:20px 24px}
.row{display:flex;gap:20px;align-items:baseline;font-family:ui-monospace,Menlo,monospace;font-size:15px;color:#a3b4c9}
#delta{font-weight:700}
h3{margin:18px 0 6px;font-size:13px;letter-spacing:.5px;color:#8698b3;text-transform:uppercase}
.now{font-size:26px;font-weight:700;color:#fff;margin:0}
.next{font-size:17px;color:#9fb0c6;margin:0}
#script p{font-size:20px;line-height:1.8;color:#c3d1e2;margin:0 0 12px}
</style></head><body><div class="wrap">
<div class="row"><span>경과 <b id="el">0:00</b></span><span>예정 <b id="pl">0:00</b></span><span id="delta"></span><span id="cnt"></span></div>
<h3>지금</h3><p class="now" id="now"></p>
<h3>다음</h3><p class="next" id="nxt"></p>
<h3>대본</h3><div id="script"></div>
</div></body></html>`;

function openPresenter(){
  pres=window.open('','deck-presenter','width=760,height=900');
  if(!pres){ toast('팝업이 차단됐습니다. S 키로 노트 서랍을 여세요.'); return; }
  pres.document.open(); pres.document.write(PRES_HTML); pres.document.close();
  pushPresenter();
}

function titleOf(slide){ const h=slide.querySelector('h2'); return h?h.textContent.trim():slide.id; }

function pushPresenter(){
  if(!pres||pres.closed){ pres=null; return; }
  const d=pres.document; if(!d.getElementById('now'))return;
  const n=Deck.slides.length, i=Deck.index, slide=Deck.slides[i];
  const planned=Deck.plannedUpTo(i)+Deck.secOf(slide.id);
  const el=elapsedSec(), diff=planned-el;
  d.getElementById('el').textContent=fmt(el);
  d.getElementById('pl').textContent=fmt(planned);
  const dl=d.getElementById('delta');
  dl.textContent = diff>=0 ? `▲ ${fmt(diff)} 빠름` : `▼ ${fmt(-diff)} 늦음`;
  dl.style.color = diff>=0 ? '#34d399' : '#fbbf24';
  d.getElementById('cnt').textContent=`${i+1} / ${n}`;
  d.getElementById('now').textContent=titleOf(slide);
  d.getElementById('nxt').textContent = i+1<n ? titleOf(Deck.slides[i+1]) : '— 끝 —';
  d.getElementById('script').innerHTML=(Deck.script[slide.id]||[])
    .map(p=>`<p>${p.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}</p>`).join('');
}

let toastTimer=null;
function toast(msg){
  const t=$('#toast'); t.textContent=msg; t.classList.add('on');
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>t.classList.remove('on'),2600);
}
```

- [ ] **Step 4: 노트 서랍과 개요 그리드를 추가한다**

```js
function toggleNotes(){
  const el=$('#notes');
  el.classList.toggle('on');
  if(el.classList.contains('on')) renderNotes();
}
function renderNotes(){
  const id=Deck.slides[Deck.index].id;
  $('#notes').innerHTML=(Deck.script[id]||[])
    .map(p=>`<p>${p.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}</p>`).join('');
}

function toggleOverview(){
  const ov=$('#overview');
  if(ov.classList.contains('on')){ ov.classList.remove('on'); return; }
  ov.innerHTML=Deck.slides.map((s,i)=>{
    const sec=Deck.secOf(s.id);
    const warn = sec>110 ? 'color:#fb7185' : sec<25 ? 'color:#fbbf24' : 'color:#8698b3';
    return `<div class="ov-cell${i===Deck.index?' cur':''}" data-i="${i}">
      <span class="n">${i+1}</span><span class="t">${titleOf(s)}</span>
      <span class="s" style="${warn}">${fmt(sec)}</span></div>`;
  }).join('');
  $$('.ov-cell',ov).forEach(c=>c.addEventListener('click',()=>{
    ov.classList.remove('on'); Deck.go(+c.dataset.i);
  }));
  ov.classList.add('on');
}
```

- [ ] **Step 5: 숫자 점프를 추가한다**

설계 7절 키 표의 `숫자` `Enter` 항목이다. 질의응답에서 "아까 그 장 다시" 요청이 나올 때
개요 그리드를 거치지 않고 바로 가는 길이다.

```js
/* ---------- 숫자 점프 ----------
   화면에 보이는 번호가 1-기반이므로 입력도 1-기반으로 받는다.
   버퍼를 세 자리로 자르는 것은 오타로 아주 큰 수가 쌓이는 것을 막기 위해서다. */
let jumpBuf='';
function jumpDigit(d){ jumpBuf=(jumpBuf+d).slice(-3); toast(`이동: ${jumpBuf}`); }
function jumpCancel(){ jumpBuf=''; }
function jumpCommit(){
  if(!jumpBuf)return;
  const n=parseInt(jumpBuf,10); jumpBuf='';
  if(n>=1 && n<=Deck.slides.length) Deck.go(n-1);
  else toast(`${n}번 슬라이드는 없습니다`);
}
```

- [ ] **Step 6: 키를 연결하고 `paint()`가 발표자 창을 밀도록 한다**

`onKey`에 추가한다. `default` 갈래가 숫자를 받는다:

```js
    case 'p': case 'P': openPresenter(); break;
    case 's': case 'S': toggleNotes(); break;
    case 'o': case 'O': toggleOverview(); break;
    case 'Enter': jumpCommit(); break;
    case 'Escape':
      jumpCancel();
      $('#overview').classList.remove('on'); $('#notes').classList.remove('on'); break;
    default:
      if(/^[0-9]$/.test(e.key)) jumpDigit(e.key);
```

`p`·`s`·`o`·`a`·`t`·`f`가 한 글자 키이므로 **숫자 갈래를 `default`에 두어야** 문자 키와
충돌하지 않는다. 숫자를 별도 `case`로 열거하면 열 줄이 늘고, 새 문자 키를 넣을 때마다
순서를 신경 써야 한다.

`paint()` 끝에 추가:

```js
  pushPresenter();
  if($('#notes').classList.contains('on')) renderNotes();
```

- [ ] **Step 7: 테스트를 추가한다**

`tools/test_deck_behavior.py` 끝에 붙인다:

```python
def on(pg, sel):
    return pg.eval_on_selector(sel, 'e => e.classList.contains("on")')


def test_s_toggles_the_notes_drawer(page):
    page.goto(DECK)
    assert on(page, '#notes') is False
    page.keyboard.press('s')
    assert on(page, '#notes') is True
    assert page.inner_text('#notes').strip() != '', '노트 서랍이 비어 있다'
    page.keyboard.press('s')
    assert on(page, '#notes') is False


def test_open_notes_drawer_follows_the_current_slide(page):
    page.goto(DECK)
    page.keyboard.press('s')
    first = page.inner_text('#notes')
    page.keyboard.press('ArrowDown')
    assert page.inner_text('#notes') != first, '슬라이드를 넘겼는데 노트가 그대로다'


def test_o_opens_one_overview_cell_per_slide(page):
    page.goto(DECK)
    page.keyboard.press('o')
    assert on(page, '#overview') is True
    assert page.eval_on_selector_all('.ov-cell', 'els => els.length') == state(page)['n']


def test_overview_cell_click_jumps_to_that_slide(page):
    page.goto(DECK)
    page.keyboard.press('o')
    page.click('.ov-cell[data-i="2"]')
    assert state(page)['i'] == 2
    assert on(page, '#overview') is False


def test_escape_closes_overview_and_notes(page):
    page.goto(DECK)
    page.keyboard.press('o')
    page.keyboard.press('s')
    page.keyboard.press('Escape')
    assert on(page, '#overview') is False
    assert on(page, '#notes') is False


def test_number_then_enter_jumps_to_that_slide(page):
    page.goto(DECK)
    page.keyboard.press('3')
    page.keyboard.press('Enter')
    assert state(page)['i'] == 2, '화면 번호는 1-기반, 인덱스는 0-기반이다'


def test_out_of_range_number_does_not_move(page):
    page.goto(DECK)
    page.keyboard.press('9')
    page.keyboard.press('9')
    page.keyboard.press('9')
    page.keyboard.press('Enter')
    assert state(page)['i'] == 0


def test_escape_discards_a_partially_typed_number(page):
    page.goto(DECK)
    page.keyboard.press('3')
    page.keyboard.press('Escape')
    page.keyboard.press('Enter')
    assert state(page)['i'] == 0
```

- [ ] **Step 8: 테스트를 돌린다**

Run: `python3 -m pytest tools/test_deck_behavior.py -v`
Expected: 15개 PASS (Task 3의 7개 + 이번 8개). 브라우저가 없으면 전부 SKIP →
손으로 `S`·`O`·`P`·`Esc`와 `3`+`Enter` 점프를 확인한다.

발표자 창(`P`)은 팝업이라 자동 테스트에서 빠졌다. **손으로 확인한다**: `P`를 눌러 창이 뜨고, 본 창에서 `→`를 누르면 자식 창의 "지금/다음/대본/경과"가 따라 바뀌는가. `file://`로 열어도 되는가.

- [ ] **Step 9: 커밋**

```bash
git add oauth2_slides.html tools/test_deck_behavior.py
git commit -m "발표자 창·노트 서랍·개요 그리드"
```

---

## Task 5: 자산 이식 — CSS · 다이어그램 · 시퀀스 · 데모

**Files:**
- Modify: `oauth2_slides.html` (`ASSET:CSS`, `ASSET:JS`, `SLIDES`)
- Modify: `tools/check_slides.py` (프레임 일치 검사 추가)
- Modify: `tools/test_check_slides.py`

**Interfaces:**
- Consumes: Task 3의 `registerBeats(id, {n, go})`
- Produces:
  - `wireDia(id, steps) -> {n, go(i), el}` — **원본과 달리 스스로 재생하지 않는다.** 덱이 비트를 몰아준다
  - `createSequence(mountId, cfg) -> {n, go(i), auto()}` — `auto()`는 자동재생 시작
  - `#s17`·`#s51`의 `mainSeq`는 `auto()`를 쓴다. 16단계를 키로 넘기면 3분 30초에 들어오지 않고, 이 두 자리의 목적은 세부가 아니라 흐름의 윤곽이다

- [ ] **Step 1: CSS를 옮긴다**

`oauth2_tutorial.html`의 아래 구간을 `ASSET:CSS` 마커 사이에 그대로 복사한다. **맨 위에 출처 주석을 단다.**

```
/* 출처: oauth2_tutorial.html
     88-175  Content (본문 타이포·card·quiz·badge·pre)
    176-268  Sequence player
    269-431  애니메이션 다이어그램 (.dia)
   58-87 Sidebar 는 옮기지 않는다 — 덱에 사이드바가 없다.
   7-57 루트 변수는 DECK:CORE:CSS 가 이미 갖고 있다. 중복 정의하지 않는다. */
```

옮긴 뒤 `.slide` 안에서 크기가 맞지 않는 것만 `DECK:STAGE:CSS`에서 덮어쓴다. **`ASSET:CSS` 블록 자체는 고치지 않는다** — 원본과 대조 가능해야 한다.

- [ ] **Step 2: 다이어그램 SVG 9개를 슬라이드로 옮긴다**

각 `<figure class="dia" id="...">`를 해당 슬라이드 안에 통째로 복사한다. 배치는 슬라이드 대장을 따른다 — `diaDelegate`→`s03`, `diaGate`→`s07`, `diaActors`→`s10`, `diaShape`→`s13`, `diaPassword`→`s23`, `diaCode`→`s26`, `diaPkce`→`s30`, `diaChannel`→`s35`, `diaStorage`→`s48`.

`.dia-top`의 재생 버튼(`.dia-btn`)과 단계 점(`.dia-dots`)은 **남긴다** — 발표 중 특정 프레임으로 되돌아갈 때 쓴다.

- [ ] **Step 3: `wireDia`를 컨트롤러 반환형으로 고쳐 이식한다**

`ASSET:JS` 마커 사이에 `diaAt`(원본 2343–2352)과 아래를 넣는다.

```js
/* 출처: oauth2_tutorial.html 2343-2352(diaAt), 2354-2400(wireDia)
   변경점: 원본은 setTimeout 으로 스스로 재생한다. 덱에서는 덱이 비트를 몰아줘야
   하므로 자동재생을 걷어내고 컨트롤러를 돌려준다. steps[i].h 는 지우지 않고
   남긴다 — 시간 추정에 쓴다. */
function wireDia(id,steps){
  const fig=$('#'+id); if(!fig)return null;
  const cap=$('.dia-cap',fig), dots=$('.dia-dots',fig), btn=$('.dia-btn',fig);
  const n=steps.length;
  const marks=$$('[data-at]',fig).map(el=>({el:el,at:diaAt(el.dataset.at,n)}));

  dots.innerHTML='';
  for(let k=0;k<n;k++){
    const b=document.createElement('button');
    b.className='dia-dot'; b.type='button';
    b.setAttribute('aria-label',(k+1)+'단계로');
    b.addEventListener('click',()=>{ Deck.beat=k; applyBeat(fig.closest('.slide'),k); paint(); });
    dots.appendChild(b);
  }
  const dotEls=$$('.dia-dot',dots);

  let i=0;
  function paintDia(){
    fig.dataset.s=i;
    cap.innerHTML=steps[i].c;
    marks.forEach(m=>m.el.classList.toggle('vis',m.at.has(i)));
    dotEls.forEach((d,k)=>d.classList.toggle('on',k===i));
  }
  if(btn) btn.remove();   // 자동재생 버튼은 덱에서 의미가 없다 — → 가 그 자리를 대신한다
  paintDia();
  return { n:n, el:fig, go(k){ i=Math.max(0,Math.min(n-1,k)); paintDia(); } };
}
```

- [ ] **Step 4: `createSequence`를 컨트롤러 반환형으로 고쳐 이식한다**

원본(2161–2270 부근)을 복사하되 끝을 바꾼다. `.sq-*` 버튼들은 남긴다 — 질의응답 때 임의 단계로 가기 위해서다.

```js
/* 출처: oauth2_tutorial.html 2161-2270(createSequence)
   변경점: render() 를 컨트롤러로 노출하고, auto() 로 자동재생을 시작한다.
   s17·s51 의 mainSeq 만 auto() 를 쓴다 — 16단계를 키로 넘기면 3분 30초에
   들어오지 않고, 이 두 자리의 목적은 세부가 아니라 흐름의 윤곽이다. */
  // ... 원본 본문 유지 ...
  render();
  return {
    n: steps.length,
    go(k){ stop(); cur=Math.max(0,Math.min(steps.length-1,k)); render(); },
    auto(){ $('.sq-auto',wrap).click(); }
  };
}
```

- [ ] **Step 5: 라이브 데모 6개를 옮긴다**

본편 데모의 마크업과 JS를 옮긴다. **원본 함수 이름을 바꾸지 않는다** — 원본과 대조할 수 있어야 한다.

| 슬라이드 | 마크업 원본 줄 | JS 함수 (원본 줄) |
|---|---|---|
| `s20` | 917–959 (`#authUrl` 블록) | `renderAuthUrl` (2008–2019) |
| `s28` | 1161–1170 (`#stateOut` 블록) | `renderState` (2021–2028) |
| `s31` | 1266–1279 (`#pkceOut` 블록) | `sha256Base64Url`·`renderPkce` (2030–2041) |
| `s38` | `#apiOut` 블록 | `renderApiCall` (2042–2049) |
| `s40` | `#rotOut` 블록 | `ROT`·`renderRot` (2050–2057) |
| `s44`·`s45` | 1484–1510 (`#jwtRaw`·`#jwtDecoded`·`#jwtChecks`) | `b64url`~`renderJwt` (2059–2108) |

**JWT 데모는 두 슬라이드에 걸쳐 있으므로 마크업을 복제한다.**

`s44`는 정상 생성·검증(`#jwtBuild`), `s45`는 위변조와 nonce 불일치(`#jwtTamper`·`#jwtBadNonce`)를
보여 준다. 두 슬라이드가 같은 `#jwtRaw`·`#jwtDecoded`·`#jwtChecks`를 공유할 수는 없다 — id는
문서에서 유일해야 하고, 한쪽에만 두면 다른 쪽 슬라이드가 빈 화면이 된다.

그래서 **출력 영역 전체를 두 슬라이드에 각각 두고**, 바깥을 감싸는 컨테이너로 구분한다:

```html
<!-- s44 -->
<div class="jwt-demo" id="jwtDemo44"> …원본 1484-1510 의 버튼·출력 마크업… </div>
<!-- s45 -->
<div class="jwt-demo" id="jwtDemo45"> …같은 마크업, 버튼만 ②③… </div>
```

안쪽 id는 `jwtRaw`처럼 그대로 두되 **`document` 대신 컨테이너를 기준으로 찾는다.** `renderJwt`가
루트를 인자로 받도록 고친다 — 원본에서 바뀌는 것은 조회 기준 하나뿐이다:

```js
/* 출처: oauth2_tutorial.html 2059-2108
   변경점: $('#jwtRaw') → $('#jwtRaw', root). 같은 데모가 두 슬라이드에 있어서
   문서 전역으로 찾으면 항상 첫째 것만 갱신된다. */
async function renderJwt(mode, root){
  const $r=(sel)=>$(sel, root);
  // 원본 본문의 $('#jwtXxx') 를 전부 $r('#jwtXxx') 로 바꾼다. 나머지는 그대로.
}
```

버튼을 걸 때 각자의 루트를 넘긴다:

```js
  const r44=$('#jwtDemo44'), r45=$('#jwtDemo45');
  $('#jwtBuild',r44).addEventListener('click',()=>renderJwt('ok',r44));
  $('#jwtTamper',r45).addEventListener('click',()=>renderJwt('tamper',r45));
  $('#jwtBadNonce',r45).addEventListener('click',()=>renderJwt('nonce',r45));
```

**`s45`에 들어올 때 정상 토큰이 이미 만들어져 있어야** 위변조를 보여 줄 수 있다. `Deck.go` 끝의
자동재생 갈래 옆에 한 줄 더한다:

```js
    if(slide.id==='s45') renderJwt('ok', $('#jwtDemo45'));
```

이러면 `s45`에 도착하는 순간 정상 검증 결과가 떠 있고, 발표자는 버튼 하나로 그것이 무너지는
것을 보여 준다. 실패를 보여 주는 것이 이 슬라이드의 목적이므로 성공 상태가 먼저 있어야 한다.

- [ ] **Step 6: 이식한 자산을 비트에 등록한다**

`init()` 안, `Deck` 초기화 뒤에 넣는다.

```js
  registerBeats('s03', wireDia('diaDelegate',[/* 원본 wireDia('diaDelegate',[...]) 의 steps 그대로 */]));
  registerBeats('s07', wireDia('diaGate',[/* ... */]));
  registerBeats('s10', wireDia('diaActors',[/* ... */]));
  registerBeats('s13', wireDia('diaShape',[/* ... */]));
  registerBeats('s23', wireDia('diaPassword',[/* ... */]));
  registerBeats('s26', wireDia('diaCode',[/* ... */]));
  registerBeats('s30', wireDia('diaPkce',[/* ... */]));
  registerBeats('s35', wireDia('diaChannel',[/* ... */]));
  registerBeats('s48', wireDia('diaStorage',[/* ... */]));

  AUTOPLAY['s17']=createSequence('mainSeq17',{title:'Authorization Code + PKCE (+ OIDC) Flow',actors:MAIN_ACTORS,steps:MAIN_STEPS});
  AUTOPLAY['s51']=createSequence('mainSeq51',{title:'다시 한 바퀴',actors:MAIN_ACTORS,steps:MAIN_STEPS});
```

**등록은 최초 `Deck.go(0)` 보다 먼저 해야 한다.** 뒤에 두면 첫 슬라이드의 `applyBeat`가
컨트롤러 없이 돌아 첫 장만 규칙이 다르게 동작한다. `init()` 의 순서는
`Deck.slides/script 준비 → registerBeats·AUTOPLAY 등록 → Deck.go(0)` 이다.

`mainSeq`는 두 슬라이드에 있으므로 **마운트 id를 `mainSeq17`·`mainSeq51`로 나눈다.** 같은 id를 두 번 쓰면 둘째 것이 조용히 죽는다.

자동재생 레지스트리는 `BEATS` 와 같은 모양으로 **`DECK:CORE:JS` 에** 둔다. `Deck.go` 는
모듈 스코프 함수라 `init()` 안의 지역 변수를 볼 수 없다 — `const mainA` 를 만들어
`Deck.go` 에서 부르면 `ReferenceError` 로 자동재생이 죽는다:

```js
/* DECK:CORE:JS — BEATS 옆에 둔다 */
const AUTOPLAY={};          // slideId -> {auto()}
```

`Deck.go` 의 `applyBeat(slide,this.beat);` 다음 줄에 추가:

```js
    if(AUTOPLAY[slide.id]) AUTOPLAY[slide.id].auto();
```

- [ ] **Step 7: 프레임 일치 검사를 검사기에 추가한다 — 먼저 테스트**

`tools/testdata/deck_frame_mismatch.html`을 만든다. `.dia` 하나에 `data-at="0"`·`data-at="1"`만 있고 `wireDia`에는 `{c:...}`가 셋인 파일.

`tools/test_check_slides.py`에 추가:

```python
def test_frame_count_mismatch_is_reported():
    problems = cs.check_dia_frames(deck('deck_frame_mismatch.html'))
    assert len(problems) == 1
    assert 'diaX' in problems[0]


def test_ok_fixture_has_no_dia_to_check():
    assert cs.check_dia_frames(deck('deck_ok.html')) == []
```

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: FAIL — `AttributeError: module 'check_slides' has no attribute 'check_dia_frames'`

- [ ] **Step 8: 프레임 일치 검사를 구현한다**

`tools/check_slides.py`에 추가하고 `CHECKS`에 등록한다.

```python
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
```

`CHECKS`를 고친다: `CHECKS = [check_script_present, check_slide_seconds, check_total, check_dia_frames]`

- [ ] **Step 9: 테스트와 검사기를 돌린다**

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: 10개 PASS

Run: `python3 tools/check_slides.py oauth2_slides.html`
Expected: 프레임 위반 0건. (대본 합계 위반은 Task 7까지 남는다.)

**대조 확인**: 원본에서도 같은 검사가 통과해야 한다 —
Run: `python3 tools/check_slides.py oauth2_tutorial.html` 는 SLIDES 마커가 없어 실패한다. 대신 프레임 수를 손으로 대조한다: `diaDelegate 7, diaGate 7, diaActors 7, diaShape 7, diaPassword 6, diaCode 6, diaPkce 7, diaChannel 6, diaStorage 6`.

- [ ] **Step 10: 커밋**

```bash
git add oauth2_slides.html tools/check_slides.py tools/test_check_slides.py tools/testdata/deck_frame_mismatch.html
git commit -m "자산 이식: 다이어그램 9개·시퀀스·라이브 데모 6개 + 프레임 일치 검사"
```

---

## Task 6: 본편 53장 콘텐츠

**Files:**
- Modify: `oauth2_slides.html` (`SLIDES`)
- Modify: `tools/check_slides.py` (글자 크기 하한 검사 추가)
- Modify: `tools/test_check_slides.py`

**Interfaces:**
- Consumes: Task 5의 자산 배치, Task 3의 `.build[data-beat]`
- Produces: `s00`~`s52` 53개 `<section class="slide">`. 각 슬라이드는 `<h2>` 하나를 갖는다 — 개요 그리드와 발표자 창이 제목으로 쓴다

- [ ] **Step 1: 슬라이드 대장대로 53장을 만든다**

위 "슬라이드 대장 — 본편 53장" 표의 id·제목·자산·비트를 그대로 따른다. 자산이 있는 슬라이드는 Task 5에서 이미 SVG가 들어가 있다.

**슬라이드 작성 규칙:**

- `<h2>`는 그 장이 **답하는 질문 또는 하는 주장**이다. 개념 이름을 제목으로 쓰지 않는다. (튜토리얼 설계문서가 세운 규칙을 그대로 잇는다)
- 화면에 문장을 늘어놓지 않는다. **말할 것은 대본으로, 화면에는 남길 것만.** 슬라이드 본문은 한 장에 `<p>` 세 줄을 넘기지 않는다
- 단계가 있는 내용은 `.build[data-beat]`로 하나씩 연다
- 글자 크기 하한: 본문 24px, 코드 20px. **인라인 `style`로 이보다 작게 쓰지 않는다**

본문 슬라이드의 표준 꼴 (`s04`):

```html
  <section class="slide" id="s04">
    <h2>앱이 받는 건 비밀번호가 아니라 <em>권한이 좁은 토큰</em></h2>
    <p class="build" data-beat="0">같은 앱인데, 열 수 있는 것이 <b>사진 읽기 하나</b>로 줄었습니다.</p>
    <p class="build" data-beat="1">바꾼 것은 <b>경로 하나</b>뿐입니다.</p>
  </section>
```

다이어그램 슬라이드의 표준 꼴 (`s03`):

```html
  <section class="slide" id="s03">
    <h2>비밀번호 대신, 좁은 열쇠 하나</h2>
    <figure class="dia" id="diaDelegate"><!-- Task 5 에서 이식한 SVG 그대로 --></figure>
  </section>
```

- [ ] **Step 2: 퀴즈 4개를 놓는다**

`s18`·`s33`·`s46`·`s52`에 원본 `.quiz` 마크업을 옮긴다. 원본 13개 중 각 위치에 맞는 것을 고른다: `s18`←`q-bigpic`, `s33`←`q-pkce`, `s46`←OIDC 퀴즈 하나, `s52`←`q-tokens`. 나머지 9개는 Task 8에서 `a12`·`a13`으로 간다.

원본 `wireQuizzes`(1964–1970)를 `ASSET:JS`로 옮기고 `init()`에서 호출한다.

- [ ] **Step 3: 글자 크기 검사를 추가한다 — 먼저 테스트**

`tools/testdata/deck_small_text.html`을 만든다. `<p style="font-size:18px">`이 든 슬라이드 하나짜리 덱.

`tools/test_check_slides.py`에 추가:

```python
def test_inline_font_size_below_floor_is_reported():
    problems = cs.check_font_floor(deck('deck_small_text.html'))
    assert len(problems) == 1
    assert '18' in problems[0]


def test_ok_fixture_passes_font_floor():
    assert cs.check_font_floor(deck('deck_ok.html')) == []
```

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: FAIL — `check_font_floor` 없음

- [ ] **Step 4: 글자 크기 검사를 구현한다**

```python
FONT_FLOOR = 24          # px, 1280 좌표계 기준 본문 하한
FONT_FLOOR_MONO = 20     # px, 코드 하한
INLINE_FONT = re.compile(
    r'''<([a-zA-Z][\w-]*)\b[^>]*\bstyle\s*=\s*["'][^"']*font-size\s*:\s*(\d+(?:\.\d+)?)px''')


def check_font_floor(deck):
    """인라인 style 의 font-size 하한. 무대에서 뒷자리가 못 읽는 글자를 막는다.
    CSS 클래스 쪽 크기는 DECK:CORE:CSS 가 책임진다 — 여기서는 손으로 박은 값만 본다."""
    problems = []
    block = SLIDES_BLOCK.search(deck.html)
    if not block:
        return problems
    for tag, size in INLINE_FONT.findall(block.group(1)):
        floor = FONT_FLOOR_MONO if tag in ('code', 'pre') else FONT_FLOOR
        if float(size) < floor:
            problems.append('<%s> 인라인 font-size %spx — 하한 %dpx 미만'
                            % (tag, size, floor))
    return problems
```

`CHECKS`에 `check_font_floor`를 추가한다.

- [ ] **Step 5: 검사를 돌린다**

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: 12개 PASS

Run: `python3 tools/check_slides.py oauth2_slides.html`
Expected: 슬라이드 53장으로 읽힌다. 대본 미작성분이 `대본이 없다`로 보고된다 (Task 7에서 해소).

- [ ] **Step 6: 개요 그리드로 눈 검사**

브라우저에서 `O`를 눌러 53장을 한 화면에 놓는다. **글자만 빽빽한 슬라이드를 찾아 쪼갠다.** 발표 자료가 문서로 되돌아가는 실패는 여기서 한눈에 보인다.

- [ ] **Step 7: 커밋**

```bash
git add oauth2_slides.html tools/check_slides.py tools/test_check_slides.py tools/testdata/deck_small_text.html
git commit -m "본편 53장 + 글자 크기 하한 검사"
```

---

## Task 7: 대본 53장 — 시간을 숫자로 맞춘다

**설계 문서 11절의 확인 지점 2.**

**Files:**
- Modify: `oauth2_slides.html` (`<script type="application/json" id="deck-script">`)

**Interfaces:**
- Consumes: Task 1의 `seconds()` 계산 규약 (공백 제외 글자 수 ÷ 5.5)
- Produces: `s00`~`s52` 전부에 대한 대본. 합계 3120초 ±180초

- [ ] **Step 1: 대본을 쓴다**

**규칙:**
- **그대로 읽으면 발표가 되는 완성된 문장.** 불릿이 아니다. 그래야 글자 수로 시간이 계산되고, 다른 사람이 대신 발표할 수 있다
- 슬라이드에 이미 쓰여 있는 문장을 그대로 읽지 않는다. 화면은 뼈대, 대본은 살이다
- 다이어그램 슬라이드의 대본은 **원본 `wireDia` steps의 `c` 캡션을 뼈대로 삼는다.** 이미 구어체이고 프레임 순서에 맞춰져 있다. 문어체 잔재만 다듬는다
- 시퀀스 슬라이드(`s17`·`s51`)는 자동재생이므로 **재생 시간에 맞춰** 쓴다
- 장과 장 사이는 "그래서 다음 문제가 생깁니다" 꼴로 잇는다 — 원본 튜토리얼의 전개 규칙이다

배분 목표 (설계 문서 6절):

| 파트 | 슬라이드 | 목표 |
|---|---|---|
| 0 (s00–s01) | 2 | 2:00 |
| 1 (s02–s05) | 4 | 3:30 |
| 2 (s06–s08) | 3 | 3:00 |
| 3 (s09–s11) | 3 | 3:00 |
| 4 (s12–s15) | 4 | 3:00 |
| 5 (s16–s18) | 3 | 3:30 |
| 6 (s19–s21) | 3 | 2:30 |
| 7 (s22–s24) | 3 | 3:00 |
| 8 (s25–s28) | 4 | 4:00 |
| 9 (s29–s33) | 5 | 5:30 |
| 10 (s34–s36) | 3 | 3:00 |
| 11 (s37–s38) | 2 | 2:00 |
| 12 (s39–s41) | 3 | 3:00 |
| 13 (s42–s46) | 5 | 5:30 |
| 14 (s47–s50) | 4 | 3:30 |
| 15 (s51–s52) | 2 | 2:00 |
| **계** | **53** | **52:00** |

목표 초 × 5.5 = 그 파트의 목표 글자 수. 예: 파트 9는 330초 × 5.5 = **1,815자**.

- [ ] **Step 2: 합계를 잰다**

Run: `python3 tools/check_slides.py oauth2_slides.html`

Expected: `대본 합계 52:xx` 가 49:00~55:00 안. 벗어나면 **길이를 조절해 다시 잰다.** 늘리지 말고 깎는 쪽을 먼저 본다 — 발표는 언제나 예상보다 늘어진다.

- [ ] **Step 3: 파트별 배분을 확인한다**

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0,'tools')
import check_slides as cs
d = cs.read_deck('oauth2_slides.html')
parts = [('0',0,1),('1',2,5),('2',6,8),('3',9,11),('4',12,15),('5',16,18),
         ('6',19,21),('7',22,24),('8',25,28),('9',29,33),('10',34,36),
         ('11',37,38),('12',39,41),('13',42,46),('14',47,50),('15',51,52)]
goal = {'0':120,'1':210,'2':180,'3':180,'4':180,'5':210,'6':150,'7':180,
        '8':240,'9':330,'10':180,'11':120,'12':180,'13':330,'14':210,'15':120}
tot=0
for name,a,b in parts:
    s=sum(cs.seconds(d.script.get('s%02d'%i,[])) for i in range(a,b+1))
    tot+=s
    g=goal[name]; mark='ok' if abs(s-g)<=25 else '<<<'
    print(f"파트{name:>3}  {cs._fmt(s)}  목표 {cs._fmt(g)}  차 {s-g:+.0f}초  {mark}")
print(f"합계 {cs._fmt(tot)}  목표 52:00  차 {tot-3120:+.0f}초")
EOF
```

Expected: 파트별 차이가 ±25초 안. `<<<`가 찍힌 파트를 조절한다.

- [ ] **Step 4: 슬라이드별 상·하한을 확인한다**

Run: `python3 tools/check_slides.py oauth2_slides.html`
Expected: `상한 110초를 넘는다` / `하한 25초에 못 미친다` 위반 0건. 상한을 넘으면 그 슬라이드를 둘로 쪼갠다(슬라이드 수가 늘면 대장 표를 함께 고친다). 하한에 못 미치면 앞뒤와 합친다.

- [ ] **Step 5: 커밋**

```bash
git add oauth2_slides.html
git commit -m "본편 대본 53장 — 합계 52분"
```

- [ ] **Step 6: 확인 지점 — 사용자에게 보고하고 멈춘다**

Step 2·3의 출력(합계와 파트별 배분)을 그대로 보고한다. 시간이 맞는지, 대본의 말투가 맞는지 확인받는다.

---

## Task 8: 부록 14장

**Files:**
- Modify: `oauth2_slides.html` (`SLIDES`, `ASSET:JS`, `deck-script`)
- Modify: `tools/check_slides.py` (부록을 합계에서 제외)
- Modify: `tools/test_check_slides.py`

**Interfaces:**
- Consumes: Task 5의 `wireDia`·`createSequence` 컨트롤러, Task 3의 `registerBeats`
- Produces: `a00`~`a13` 14개 슬라이드. `<section class="slide appendix" id="a00">` — `appendix` 클래스로 구분한다

- [ ] **Step 1: 부록을 합계에서 빼도록 검사기를 고친다 — 먼저 테스트**

부록 대본은 52분 합계에 들어가면 안 된다. **발표하지 않는 장이기 때문이다.**

`tools/testdata/deck_with_appendix.html`을 만든다 — `deck_ok.html`에 `<section class="slide appendix" id="a00">`과 그 대본을 더한 파일.

```python
def test_appendix_slides_are_excluded_from_total():
    d = deck('deck_with_appendix.html')
    assert 'a00' in d.script
    assert d.main_slides == ['s00', 's01']       # 부록 제외
    assert d.slides == ['s00', 's01', 'a00']     # 전체는 포함


def test_appendix_slide_still_needs_script():
    d = deck('deck_with_appendix.html')
    assert cs.check_script_present(d) == []
```

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: FAIL — `Deck` 에 `main_slides` 없음

- [ ] **Step 2: 검사기를 고친다**

`Deck` namedtuple에 `main_slides`를 더한다. `read_deck`에서 `class`에 `appendix`가 없는 슬라이드만 모은다.

```python
Deck = namedtuple('Deck', 'html slides main_slides script')

CLASS_ATTR = re.compile(r'''\bclass\s*=\s*["']([^"']+)["']''')
```

`read_deck`의 슬라이드 수집을 고친다:

```python
    slides, main_slides = [], []
    for tag in SLIDE_TAG.findall(block.group(1)):
        m = ID_ATTR.search(tag)
        if not m:
            raise ValueError('%s: id 없는 .slide 가 있다 — %s' % (path, tag[:60]))
        sid = m.group(1)
        slides.append(sid)
        classes = CLASS_ATTR.search(tag)
        if not (classes and 'appendix' in classes.group(1).split()):
            main_slides.append(sid)
```

**반환문도 함께 고친다.** namedtuple 필드가 넷이 됐으므로 Task 1의 3-인자 생성자는 그대로
두면 `TypeError`가 난다:

```python
    return Deck(html=html, slides=slides, main_slides=main_slides, script=script)
```

`check_total`이 `deck.main_slides`를 쓰도록 고치고, 보고 문구에 부록 장 수를 덧붙인다:

```python
def check_total(deck):
    total = sum(seconds(deck.script.get(sid, [])) for sid in deck.main_slides)
    lo, hi = TOTAL_TARGET - TOTAL_TOL, TOTAL_TARGET + TOTAL_TOL
    if not (lo <= total <= hi):
        return ['본편 대본 합계 %s — 목표 %s ±%s 를 벗어난다 (허용 %s~%s)'
                % (_fmt(total), _fmt(TOTAL_TARGET), _fmt(TOTAL_TOL), _fmt(lo), _fmt(hi))]
    return []
```

`main`의 출력도 본편/부록을 나눠 찍는다:

```python
        n_app = len(deck.slides) - len(deck.main_slides)
        total = sum(seconds(deck.script.get(s, [])) for s in deck.main_slides)
        print('%s — 본편 %d장(%s) + 부록 %d장'
              % (path, len(deck.main_slides), _fmt(total), n_app))
```

- [ ] **Step 3: 테스트를 돌린다**

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: 14개 PASS

- [ ] **Step 4: 부록 14장을 만든다**

위 "슬라이드 대장 — 부록 14장" 표대로. 자산 이식:
- `a02` ← `nativeSeq` (`NATIVE_ACTORS`/`NATIVE_STEPS`, 9단계)
- `a03` ← `deviceSeq` (`DEVICE_ACTORS`/`DEVICE_STEPS`, 10단계)
- `a04` ← `diaSecret` (원본 1626–1672, 6프레임)
- `a05` ← `#platPicks`·`renderPlat`
- `a07` ← `ccSeq` (`CC_ACTORS`/`CC_STEPS`, 4단계)
- `a10` ← `#tokenChoiceOut`·`renderTokenChoice`
- `a11` ← `#consoleOut`·`CONSOLE`
- `a12`·`a13` ← 남은 퀴즈 9개

`init()`에 등록한다:

```js
  registerBeats('a04', wireDia('diaSecret',[/* 원본 steps 그대로 */]));
  createSequence('nativeSeq',{title:'CLI · 네이티브 앱 로그인',actors:NATIVE_ACTORS,steps:NATIVE_STEPS,hasCheck:true});
  createSequence('deviceSeq',{title:'디바이스 코드 흐름',actors:DEVICE_ACTORS,steps:DEVICE_STEPS});
  createSequence('ccSeq',{title:'Client Credentials Flow',actors:CC_ACTORS,steps:CC_STEPS});
```

부록 대본도 쓴다 — 질의응답에서 꺼낼 때 읽을 문장이다. 짧아도 된다(25초 하한은 지킨다).

- [ ] **Step 5: `A` 키로 부록 첫 장에 점프하도록 한다**

`onKey`에 추가:

```js
    case 'a': case 'A': {
      const i=Deck.slides.findIndex(s=>s.classList.contains('appendix'));
      if(i>=0) Deck.go(i);
      break;
    }
```

개요 그리드에서 부록을 구분되게 표시한다 — `toggleOverview`의 셀 생성에서 `appendix`면 `.ov-cell`에 흐린 배경을 준다.

- [ ] **Step 6: 검사를 돌린다**

Run: `python3 tools/check_slides.py oauth2_slides.html`
Expected: `본편 53장(52:xx) + 부록 14장`, 위반 0건

- [ ] **Step 7: 커밋**

```bash
git add oauth2_slides.html tools/check_slides.py tools/test_check_slides.py tools/testdata/deck_with_appendix.html
git commit -m "부록 14장 + A 키 점프, 부록은 합계에서 제외"
```

---

## Task 9: 마무리 검사 — 죽은 CSS · 외부 요청 · 완주

**Files:**
- Modify: `oauth2_slides.html` (죽은 CSS 제거)
- Create: `docs/superpowers/notes/2026-08-20-oauth2-slides-known-issues.md`

**Interfaces:**
- Consumes: Task 1~8의 전부
- Produces: 파일럿 통과 여부 판정과 남은 문제 기록

- [ ] **Step 1: 죽은 CSS를 찾는다**

Run: `python3 tools/check_dead_css.py --report oauth2_slides.html`

Task 5에서 통째로 옮긴 `Content` 블록(원본 88–175)에 덱이 안 쓰는 규칙이 남아 있다. 보고된 셀렉터를 확인하고 `ASSET:CSS`에서 지운다. **`.dia`·`.seq` 규칙은 SVG 클래스라 정적 분석이 놓칠 수 있으므로, 지우기 전에 그 클래스가 SVG 안에 있는지 직접 확인한다.**

- [ ] **Step 2: 외부 요청 금지를 확인한다**

Run: `python3 tools/check_tutorial.py oauth2_slides.html`
Expected: 원격 리소스·`fetch`·`XMLHttpRequest`·`new Image` 위반 0건

- [ ] **Step 3: 전체 테스트를 돌린다**

Run: `python3 -m pytest tools/ -v`
Expected: 검사기 테스트 14개 PASS. 동작 테스트 15개 PASS 또는 SKIP.

- [ ] **Step 4: 완주 검사**

브라우저에서 `oauth2_slides.html`을 열고 **`→`만 눌러 처음부터 끝까지 간다.** 확인할 것:
- 67장 내내 끊김 없이 진행되는가 — 특히 다이어그램 프레임이 다 소진된 뒤 다음 장으로 넘어가는 이음매
- `s17`·`s51`에서 `mainSeq` 자동재생이 시작되는가
- 라이브 데모 6개가 실제로 도는가 — 특히 `s31`의 SHA-256과 `s44`·`s45`의 JWT 서명 검증(WebCrypto)
- `s45`의 위변조·nonce 버튼이 `s44`의 출력을 건드리지 않는가
- `P`로 발표자 창이 뜨고 따라 움직이는가
- 브라우저 콘솔에 오류가 없는가

- [ ] **Step 5: 남은 문제를 기록한다**

`docs/superpowers/notes/2026-08-20-oauth2-slides-known-issues.md`에 완주 검사에서 발견한 것, 고치지 않고 남긴 것과 그 이유를 적는다. 이 저장소의 `2026-08-14-known-issues.md` 형식을 따른다.

- [ ] **Step 6: 커밋**

```bash
git add oauth2_slides.html docs/superpowers/notes/2026-08-20-oauth2-slides-known-issues.md
git commit -m "마무리 검사: 죽은 CSS 제거·완주 확인·남은 문제 기록"
```

- [ ] **Step 7: 파일럿 통과 판정을 보고한다**

설계 문서 10절의 세 층 검사 결과를 사용자에게 보고한다. 통과면 `index.html` 편입과 나머지 7편 확장을 논의하고, 통과가 아니면 무엇이 문제였는지와 선택지를 제시한다.

**`index.html` 편입과 `tools/build_slides.py` 추출은 이 계획의 범위 밖이다.** 설계 문서 12절대로 파일럿 통과 후에 별도로 정한다.
