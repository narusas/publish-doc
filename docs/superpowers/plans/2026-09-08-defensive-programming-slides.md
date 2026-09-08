# 방어적 프로그래밍 발표 덱 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `defensive_programming.html`의 자산을 재사용해 이커머스 운영 개발팀(방어적 프로그래밍을 몰라서 못 하는 개발자) 대상 52분 발표 덱 `defensive_programming_slides.html`(본편 54장 + 부록 13장)을 만들고, OAuth2 파일럿의 덱 엔진을 바이트 단위로 공유한다.

**Architecture:** 자체완결 단일 HTML. 1280×720 고정 좌표계, 오른쪽 화살표 하나로 굴러가는 비트 체계, JSON 대본 블록은 파일럿(`oauth2_slides.html`) 그대로다. 엔진 네 블록(`DECK:CORE:CSS` · `DECK:CORE:JS` · `DECK:CHROME` 두 조각)은 파일럿에서 복사하고 두 덱을 바이트 단위로 대조하는 테스트로 묶는다. 원본 튜토리얼의 도해 열 장과 데모 넷을 `{n, go(k)}` 컨트롤러로 감싸 비트에 매단다. 여섯 반경이 여섯 막이고, 막마다 전과 후 코드 한 쌍, "내일 할 것" 한 장, 퀴즈 하나로 닫는다.

**Tech Stack:** 순수 HTML/CSS/JS (빌드 도구 없음, 외부 요청 없음). 검사기는 Python 3 표준 라이브러리. 브라우저 동작 테스트는 pytest + Playwright(chromium).

**Spec:** `docs/superpowers/specs/2026-09-08-defensive-programming-slides-design.md` (선행: `docs/superpowers/specs/2026-08-20-tutorial-slides-design.md`)

## Global Constraints

- **외부 요청 금지.** CDN·폰트·이미지 원격 로드, `fetch`/`XMLHttpRequest`/`new Image` 전부 금지. `tools/check_slides.py`의 `check_no_external`이 강제한다.
- **단일 파일.** `defensive_programming_slides.html` 하나에 CSS·JS·SVG·Prism 이 전부 들어간다.
- **`file://`에서 동작.** `localStorage`·`BroadcastChannel`·`fetch`에 의존하지 않는다. 원본의 `Store`는 아무것도 기억하지 않는 스텁으로 둔다.
- **대본 속도 상수 5.5자/초.** 덱과 검사기가 같은 값을 쓴다.
- **대본 목표 3120초 ±180초 (52:00 ±3:00).** 부록은 합계에서 뺀다.
- **슬라이드당 대본 25초~110초.** 부록도 같다.
- **글자 크기 하한(1280 좌표계): 본문 24px, 코드 20px.** 예외는 `DECK:STAGE:CSS`의 「예외 목록 시작/끝」 블록과 `tools/test_deck_behavior.py`의 `EXEMPT`에 한 글자씩 같게 적는다. 이 덱은 `[svg, svg *] 바닥 12px` 한 줄로 시작한다.
- **본편 금지어.** 본편 슬라이드 텍스트와 본편 대본에 다음 낱말이 나오면 검사기가 실패한다: 불변식, 사전조건, 사후조건, 격벽, 회로 차단기, 멱등, 백오프, 지터, 값 타입, 검사 예외, 비검사 예외, 리플렉션. 부록에는 허용한다.
- **본편 개념어 다섯.** 경계, 격리, 빨리 죽기·버티기, 폴백, 요건 문장. 처음 나오는 장의 대본에서 한 문장으로 풀어 쓴다.
- **전과 후 코드 규격.** 한 판 여덟 줄 이하, 한 줄 45자 이하, 바뀐 줄 표시(`.chg`)는 한 판에 셋 이하.
- **각색 유지.** 사내 식별자를 쓰지 않는다. `bannerImageList`·`mainSections_jsp`·`SectionContent`·`SectionVO` 등 원본이 쓰는 이름만 쓴다. 원인을 단정하지 않는다.
- **한국어 문장 규칙.** `~/.claude/output-styles/fluent-korean.md`를 따른다. 대본은 그대로 읽으면 발표가 되는 완성된 문장이다.
- **커밋은 파일을 지정해서.** `git add -A`·`git add .`를 쓰지 않는다. 이 저장소에는 상시 미커밋 상태인 91MB 음성 파일(`auth_basics_full.m4a`)과 이 작업과 무관한 `docs/superpowers/notes/2026-08-14-known-issues.md` 수정이 있다.
- **브랜치.** `defprog-slides` (설계 문서 커밋 `7c1304d`가 첫 커밋이다).

---

## 파일 구조

| 파일 | 책임 |
|---|---|
| `defensive_programming_slides.html` (신규) | 덱 전체. 아래 마커로 구획된다 |
| `tools/check_slides.py` (수정) | `data-frames` 선언, 컨트롤러 넷의 마운트 검사, 본편 금지어 검사 |
| `tools/test_check_slides.py` (수정) | 두 덱 순회, 새 검사의 픽스처 테스트, 엔진 네 블록 동일성 |
| `tools/test_deck_behavior.py` (수정) | 두 덱 순회, 덱별 활자 예외 목록, `data-frames` 실측, 컨트롤러 넷 동작 |
| `tools/testdata/deck_frames_declared.html` 등 (신규) | 새 검사의 최소 픽스처 |

덱 내부 마커. **이 문자열 그대로** 쓴다. 검사기와 테스트가 이 문자열로 블록을 찾는다.

```
/* ==== DECK:CORE:CSS ==== */ … /* ==== /DECK:CORE:CSS ==== */
/* ==== DECK:STAGE:CSS ==== */ … /* ==== /DECK:STAGE:CSS ==== */
/* ==== ASSET:CSS ← defensive_programming.html ==== */ … /* ==== /ASSET:CSS ==== */
<!-- ==== DECK:CHROME ==== --> … <!-- ==== /DECK:CHROME ==== -->   (두 조각)
<!-- ==== SLIDES ==== -->  …  <!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">
/* ==== DECK:CORE:JS ==== */ … /* ==== /DECK:CORE:JS ==== */
/* ==== ASSET:JS ← defensive_programming.html ==== */ … /* ==== /ASSET:JS ==== */
```

## 원본 자산 좌표 (확인 완료 · `defensive_programming.html` 5,744줄 기준)

| 블록 | 줄 | 처리 |
|---|---|---|
| Prism 테마 `<style id="prism-theme">` | 8–10 | 그대로 옮긴다 (`<head>`, `<style>` 앞) |
| `<style>` | 11–662 | 아래 범위만 골라 `ASSET:CSS`로 |
| `:root` 변수 | 15–44 | 옮기되 `--bg`·`--text-dim`·`--text-mut` 세 줄은 뺀다 (`DECK:STAGE:CSS`가 정한다) |
| `.quiz` 일가 | 176–193 | 옮긴다 |
| `.trace` | 266–271 | 옮긴다 |
| `.gap` | 284–288 | 옮긴다 |
| `.demo` | 305–309 | 옮긴다 (`.demo-tag` 315–320은 뺀다) |
| `.picker` `.pick` `.verdict` | 321–331 | 옮긴다 |
| `.kv` | 336–338 | 옮긴다 |
| `.tog` | 348–360 | 옮긴다 |
| `.asm-*` `.ctl-*` | 376–398 | 옮긴다 |
| `.jcard` 일가 | 399–420 | 옮긴다 |
| `.wgrid` `.wfield` `.reqout` | 452–465 | 옮긴다 |
| 도해 `.dia` 일가 | 531–662 | 옮긴다 (`.dia-btn`·`.dia.paused`·`.busy`처럼 죽는 것은 Task 9 에서 지운다) |
| Prism 본체·JSP 문법 `<script>` 두 개 | 4302–4349 | 그대로 옮기되 첫 `<script>` 태그에 `data-manual` 을 단다 |
| `$` `$$` | 4382–4383 | 옮기지 않는다 (`DECK:CORE:JS`에 같은 것이 있다) |
| `Store` | 4384–4387 | 옮기지 않는다. 스텁으로 대체 |
| `wirePicker` | 4557–4563 | 옮기지 않는다. 컨트롤러가 직접 배선 |
| `RADIUS` | 4567–4580 | 그대로 |
| `paintRadiusDia` | 4595–4626 | 그대로 |
| `diaAt` | 4642–4655 | 옮기지 않는다. 파일럿 `oauth2_slides.html` 2579–2588 의 것을 쓴다 (같은 함수) |
| `wireDia` | 4656–4726 | 옮기지 않는다. 파일럿 2590–2620 의 덱판을 쓴다 |
| `wireDia(...)` 단계 배열 아홉 | 4727–4799 | 그대로, `registerBeats` 로 감싼다 |
| `diaRadius` 단계 (`RADIUS.map`) | 4805–4816 | `radiusSteps()` 함수로 감싼다 |
| `EL` 모듈 | 4822–4849 | 그대로 |
| `EL` 배선 IIFE | 4852–4876 | `wireEl`로 다시 쓴다 |
| `Assembly` 엔진 | 5058–5148 | 그대로 |
| `SECTION_STATE` `renderAssembly` `buildControls` | 5156–5268 | 그대로 |
| D8 `CARDS` `VERDICT` | 5332–5351 | 최상위 `JUDGE_CARDS`·`JUDGE_VERDICT`로 끌어올린다 |
| D8 배선 IIFE | 5325–5413 | `wireJudge`로 다시 쓴다 |
| `QUESTIONS` | 5420–5449 | 그대로 |
| D10 `SLOTS` | 5520–5525 | 최상위 `WORD_SLOTS`로 끌어올린다 |
| D10 배선 IIFE | 5511–5670 | `wireWord`로 다시 쓴다 (`EXAMPLES`·질문 select·복사 버튼은 뺀다) |
| 스택트레이스 `pre.trace` | 696–707 | 마크업 그대로 |
| 퀴즈 15개 `.quiz` | `data-qid` 로 찾는다 | 마크업 그대로 |

도해 좌표와 프레임 수:

| id | 줄 | 프레임 | 덱 자리 |
|---|---|---|---|
| `diaBlame` | 823 | 6 | s06 |
| `diaSilent` | 1120 | 6 | s08 |
| `diaBoundary` | 1342 | 4 | s13 |
| `diaShape` | 1595 | 4 | s17 |
| `diaCommit` | 1803 | 5 | s23 |
| `diaLayers` | 2002 | 5 | s24 |
| `diaPool` | 2372 | 5 | s33 |
| `diaBudget` | 2473 | 5 | a02 |
| `diaSpecGap` | 2921 | 6 | s40 |
| `diaRadius` | 3696 | 6 (실행 시 생성) | s04 `diaRadiusIntro` · s51 `diaRadiusRecap` |

파일럿 `oauth2_slides.html`(3,204줄) 좌표:

| 블록 | 줄 |
|---|---|
| `DECK:CORE:CSS` | 8–137 |
| `DECK:STAGE:CSS` | 139–430 (참고용. 이 덱은 새로 쓴다) |
| `DECK:CHROME` 첫 조각 | 748–760 |
| `DECK:CHROME` 둘째 조각 | 2094–2102 |
| `DECK:CORE:JS` | 2177–2570 |
| `diaAt` · `wireDia`(덱판) | 2579–2620 |
| `wireQuizBank` | 2916–2922 |
| `wireQuizzes` | 3137–3143 |
| 부트 한 줄 | 3199 |

## 슬라이드 대장 — 본편 54장

"초"는 대본 목표다. 비트는 `.build` 단계 수와 컨트롤러 `n` 중 큰 쪽이다.

| id | 제목 (`<h2>`) | 자산 · 비트 | 초 |
|---|---|---|---|
| `s00` | 방어적 프로그래밍 — 하나가 죽었을 때 전체가 죽지 않게 | 1 | 30 |
| `s01` | 지난 9월 7일, 메인페이지가 통째로 오류를 냈습니다 | `pre.trace` · 1 | 60 |
| `s02` | 이 열 줄 안에 범인이 있을까요. 없습니다 | build 3 · 4 | 50 |
| `s03` | 방어적 프로그래밍은 예외를 없애는 기술이 아닙니다 | build 2 · 3 | 50 |
| `s04` | 오늘의 약속 두 문장, 그리고 여섯 반경 | `diaRadiusIntro`(고정) + build 2 · 3 | 50 |
| `s05` | 반경 1 · 한 줄 — 터진 자리와 잘못된 자리는 다른 곳입니다 | 막 표지 · 1 | 30 |
| `s06` | 스택트레이스는 호출이 지나온 길이지 값이 지나온 길이 아닙니다 | `diaBlame` · 6 | 90 |
| `s07` | 같은 식에 다섯 값 — null 은 조용하고 문자열은 시끄럽습니다 | `elLab07` · 5 | 80 |
| `s08` | 조용한 쪽이 더 위험합니다 | `diaSilent` · 6 | 80 |
| `s09` | 전과 후 ① — 잡고 로그만 남기는 catch | 코드 쌍 · 2 | 70 |
| `s10` | 예외에 담을 세 조각, 담지 말아야 할 것 하나 | build 4 · 5 | 50 |
| `s11` | 이 스택트레이스만 보고 확실하게 말할 수 있는 것은? | 퀴즈 `q-trace` + build · 2 | 45 |
| `s12` | 내일 할 것 ① — catch 뒤에 로그만 있는 자리 | build 3 · 3 | 35 |
| `s13` | 반경 2 · 한 함수 — 검증을 미룬 만큼 늘어나는 거리 | `diaBoundary` · 4 | 90 |
| `s14` | 전과 후 ② — 곳곳의 null 검사 | 코드 쌍 · 2 | 70 |
| `s15` | 원인이 셋 중 무엇이든, 선을 그을 자리는? | 퀴즈 `q-boundary` + build · 2 | 45 |
| `s16` | 내일 할 것 ② — 외부 응답이 우리 객체가 되는 자리 | build 3 · 3 | 35 |
| `s17` | 반경 3 · 한 객체 — 무엇이든 담기는 모델이 치르는 대가 | `diaShape` · 4 | 75 |
| `s18` | 전과 후 ③ — `Map<String, Object>` | 코드 쌍 · 2 | 70 |
| `s19` | 내일 할 것 ③ — 새 화면 모델은 클래스로 | build 3 · 3 | 35 |
| `s20` | 반경 4 · 한 모듈 — 섹션 하나가 죽어서 메인이 죽었습니다 | 막 표지 · 1 | 30 |
| `s21` | 여덟 섹션, 하나에 예외를 넣으면 | `asmLab21` · 2 | 75 |
| `s22` | 화면은 여덟 칸인데 코드는 한 흐름입니다 — 141번째 c:set | build 2 · 3 | 45 |
| `s23` | 응답이 이미 나간 뒤에는 되돌릴 것이 없습니다 | `diaCommit` · 5 | 80 |
| `s24` | 같은 예외, 네 층 — 대안이 있는 층만 삼킬 수 있습니다 | `diaLayers` + build(data-beat 5) · 6 | 90 |
| `s25` | 빨리 죽을 자리와 버틸 자리 — 여덟 장을 직접 골라 봅시다 | `judgeLab25` · 8 | 85 |
| `s26` | 기준은 하나입니다 | build 2 · 3 | 60 |
| `s27` | 오늘 사건은 두 문장을 동시에 틀렸습니다 | build 2 · 3 | 40 |
| `s28` | 격리를 켜면 — 빈자리 하나, 나머지 일곱은 그대로 | `asmLab28` · 2 | 60 |
| `s29` | 전과 후 ④ — 한 JSP에 섹션이 나열되어 있다 | 코드 쌍 · 2 | 90 |
| `s30` | c:catch 가 하는 것과 못 하는 것 | build 3 · 4 | 50 |
| `s31` | 빨리 죽을지 버틸지를 가르는 기준은? | 퀴즈 `q-failfast` + build · 2 | 45 |
| `s32` | 내일 할 것 ④ — 없어도 되는 섹션만 감싼다 | build 4 · 4 | 60 |
| `s33` | 반경 5 · 프로세스 경계 — 죽는 것보다 느린 것이 위험합니다 | `diaPool` · 5 | 100 |
| `s34` | 느린 섹션 하나가 페이지 전체를 기다리게 합니다 | `asmLab34` · 2 | 70 |
| `s35` | 전과 후 ⑤ — 타임아웃 없는 호출 | 코드 쌍 · 2 | 60 |
| `s36` | 빈자리에 놓을 수 있는 넷, 그리고 얼마나 오래된 것까지 괜찮은가 | build 5 · 5 | 55 |
| `s37` | 폴백으로 직전 값을 골랐을 때 | 퀴즈 `q-fallback` + build · 2 | 45 |
| `s38` | 내일 할 것 ⑤ — 타임아웃 두 값, 폴백 대상은 묻는다 | build 3 · 3 | 30 |
| `s39` | 반경 6 · 요구사항 — 기획서에는 정상 경로만 있습니다 | 막 표지 · 1 | 30 |
| `s40` | 다섯 줄을 다시 읽으면, 빈자리가 다섯입니다 | `diaSpecGap` · 6 | 100 |
| `s41` | 세 군데에서 놓칩니다 — 그래서 볼 수 있는 사람은 개발자뿐입니다 | build 4 · 5 | 50 |
| `s42` | 개발자가 기획에게 물어야 할 열두 가지, 네 축 | build 4 · 5 | 50 |
| `s43` | 우리 화면에서 먼저 물을 넷 — 그리고 여섯 번째가 급소입니다 | build 5 · 6 | 90 |
| `s44` | 묻는 태도 — "이렇게 하려는데 맞습니까" | build 3 · 4 | 45 |
| `s45` | 전과 후 ⑥ — 정상 경로만 있는 요건 | 문장 쌍 · 2 | 60 |
| `s46` | 이번 사건의 문장을 지금 만들어 봅시다 | `wordLab46` · 4 | 80 |
| `s47` | 요건 문장이 그대로 테스트 이름이 됩니다 | 코드 · 1 | 40 |
| `s48` | 장애 회고의 산출물은 코드 수정이 아니라 요건 문장입니다 | build 2 · 3 | 40 |
| `s49` | 기본값을 제안하는 말투가 강력한 이유는? | 퀴즈 `q-wording` + build · 2 | 45 |
| `s50` | 내일 할 것 ⑥ — SR 접수 때 네 질문, 답은 요건 문장으로 | build 3 · 3 | 30 |
| `s51` | 다시 그 스택트레이스로 — 반경마다 막은 것과 남긴 구멍 | `diaRadiusRecap` · 6 | 65 |
| `s52` | 방어는 어디에서 멈춥니까? | 퀴즈 `q-recap` + build · 2 | 45 |
| `s53` | 내일 할 것 여섯 줄, 그리고 더 읽을 것 | build 6 · 7 | 40 |

막별 합계: 0막 240 · 1막 480 · 2막 240 · 3막 180 · 4막 810 · 5막 360 · 6막 660 · 7막 150 = **3120초**.

## 슬라이드 대장 — 부록 13장

| id | 제목 | 자산 · 비트 | 초 |
|---|---|---|---|
| `a00` | 부록 — 질문이 나올 때만 펼칩니다 | 1 | 30 |
| `a01` | 그런 값을 애초에 가질 수 없게 — 생성자에서 강제하기 | 코드 (원본 1537줄) · 2 | 80 |
| `a02` | 예산에서 거꾸로 나눈 타임아웃 | `diaBudget` · 5 | 80 |
| `a03` | 회로 차단기와 재시도 — 방어 수단이 새 실패를 만듭니다 | build 3 · 4 | 60 |
| `a04` | 격벽 — 섹션마다 자기 몫의 자원 | build 2 · 3 | 45 |
| `a05` | 열두 질문 · 데이터와 연동 | build 6 · 7 | 60 |
| `a06` | 열두 질문 · 행위와 한계 | build 6 · 7 | 60 |
| `a07` | 완료 정의 한 줄과 설계 리뷰의 고정 질문 | build 2 · 3 | 60 |
| `a08` | 자바·스프링 대응표 | 표 · 1 | 60 |
| `a09` | 응답 버퍼와 오류 페이지 — 버퍼를 키워도 커밋은 사라지지 않습니다 | build 3 · 4 | 60 |
| `a10` | 잡은 실패를 한 번에 남기는 자리 — 인터셉터 | 코드 (원본 4215줄 축약) · 1 | 70 |
| `a11` | 남은 퀴즈 ① — 1·2·3·5·6·7장 | `wireQuizBank('a11')` (`q-unknown` `q-silent` `q-invariant` `q-assembly` `q-swallow`) · 5 | 90 |
| `a12` | 남은 퀴즈 ② — 9·11·12·14장 | `wireQuizBank('a12')` (`q-slowdown` `q-specgap` `q-questions` `q-process`) · 4 | 90 |

---

## Task 1: 검사기 확장 셋 — `data-frames` · 컨트롤러 마운트 · 본편 금지어

**Files:**
- Modify: `tools/check_slides.py` (146–171 정규식, 198–213 `_max_at`, 215–231 `_wiredia_step_counts`, 246–277 `check_dia_frames`, 360 `CHECKS`)
- Modify: `tools/test_check_slides.py` (273–279 `test_every_check_function_is_wired_into_the_gate`)
- Create: `tools/testdata/deck_frames_declared.html`, `tools/testdata/deck_frames_declared_mismatch.html`, `tools/testdata/deck_frames_undeclared_call.html`, `tools/testdata/deck_demo_wrong_slide.html`, `tools/testdata/deck_banned_word.html`

**Interfaces:**
- Consumes: 기존 `read_deck`, `_slide_spans`, `DIA_FIG`, `CHECKS`
- Produces: `DATA_FRAMES` 정규식, `_max_at(segment)`가 `data-frames`를 우선하는 동작, `_wiredia_step_counts`가 배열 리터럴이 아닌 호출에 `None`을 돌려주는 동작, `REGISTER_MOUNT`·`ASSET_VAR`가 `wireEl|wireAssembly|wireJudge|wireWord`를 알아보는 동작, `BANNED_MAIN` 상수, `check_banned_words(deck)`. 뒤의 모든 태스크가 `python3 tools/check_slides.py defensive_programming_slides.html`을 관문으로 쓴다

- [ ] **Step 1: 픽스처 다섯을 만든다**

`tools/testdata/deck_frames_declared.html` — 실행 시 생성되는 도해. `data-at`이 마크업에 없고 `data-frames="6"`을 선언한다. `wireDia` 호출은 배열 리터럴이 아니다.

```html
<!DOCTYPE html><html><body>
<!-- ==== SLIDES ==== -->
<section class="slide" id="s00"><h2>a</h2>
  <figure class="dia" id="diaGen" data-frames="6"><svg><g id="bands"></g></svg></figure>
</section>
<!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">{"s00":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"]}</script>
<script>
registerBeats('s00', wireDia('diaGen', radiusSteps()));
</script>
</body></html>
```

`tools/testdata/deck_frames_declared_mismatch.html` — 같은 것에 `wireDia`를 배열 리터럴 5단계로 쓴다. 선언 6 ≠ 단계 5.

```html
<!DOCTYPE html><html><body>
<!-- ==== SLIDES ==== -->
<section class="slide" id="s00"><h2>a</h2>
  <figure class="dia" id="diaGen" data-frames="6"><svg><g></g></svg></figure>
</section>
<!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">{"s00":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"]}</script>
<script>
registerBeats('s00', wireDia('diaGen', [{c:'1'},{c:'2'},{c:'3'},{c:'4'},{c:'5'}]));
</script>
</body></html>
```

`tools/testdata/deck_frames_undeclared_call.html` — `data-frames`도 없고 배열 리터럴도 아니다. 단계 수를 셀 수 없다.

```html
<!DOCTYPE html><html><body>
<!-- ==== SLIDES ==== -->
<section class="slide" id="s00"><h2>a</h2>
  <figure class="dia" id="diaGen"><svg><g data-at="0"></g></svg></figure>
</section>
<!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">{"s00":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"]}</script>
<script>
registerBeats('s00', wireDia('diaGen', radiusSteps()));
</script>
</body></html>
```

`tools/testdata/deck_demo_wrong_slide.html` — 데모 마운트가 `s00`에 있는데 `s01`에 등록한다.

```html
<!DOCTYPE html><html><body>
<!-- ==== SLIDES ==== -->
<section class="slide" id="s00"><h2>a</h2><div class="demo" id="asmLab00"></div></section>
<section class="slide" id="s01"><h2>b</h2></section>
<!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">{"s00":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"],"s01":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"]}</script>
<script>
registerBeats('s01', wireAssembly('asmLab00', {beats:[{}]}));
</script>
</body></html>
```

`tools/testdata/deck_banned_word.html` — 본편 슬라이드 텍스트에 "격벽", 본편 대본에 "회로 차단기", 부록에 "불변식". 주석 안의 "멱등"은 잡히면 안 된다.

```html
<!DOCTYPE html><html><body>
<!-- ==== SLIDES ==== -->
<section class="slide" id="s00"><h2>격벽을 세웁니다</h2><!-- 멱등 --></section>
<section class="slide" id="s01"><h2>b</h2></section>
<section class="slide appendix" id="a00"><h2>불변식</h2></section>
<!-- ==== /SLIDES ==== -->
<script type="application/json" id="deck-script">{"s00":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"],"s01":["회로 차단기를 켭니다 가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마"],"a00":["가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하가나다라마바사아자차카타파하"]}</script>
</body></html>
```

- [ ] **Step 2: 실패하는 테스트를 쓴다**

`tools/test_check_slides.py` 끝에 추가:

```python
# --- Task 1 · 실행 시 생성되는 도해의 프레임 선언 ---------------------------------

def test_declared_frames_satisfy_the_frame_check_without_data_at():
    """paintRadiusDia 처럼 실행 시 SVG 를 그리는 도해는 마크업에 data-at 이 없다.
    figure 의 data-frames 가 그 수를 대신 선언하고, 배열 리터럴이 아닌 wireDia 호출은
    단계 수를 셀 수 없으므로 선언만 있으면 통과한다. 실제 프레임 수와 선언이 같은지는
    브라우저 테스트가 잰다."""
    assert cs.check_dia_frames(deck('deck_frames_declared.html')) == []


def test_declared_frames_are_compared_with_a_literal_step_array():
    problems = cs.check_dia_frames(deck('deck_frames_declared_mismatch.html'))
    assert len(problems) == 1
    assert '6' in problems[0] and '5' in problems[0]


def test_uncountable_wiredia_call_without_declaration_is_reported():
    problems = cs.check_dia_frames(deck('deck_frames_undeclared_call.html'))
    assert len(problems) == 1
    assert 'data-frames' in problems[0]


def test_max_at_prefers_the_declaration():
    assert cs._max_at('<figure class="dia" id="x" data-frames="6"><g data-at="0"></g></figure>') == 5
    assert cs._max_at('<g data-at="0,2"></g><g data-at="1-4"></g>') == 4


# --- Task 1 · 컨트롤러 넷의 마운트가 등록된 장에 있는가 -------------------------

def test_demo_controller_registered_on_the_wrong_slide_is_reported():
    problems = cs.check_dia_frames(deck('deck_demo_wrong_slide.html'))
    assert len(problems) == 1
    assert 'asmLab00' in problems[0] and 's01' in problems[0]


def test_mount_bindings_know_the_four_demo_controllers():
    html = ("registerBeats('s07', wireEl('elLab07'));"
            "registerBeats('s21', wireAssembly('asmLab21', {beats:[{}]}));"
            "registerBeats('s25', wireJudge('judgeLab25'));"
            "registerBeats('s46', wireWord('wordLab46'));")
    assert cs._mount_bindings(html) == [
        ('s07', 'elLab07'), ('s21', 'asmLab21'), ('s25', 'judgeLab25'), ('s46', 'wordLab46')]


# --- Task 1 · 본편 금지어 ------------------------------------------------------

def test_banned_words_in_main_slides_and_script_are_reported_but_not_in_appendix():
    problems = cs.check_banned_words(deck('deck_banned_word.html'))
    assert sorted(problems) == sorted([
        's00: 본편에 부록 용어 "격벽" — 풀어 쓰거나 부록으로 보내라',
        's01: 본편에 부록 용어 "회로 차단기" — 풀어 쓰거나 부록으로 보내라',
    ])


def test_banned_word_list_is_the_one_the_spec_fixed():
    assert cs.BANNED_MAIN == ['불변식', '사전조건', '사후조건', '격벽', '회로 차단기', '멱등',
                              '백오프', '지터', '값 타입', '검사 예외', '비검사 예외', '리플렉션']


def test_ok_fixture_has_no_banned_words():
    assert cs.check_banned_words(deck('deck_ok.html')) == []
```

그리고 273–279 의 `test_every_check_function_is_wired_into_the_gate` 목록 끝에 `'check_banned_words'`를 더한다:

```python
    assert [c.__name__ for c in cs.CHECKS] == [
        'check_script_present', 'check_slide_seconds', 'check_total',
        'check_dia_frames', 'check_no_external', 'check_script_terminator',
        'check_font_floor', 'check_banned_words',
    ], 'CHECKS 목록이 바뀌었다 — 규칙을 빼거나 더했다면 이 줄도 같이 고쳐라'
```

- [ ] **Step 3: 실패를 확인한다**

Run: `python3 -m pytest tools/test_check_slides.py -v -k "declared or uncountable or max_at or controller or banned or wired"`
Expected: FAIL. `check_banned_words` 없음, `_mount_bindings`가 네 컨트롤러를 못 잡음, `deck_frames_declared`가 "SVG 는 있는데 wireDia 호출이 없다"로 실패, 목록 테스트가 `check_banned_words` 부재로 실패.

- [ ] **Step 4: 정규식과 `_max_at`을 고친다**

`tools/check_slides.py` 150 의 `WIRE_DIA`와 162–167 의 두 정규식을 바꾸고 `DATA_FRAMES`를 더한다:

```python
# 배열 리터럴이 아닌 호출(wireDia('diaRadiusRecap', radiusSteps()))도 잡는다. 단계 수는
# 그때 셀 수 없으므로 None 이 되고, figure 의 data-frames 선언이 그 자리를 대신한다.
WIRE_DIA = re.compile(r'''wireDia\(\s*['"](\w+)['"]\s*,\s*''')
# 실행 시 SVG 를 그리는 도해는 마크업에 data-at 이 없다. figure 가 프레임 수를 선언한다.
# 속성은 id 뒤에 와야 한다 — DIA_FIG 의 segment 가 id 다음부터 시작하기 때문이다.
DATA_FRAMES = re.compile(r'''\bdata-frames\s*=\s*["'](\d+)["']''')

# 컨트롤러는 다섯 갈래다. 도해(wireDia)·시퀀스(createSequence)에 이 덱의 데모 넷
# (wireEl·wireAssembly·wireJudge·wireWord)이 더해졌다. 전부 첫 인자가 마운트 id 다.
CONTROLLERS = r'(?:wireDia|createSequence|wireEl|wireAssembly|wireJudge|wireWord)'
REGISTER_MOUNT = re.compile(
    r'''registerBeats\(\s*['"]([^'"]+)['"]\s*,\s*''' + CONTROLLERS + r'''\(\s*['"](\w+)['"]''')
ASSET_VAR = re.compile(
    r'''\b(?:const|let|var)\s+(\w+)\s*=\s*''' + CONTROLLERS + r'''\(\s*['"](\w+)['"]''')
```

`_max_at`(198줄) 머리에 선언 우선 분기를 넣는다:

```python
def _max_at(segment):
    """data-at 이 가리키는 최대 프레임 인덱스. '3+' 나 '1-4' 같은 표기를 푼다.
    figure 가 data-frames 를 선언했으면 그 값을 믿는다 — 실행 시 그려지는 그림이다."""
    m = DATA_FRAMES.search(segment)
    if m:
        return int(m.group(1)) - 1
    top = -1
    ...  # 이하 그대로
```

`_wiredia_step_counts`(215줄)는 다음 문자가 `[`일 때만 센다:

```python
def _wiredia_step_counts(html):
    """wireDia(id, [ {c:...}, ... ]) 의 단계 수를 id 별로 센다.
    배열 리터럴이 아니면(함수 호출·변수) 셀 수 없으므로 None 을 둔다."""
    counts = {}
    for m in WIRE_DIA.finditer(html):
        i = m.end()
        if i >= len(html) or html[i] != '[':
            counts[m.group(1)] = None
            continue
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
```

`check_dia_frames`(246줄)의 첫 고리를 바꾼다:

```python
    for fid, segment in DIA_FIG.findall(deck.html):
        frames = _max_at(segment) + 1
        declared = DATA_FRAMES.search(segment) is not None
        if fid not in counts:
            problems.append('%s: SVG 는 있는데 wireDia 호출이 없다' % fid)
        elif counts[fid] is None:
            if not declared:
                problems.append('%s: wireDia 단계 수를 셀 수 없다 — 배열 리터럴로 쓰거나 '
                                'figure 에 data-frames 를 적어라' % fid)
        elif frames != counts[fid]:
            problems.append('%s: data-at 프레임 %d개 ≠ wireDia 단계 %d개'
                            % (fid, frames, counts[fid]))
```

마지막 고리의 오류 메시지가 `counts.get(fid, 1)`을 `%d`로 찍는다. `None`이면 죽으므로 `(counts.get(fid) or 1)`로 바꾼다.

- [ ] **Step 5: 금지어 검사를 구현한다**

`check_font_floor` 뒤, `CHECKS` 앞에 추가:

```python
# 설계 7절 「용어 규칙」. 청중이 방어적 프로그래밍을 몰라서 못 하는 개발자라 본편에서
# 쓰는 개념어를 다섯(경계·격리·빨리 죽기와 버티기·폴백·요건 문장)으로 제한했다.
# 아래 열둘은 부록으로 내린 개념의 이름이고 본편 슬라이드·대본 어디에도 나오면 안 된다.
# 설계 문서의 목록과 한 글자씩 같아야 한다.
BANNED_MAIN = ['불변식', '사전조건', '사후조건', '격벽', '회로 차단기', '멱등',
               '백오프', '지터', '값 타입', '검사 예외', '비검사 예외', '리플렉션']
HTML_COMMENT = re.compile(r'<!--.*?-->', re.S)
ANY_TAG = re.compile(r'<[^>]+>')


def _banned_pattern(word):
    # '비검사 예외'가 '검사 예외'로 한 번 더 잡히지 않게 한다.
    if word == '검사 예외':
        return re.compile(r'(?<!비)검사 예외')
    return re.compile(re.escape(word))


def check_banned_words(deck):
    """본편 슬라이드 텍스트와 본편 대본의 부록 용어. 주석은 세지 않는다 — 다음 사람에게
    남기는 설명에는 그 이름이 필요하다."""
    problems = []
    spans = _slide_spans(deck.html)
    for sid in deck.main_slides:
        span = spans.get(sid)
        text = ''
        if span:
            text = ANY_TAG.sub(' ', HTML_COMMENT.sub(' ', deck.html[span[0]:span[1]]))
        text += ' ' + ' '.join(deck.script.get(sid, []))
        for word in BANNED_MAIN:
            if _banned_pattern(word).search(text):
                problems.append('%s: 본편에 부록 용어 "%s" — 풀어 쓰거나 부록으로 보내라'
                                % (sid, word))
    return problems


CHECKS = [check_script_present, check_slide_seconds, check_total,
          check_dia_frames, check_no_external, check_script_terminator,
          check_font_floor, check_banned_words]
```

- [ ] **Step 6: 전부 통과시킨다**

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: 38 + 9 = 47 PASS. 파일럿 덱 `oauth2_slides.html`도 여전히 통과한다 — `python3 tools/check_slides.py oauth2_slides.html` → `✓ 통과`. (파일럿에는 금지어가 없고 실행 시 생성 도해도 없다.)

- [ ] **Step 7: 커밋**

```bash
git add tools/check_slides.py tools/test_check_slides.py tools/testdata/deck_frames_declared.html tools/testdata/deck_frames_declared_mismatch.html tools/testdata/deck_frames_undeclared_call.html tools/testdata/deck_demo_wrong_slide.html tools/testdata/deck_banned_word.html
git commit -m "check_slides: data-frames 선언 · 데모 컨트롤러 마운트 · 본편 금지어"
```

---

## Task 2: 덱 골격 — 파일럿 엔진 복사 · 빈 슬라이드 67장 · 무대 CSS 뼈대

**설계 12절의 확인 지점 1.** 이 태스크가 끝나면 자산 없이도 덱이 굴러가야 한다.

**Files:**
- Create: `defensive_programming_slides.html`
- Create: `tools/build_defprog_skeleton.py` (한 번 쓰고 버리는 생성기. 커밋은 하되 이후 태스크는 덱 파일을 직접 고친다)

**Interfaces:**
- Consumes: `oauth2_slides.html`의 네 엔진 블록 (8–137, 748–760, 2094–2102, 2177–2570)
- Produces: 마커 일곱 개가 제자리에 있는 덱 파일. `registerAssets()`·`wireDemos()` 두 빈 함수를 `ASSET:JS`에 둔다 (`DECK:CORE:JS`의 `init()`이 `typeof`로 확인하고 부른다). 67개 `<section class="slide" id=…>`, 부록 13장은 `class="slide appendix"`. 대본 블록에는 장마다 자리 표시 문단 하나

- [ ] **Step 1: 생성기를 쓴다**

`tools/build_defprog_skeleton.py`:

```python
#!/usr/bin/env python3
"""defensive_programming_slides.html 골격 생성기. Task 2 에서 한 번 돌린다.

파일럿 oauth2_slides.html 에서 엔진 네 블록을 바이트 그대로 잘라 오고, 슬라이드 대장의
id 와 제목으로 빈 장 67개를 만든다. 이후 태스크는 만들어진 덱 파일을 직접 고친다 —
이 생성기를 다시 돌리면 그 작업이 전부 지워진다."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(ROOT, 'oauth2_slides.html')
OUT = os.path.join(ROOT, 'defensive_programming_slides.html')

CORE_CSS = re.compile(r'/\* ==== DECK:CORE:CSS ==== \*/.*?/\* ==== /DECK:CORE:CSS ==== \*/', re.S)
CORE_JS = re.compile(r'/\* ==== DECK:CORE:JS ==== \*/.*?/\* ==== /DECK:CORE:JS ==== \*/', re.S)
CHROME = re.compile(r'<!-- ==== DECK:CHROME ==== -->.*?<!-- ==== /DECK:CHROME ==== -->', re.S)

MAIN = [
 ('s00', '방어적 프로그래밍 — 하나가 죽었을 때 전체가 죽지 않게'),
 ('s01', '지난 9월 7일, 메인페이지가 통째로 오류를 냈습니다'),
 ('s02', '이 열 줄 안에 범인이 있을까요. 없습니다'),
 ('s03', '방어적 프로그래밍은 예외를 없애는 기술이 아닙니다'),
 ('s04', '오늘의 약속 두 문장, 그리고 여섯 반경'),
 ('s05', '반경 1 · 한 줄 — 터진 자리와 잘못된 자리는 다른 곳입니다'),
 ('s06', '스택트레이스는 호출이 지나온 길이지 값이 지나온 길이 아닙니다'),
 ('s07', '같은 식에 다섯 값 — null 은 조용하고 문자열은 시끄럽습니다'),
 ('s08', '조용한 쪽이 더 위험합니다'),
 ('s09', '전과 후 ① — 잡고 로그만 남기는 catch'),
 ('s10', '예외에 담을 세 조각, 담지 말아야 할 것 하나'),
 ('s11', '이 스택트레이스만 보고 확실하게 말할 수 있는 것은?'),
 ('s12', '내일 할 것 ① — catch 뒤에 로그만 있는 자리'),
 ('s13', '반경 2 · 한 함수 — 검증을 미룬 만큼 늘어나는 거리'),
 ('s14', '전과 후 ② — 곳곳의 null 검사'),
 ('s15', '원인이 셋 중 무엇이든, 선을 그을 자리는?'),
 ('s16', '내일 할 것 ② — 외부 응답이 우리 객체가 되는 자리'),
 ('s17', '반경 3 · 한 객체 — 무엇이든 담기는 모델이 치르는 대가'),
 ('s18', '전과 후 ③ — Map&lt;String, Object&gt;'),
 ('s19', '내일 할 것 ③ — 새 화면 모델은 클래스로'),
 ('s20', '반경 4 · 한 모듈 — 섹션 하나가 죽어서 메인이 죽었습니다'),
 ('s21', '여덟 섹션, 하나에 예외를 넣으면'),
 ('s22', '화면은 여덟 칸인데 코드는 한 흐름입니다 — 141번째 c:set'),
 ('s23', '응답이 이미 나간 뒤에는 되돌릴 것이 없습니다'),
 ('s24', '같은 예외, 네 층 — 대안이 있는 층만 삼킬 수 있습니다'),
 ('s25', '빨리 죽을 자리와 버틸 자리 — 여덟 장을 직접 골라 봅시다'),
 ('s26', '기준은 하나입니다'),
 ('s27', '오늘 사건은 두 문장을 동시에 틀렸습니다'),
 ('s28', '격리를 켜면 — 빈자리 하나, 나머지 일곱은 그대로'),
 ('s29', '전과 후 ④ — 한 JSP에 섹션이 나열되어 있다'),
 ('s30', 'c:catch 가 하는 것과 못 하는 것'),
 ('s31', '빨리 죽을지 버틸지를 가르는 기준은?'),
 ('s32', '내일 할 것 ④ — 없어도 되는 섹션만 감싼다'),
 ('s33', '반경 5 · 프로세스 경계 — 죽는 것보다 느린 것이 위험합니다'),
 ('s34', '느린 섹션 하나가 페이지 전체를 기다리게 합니다'),
 ('s35', '전과 후 ⑤ — 타임아웃 없는 호출'),
 ('s36', '빈자리에 놓을 수 있는 넷, 그리고 얼마나 오래된 것까지 괜찮은가'),
 ('s37', '폴백으로 직전 값을 골랐을 때'),
 ('s38', '내일 할 것 ⑤ — 타임아웃 두 값, 폴백 대상은 묻는다'),
 ('s39', '반경 6 · 요구사항 — 기획서에는 정상 경로만 있습니다'),
 ('s40', '다섯 줄을 다시 읽으면, 빈자리가 다섯입니다'),
 ('s41', '세 군데에서 놓칩니다 — 그래서 볼 수 있는 사람은 개발자뿐입니다'),
 ('s42', '개발자가 기획에게 물어야 할 열두 가지, 네 축'),
 ('s43', '우리 화면에서 먼저 물을 넷 — 그리고 여섯 번째가 급소입니다'),
 ('s44', '묻는 태도 — "이렇게 하려는데 맞습니까"'),
 ('s45', '전과 후 ⑥ — 정상 경로만 있는 요건'),
 ('s46', '이번 사건의 문장을 지금 만들어 봅시다'),
 ('s47', '요건 문장이 그대로 테스트 이름이 됩니다'),
 ('s48', '장애 회고의 산출물은 코드 수정이 아니라 요건 문장입니다'),
 ('s49', '기본값을 제안하는 말투가 강력한 이유는?'),
 ('s50', '내일 할 것 ⑥ — SR 접수 때 네 질문, 답은 요건 문장으로'),
 ('s51', '다시 그 스택트레이스로 — 반경마다 막은 것과 남긴 구멍'),
 ('s52', '방어는 어디에서 멈춥니까?'),
 ('s53', '내일 할 것 여섯 줄, 그리고 더 읽을 것'),
]
APPENDIX = [
 ('a00', '부록 — 질문이 나올 때만 펼칩니다'),
 ('a01', '그런 값을 애초에 가질 수 없게 — 생성자에서 강제하기'),
 ('a02', '예산에서 거꾸로 나눈 타임아웃'),
 ('a03', '회로 차단기와 재시도 — 방어 수단이 새 실패를 만듭니다'),
 ('a04', '격벽 — 섹션마다 자기 몫의 자원'),
 ('a05', '열두 질문 · 데이터와 연동'),
 ('a06', '열두 질문 · 행위와 한계'),
 ('a07', '완료 정의 한 줄과 설계 리뷰의 고정 질문'),
 ('a08', '자바·스프링 대응표'),
 ('a09', '응답 버퍼와 오류 페이지 — 버퍼를 키워도 커밋은 사라지지 않습니다'),
 ('a10', '잡은 실패를 한 번에 남기는 자리 — 인터셉터'),
 ('a11', '남은 퀴즈 ① — 1·2·3·5·6·7장'),
 ('a12', '남은 퀴즈 ② — 9·11·12·14장'),
]

# s02 만 지금 내용을 갖는다. 비트가 둘 이상인 장이 하나는 있어야 Task 3 의 동작 테스트
# (first_multi_beat_slide)가 골격에서도 돈다. 내용은 대장 그대로라 Task 6 에서 안 바꾼다.
S02 = '''    <ul class="suspects">
      <li class="build" data-beat="1">JSP 9946번째 줄에 버그가 있다? — <b>터진 자리</b>이지 잘못된 자리가 아닙니다</li>
      <li class="build" data-beat="2">API 가 잘못된 값을 줬다? — 이 열 줄 어디에도 API 는 없습니다</li>
      <li class="build" data-beat="3">캐시가 잘못 저장했다? — 캐시도 없습니다. <b>셋 다 추측입니다</b></li>
    </ul>
'''

STAGE_CSS = '''/* ==== DECK:STAGE:CSS ==== */
/* 무대용 명도 대비 상향. 회의실 조명이 밝아도 뒷자리에서 읽히도록. 파일럿과 같은 값. */
:root{ --bg:#04070d; --text-dim:#c3d1e2; --text-mut:#a3b4c9; }

/* 튜토리얼의 section 규칙(margin-bottom)이 절대배치된 .slide 의 높이를 갉아먹는다 */
.slide{margin:0}

/* ---- 활자 하한 ----
   기준: 본문 24px, 코드 20px (1280x720 좌표계). 뒷자리에서 읽히는 최소치다.
   내용을 나르는 요소는 예외 없이 이 선을 지킨다. 예외에도 바닥이 있다 — 줄마다 제
   바닥을 들고 있고, 더 줄이는 것만 막는다.

   ==== 예외 목록 시작 ====
   형식: [셀렉터] 바닥 Npx — 근거. tools/test_deck_behavior.py 의
   EXEMPT['defensive_programming_slides.html'] 과
   test_the_font_floor_exemptions_match_their_css_comment 가 이 목록을 한 글자씩
   대조한다. 한쪽만 고치면 그 테스트가 잡는다.
     [svg, svg *] 바닥 12px — 그림 속 글자. viewBox 좌표를 화면 px 로 환산해서 잰다. 같은 말을 .dia-cap 이 26px 로 다시 싣는다
   ==== 예외 목록 끝 ====
   svg 줄의 근거는 파일럿 DECK:STAGE:CSS 의 「svg 줄의 근거를 따로 적는다」와 같다. */

/* 이후 태스크가 이 아래에 무대 규칙을 더한다: Task 4 도해, Task 5 데모·퀴즈,
   Task 6 막 표지·전과 후·내일 할 것. */
/* ==== /DECK:STAGE:CSS ==== */'''

ASSET_CSS = '''/* ==== ASSET:CSS ← defensive_programming.html ==== */
/* Task 4·5 가 채운다. 출처는 원본 파일과 줄 번호로 적는다. */
/* ==== /ASSET:CSS ==== */'''

ASSET_JS = '''/* ==== ASSET:JS ← defensive_programming.html ==== */
/* Task 4·5 가 채운다. 아래 두 함수는 DECK:CORE:JS 의 init() 이 typeof 로 확인하고
   부르는 접점이다 — registerAssets 는 Deck.go(0) 앞에서, wireDemos 는 뒤에서. */
function registerAssets(){}
function wireDemos(){}
/* ==== /ASSET:JS ==== */'''


def slide(sid, title, appendix):
    cls = 'slide appendix' if appendix else 'slide'
    body = S02 if sid == 's02' else ''
    return '  <section class="%s" id="%s">\n    <h2>%s</h2>\n%s  </section>\n' % (cls, sid, title, body)


def main():
    with open(PILOT, encoding='utf-8') as fh:
        pilot = fh.read()
    core_css = CORE_CSS.search(pilot).group(0)
    core_js = CORE_JS.search(pilot).group(0)
    chrome = CHROME.findall(pilot)
    assert len(chrome) == 2, 'DECK:CHROME 은 두 조각이어야 한다'

    slides = ''.join(slide(s, t, False) for s, t in MAIN)
    slides += '  <!-- ==== 부록 a00~a12 ==== 발표에서는 넘어가는 장이다. class 의 appendix 가\n'
    slides += '       그 표시이고, tools/check_slides.py 의 check_total 이 같은 표시를 보고 52분\n'
    slides += '       합계에서 뺀다. -->\n'
    slides += ''.join(slide(s, t, True) for s, t in APPENDIX)

    # 자리 표시 대본. 검사기는 25초 하한으로 전부 잡는다 — Task 7·8 이 채운다.
    script = {sid: ['(대본 미작성) ' + re.sub(r'<[^>]+>', '', t)] for sid, t in MAIN + APPENDIX}

    html = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>방어적 프로그래밍 — 발표 덱</title>
<style>
%s

%s

%s
</style>
</head>
<body>
%s

<!-- ==== SLIDES ==== -->
%s<!-- ==== /SLIDES ==== -->

%s

<script type="application/json" id="deck-script">
%s
</script>

<script>
%s

%s

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
</script>
</body>
</html>
''' % (core_css, STAGE_CSS, ASSET_CSS, chrome[0], slides, chrome[1],
       json.dumps(script, ensure_ascii=False, indent=1), core_js, ASSET_JS)
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('wrote', OUT, len(MAIN), 'main +', len(APPENDIX), 'appendix')


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 돌린다**

Run: `python3 tools/build_defprog_skeleton.py`
Expected: `wrote … 54 main + 13 appendix`

- [ ] **Step 3: 검사기로 골격을 확인한다**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: `본편 54장(…) + 부록 13장`. 위반은 **전부** `대본 … 하한 25초에 못 미친다`(67건)와 `본편 대본 합계 … 벗어난다`(1건)뿐이다. 그 밖의 위반(마커 없음, 외부 요청, 금지어)이 하나라도 있으면 생성기를 고친다. 금지어 검사는 `a03`·`a04`의 제목에 "회로 차단기"·"격벽"이 있어도 부록이라 잡지 않아야 한다.

- [ ] **Step 4: 브라우저에서 굴려 본다**

`defensive_programming_slides.html`을 브라우저로 연다. 확인할 것 넷: 첫 장이 뜬다. 오른쪽 화살표로 `s02`의 세 줄이 하나씩 열린 뒤 `s03`으로 넘어간다. `A`로 `a00`에 가고 HUD 가 `부록 1 / 13`을 말한다. `O` 개요 그리드에 67칸이 보이고 부록 칸이 점선이다. 콘솔 오류 0.

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming_slides.html tools/build_defprog_skeleton.py
git commit -m "defprog 덱 골격 — 파일럿 엔진 네 블록 복사, 빈 슬라이드 67장"
```

- [ ] **Step 6: 확인 지점 — 사용자에게 보고하고 멈춘다**

Step 3의 검사기 출력 요약과 Step 4의 네 가지 확인 결과를 보고한다. 골격이 틀렸는데 자산을 얹으면 손해가 크다.

---

## Task 3: 테스트를 두 덱에 물린다 — 순회 · 덱별 활자 예외 · 엔진 동일성

**Files:**
- Modify: `tools/test_check_slides.py` (10 `DECK`, 263, 302, 327, 342, 372, 388)
- Modify: `tools/test_deck_behavior.py` (59 `DECK`, 모든 `page.goto(DECK)`, 953–976 `EXEMPT`, 1030–1075, 1076–1118, 1201–1257)

**Interfaces:**
- Consumes: Task 2의 덱 파일
- Produces: `DECK_FILES = ['oauth2_slides.html', 'defensive_programming_slides.html']`, 픽스처 `deck`(절대 경로, 두 덱 순회)·`pilot`(파일럿 절대 경로), `EXEMPT`가 파일 이름을 키로 갖는 dict, `measure_spec(path)`, `SHIPPED`(검사기 전부를 통과해야 하는 덱 목록 — Task 8이 둘째를 더한다), `LATER`(내용이 아직 없어 파일럿에만 묶어 둔 테스트 — Task 8이 푼다)

- [ ] **Step 1: 실패하는 테스트 — 엔진 동일성**

`tools/test_check_slides.py` 끝에 추가:

```python
# --- Task 3 · 두 덱은 엔진을 바이트 단위로 공유한다 ------------------------------

CORE_CSS = re.compile(
    r'/\* ==== DECK:CORE:CSS ==== \*/(.*?)/\* ==== /DECK:CORE:CSS ==== \*/', re.S)


def _engine_blocks(path):
    with open(path, encoding='utf-8') as fh:
        html = fh.read()
    return {
        'DECK:CORE:CSS': CORE_CSS.search(html).group(1),
        'DECK:CORE:JS': CORE_JS.search(html).group(1),
        'DECK:CHROME': CHROME_BLOCK.findall(html),
    }


def test_the_two_decks_share_the_engine_byte_for_byte():
    """설계 10절. build_slides.py 를 뽑는 대신 두 벌을 같게 유지한다. 코어를 고쳐야
    하면 두 덱을 같이 고쳐야 이 테스트가 통과한다 — 한쪽만 고치면 여기서 잡힌다."""
    a = _engine_blocks(os.path.join(ROOT, 'oauth2_slides.html'))
    b = _engine_blocks(os.path.join(ROOT, 'defensive_programming_slides.html'))
    for name in a:
        assert a[name] == b[name], '%s 가 두 덱에서 다르다' % name
```

Run: `python3 -m pytest tools/test_check_slides.py -k engine -v`
Expected: PASS (Task 2 가 바이트 그대로 복사했다). 실패하면 생성기가 아니라 손으로 고친 흔적이 있다는 뜻이다 — 골격을 다시 만든다.

- [ ] **Step 2: 검사기 테스트를 두 덱에 물린다**

`tools/test_check_slides.py` 머리(10줄)를 바꾼다:

```python
import pytest

DECK_FILES = ['oauth2_slides.html', 'defensive_programming_slides.html']
# 검사기 전부를 통과해야 하는 덱. 둘째는 대본이 다 찬 뒤(Task 8)에 들어온다.
SHIPPED = ['oauth2_slides.html']


@pytest.fixture(params=DECK_FILES, ids=[f.split('_')[0] for f in DECK_FILES])
def deck_path(request):
    return os.path.join(ROOT, request.param)
```

그리고 다음 여섯 자리를 고친다.

| 줄 | 전 | 후 |
|---|---|---|
| 257 | `def test_the_shipped_deck_passes_every_check():` | `@pytest.mark.parametrize('name', SHIPPED)` 를 위에 달고 `def test_the_shipped_deck_passes_every_check(name):` |
| 263 | `deck = cs.read_deck(DECK)` | `deck = cs.read_deck(os.path.join(ROOT, name))` |
| 302 | `os.path.join(os.path.dirname(DECK), 'tools', 'test_deck_behavior.py')` | `os.path.join(ROOT, 'tools', 'test_deck_behavior.py')` |
| 318·327 | `def test_the_deck_and_the_checker_share_their_constants():` · `open(DECK,` | `(deck_path):` · `open(deck_path,` |
| 340·342 | `def test_the_deck_does_not_hardcode_the_slide_length_limits_again():` · `open(DECK,` | `(deck_path):` · `open(deck_path,` |
| 366·372 | `def test_the_deck_chrome_lives_inside_its_own_marker():` · `open(DECK,` | `(deck_path):` · `open(deck_path,` |
| 382·388 | `def test_every_id_the_core_js_reaches_for_is_in_the_chrome_block():` · `open(DECK,` | `(deck_path):` · `open(deck_path,` |

Run: `grep -n '\bDECK\b' tools/test_check_slides.py`
Expected: 남는 것은 `DECK_FILES`·`DECK_CONST`·`DECK:` 마커 문자열뿐이다. 단독 `DECK` 0건.

Run: `python3 -m pytest tools/test_check_slides.py -v`
Expected: 전부 PASS. 두 덱 순회 테스트는 `[oauth2]`·`[defensive]` 두 번 돈다.

- [ ] **Step 3: 동작 테스트를 두 덱에 물린다 — 기계적 치환**

다음 스크립트를 한 번 돌린다. `def test_x(page):` 서명에 픽스처를 더하고, 본문의 `page.goto(DECK)`를 그 픽스처로 바꾼다. 파일럿에만 있는 성질(자동재생 시퀀스·JWT 데모)을 보는 일곱 테스트는 `pilot`에 묶고, 내용이 아직 없는 퀴즈 은행 테스트는 `LATER`로 두어 Task 8 이 푼다.

```bash
python3 - <<'EOF'
import re
p = 'tools/test_deck_behavior.py'
s = open(p, encoding='utf-8').read()

PILOT_ONLY = {
    'test_appendix_sequences_do_not_play_by_themselves',
    'test_leaving_an_autoplaying_slide_stops_it',
    'test_entering_an_autoplaying_slide_rewinds_and_starts_it',
    'test_a_stray_right_arrow_during_autoplay_does_not_cost_the_slide',
    'test_backing_into_an_autoplaying_slide_lands_on_the_beat_it_shows',
    'test_leaving_an_autoplaying_slide_backwards_never_shows_a_beat_that_lies',
    'test_the_two_jwt_demos_stay_identical_apart_from_their_button_rows',
}
LATER = {'test_appendix_quiz_bank_shows_exactly_one_question_per_beat'}

def sig(m):
    name = m.group(1)
    fx = 'pilot' if (name in PILOT_ONLY or name in LATER) else 'deck'
    return 'def %s(page, %s):' % (name, fx)
s = re.sub(r'def (test_\w+)\(page\):', sig, s)

out, cur = [], 'deck'
for line in s.splitlines(keepends=True):
    m = re.match(r'def test_\w+\(page, (deck|pilot)\):', line)
    if m:
        cur = m.group(1)
    line = line.replace('page.goto(DECK)', "page.goto('file://' + %s)" % cur)
    out.append(line)
s = ''.join(out)

FIXTURES = '''DECK_FILES = ['oauth2_slides.html', 'defensive_programming_slides.html']
PILOT = os.path.join(ROOT, 'oauth2_slides.html')

# 파일럿에만 있는 성질(자동재생 시퀀스 · JWT 데모 한 쌍)을 보는 테스트는 pilot 을 받고,
# 두 덱이 다 지켜야 하는 엔진 계약은 deck 을 받아 두 번 돈다.
# LATER: 둘째 덱에 아직 그 내용이 없어 pilot 에 묶어 둔 테스트. Task 8 이 deck 으로 바꾼다.
#   - test_appendix_quiz_bank_shows_exactly_one_question_per_beat


@pytest.fixture(params=DECK_FILES, ids=[f.split('_')[0] for f in DECK_FILES])
def deck(request):
    return os.path.join(ROOT, request.param)


@pytest.fixture
def pilot():
    return PILOT'''
old = "DECK = 'file://' + os.path.join(ROOT, 'oauth2_slides.html')"
assert s.count(old) == 1
s = s.replace(old, FIXTURES)
s = s.replace("deck = cs.read_deck(os.path.join(ROOT, 'oauth2_slides.html'))",
              'deck_read = cs.read_deck(deck)')
open(p, 'w', encoding='utf-8').write(s)
print('rewritten')
EOF
```

`test_the_deck_and_the_checker_agree_on_every_slide_time`(1201줄)에서 지역 변수 `deck`이 픽스처 이름과 겹치므로 위 스크립트가 `deck_read`로 바꿨다. 그 함수 본문에 남은 `deck.slides`·`deck.script`를 전부 `deck_read.slides`·`deck_read.script`로 손으로 고친다.

Run: `grep -n 'page.goto(DECK)\|\bDECK\b' tools/test_deck_behavior.py`
Expected: 0건 (`DECK_FILES`·`DECK:` 문자열 제외).

- [ ] **Step 4: 활자 예외 목록을 덱별로 나눈다**

`tools/test_deck_behavior.py` 953–976 의 `EXEMPT = [...]`를 dict 로 감싼다. 기존 열한 줄은 그대로 파일럿의 값이다:

```python
EXEMPT = {
    'oauth2_slides.html': [
        # (기존 열한 줄 그대로)
    ],
    'defensive_programming_slides.html': [
        ('svg, svg *', 12,
         '그림 속 글자. viewBox 좌표를 화면 px 로 환산해서 잰다. 같은 말을 .dia-cap 이 26px 로 다시 싣는다'),
    ],
}
# 덱마다 예외 줄 수. CSS 주석·노트의 "열한 줄" 같은 말과 같이 움직인다.
EXEMPT_ROWS = {'oauth2_slides.html': 11, 'defensive_programming_slides.html': 1}


def exempt_of(path):
    return EXEMPT[os.path.basename(path)]


def measure_spec(path):
    return {'body': FONT_FLOOR, 'mono': FONT_FLOOR_MONO,
            'exempt': [[sel, floor] for sel, floor, _ in exempt_of(path)]}
```

`MEASURE_SPEC = {...}`(1023–1027줄) 상수는 지운다.

`test_the_font_floor_exemptions_match_their_css_comment()`(1030줄)는 `page`가 없으므로 위 스크립트가 손대지 않았다. 손으로 바꾼다:

```python
@pytest.mark.parametrize('name', DECK_FILES)
def test_the_font_floor_exemptions_match_their_css_comment(name):
    """(독스트링 그대로)"""
    with open(os.path.join(ROOT, name), encoding='utf-8') as fh:
        html = fh.read()
    block = EXEMPT_BLOCK.search(html)
    assert block, '%s: DECK:STAGE:CSS 에서 「예외 목록 시작/끝」 블록을 찾지 못했다' % name

    parsed = []
    for line in block.group(1).splitlines():
        m = EXEMPT_LINE.match(line)
        if m:
            parsed.append((m.group(1), int(m.group(2)), m.group(3)))

    assert parsed == EXEMPT[name], (
        '%s: CSS 주석의 예외 목록과 EXEMPT 가 다르다.\n'
        'CSS  (%d줄): %s\nEXEMPT(%d줄): %s' % (
            name, len(parsed), [p[:2] for p in parsed],
            len(EXEMPT[name]), [e[:2] for e in EXEMPT[name]]))
    assert len(EXEMPT[name]) == EXEMPT_ROWS[name], \
        '%s: 예외가 %d줄이다 — CSS 주석·노트의 줄 수도 같이 고쳐라' % (name, len(EXEMPT[name]))
```

`test_every_exempted_selector_is_measured_against_a_real_floor(page, deck)`(1076줄) 본문의 두 `EXEMPT`를 `exempt_of(deck)`으로, `test_every_visible_text_is_at_or_above_the_font_floor(page, deck)`(1108줄)의 `MEASURE_SPEC`을 `measure_spec(deck)`으로 바꾼다.

- [ ] **Step 5: 브라우저 테스트를 돌린다**

Run: `python3 -m pytest tools/test_deck_behavior.py -v`
Expected: 파일럿 쪽 `[oauth2]`는 전부 PASS. 둘째 덱 `[defensive]`도 전부 PASS 여야 한다 — 골격에는 비트 둘 이상인 장(`s02`), 부록, 대본(자리 표시)이 있어 엔진 계약 테스트의 전제가 성립한다. 실패하면 골격이 엔진 계약을 깬 것이므로 여기서 고친다. `test_no_slide_overflows_the_720px_stage[defensive]`는 제목만 있는 장이라 통과한다.

Run: `python3 -m pytest tools/ -q`
Expected: 실패 0. (`tools/test_defensive_*.py`는 튜토리얼 쪽 테스트라 이 작업과 무관하게 그대로 통과한다.)

- [ ] **Step 6: 커밋**

```bash
git add tools/test_check_slides.py tools/test_deck_behavior.py
git commit -m "덱 테스트를 두 덱에 물린다 — 순회 픽스처, 덱별 활자 예외, 엔진 네 블록 동일성"
```

---

## Task 4: 자산 이식 ① — CSS · 도해 열 장 · 반경 지도 두 벌

**Files:**
- Modify: `defensive_programming_slides.html` (`ASSET:CSS`, `DECK:STAGE:CSS`, `SLIDES`의 s04·s06·s08·s13·s17·s23·s24·s33·s40·s51·a02, `ASSET:JS`)
- Modify: `tools/test_deck_behavior.py` (`data-frames` 실측 테스트 추가)

**Interfaces:**
- Consumes: Task 1의 `data-frames` 규칙, Task 2의 `registerAssets()` 접점, 파일럿의 `diaAt`·`wireDia`(덱판)
- Produces: `figure.dia` 열한 개(`diaRadius`가 둘), `radiusSteps()`, `registerAssets()` 안의 `registerBeats` 아홉 줄, `s04`의 고정 지도

- [ ] **Step 1: 실패하는 테스트 — 선언한 프레임 수가 실제와 같은가**

`tools/test_deck_behavior.py` 끝에 추가:

```python
# --- Task 4 · 실행 시 생성되는 도해의 프레임 선언은 실측과 같아야 한다 ---------------

def test_declared_frame_counts_match_what_gets_drawn(page, deck):
    """figure[data-frames] 는 검사기가 셀 수 없는 프레임 수를 대신 선언한다. 선언이
    실제와 갈리면 검사기는 통과라고 하는데 → 는 빈 프레임을 넘기거나 마지막 프레임을
    못 간다. 그려진 뒤의 [data-at] 최댓값을 재서 선언과 대조한다."""
    page.goto('file://' + deck)
    got = page.evaluate('''() => Array.from(document.querySelectorAll('figure.dia[data-frames]'))
      .map(f => {
        let top = -1;
        f.querySelectorAll('[data-at]').forEach(el => {
          String(el.dataset.at).split(',').forEach(p => {
            p = p.trim(); if (!p) return;
            if (p.endsWith('+')) p = p.slice(0, -1);
            if (p.includes('-')) p = p.split('-').pop();
            const n = parseInt(p, 10); if (!isNaN(n)) top = Math.max(top, n);
          });
        });
        return [f.id, parseInt(f.dataset.frames, 10), top + 1];
      })''')
    if os.path.basename(deck) == 'defensive_programming_slides.html' and not got:
        pytest.fail(MUST_EXIST % 'data-frames 를 선언한 도해(diaRadiusIntro·diaRadiusRecap)')
    bad = ['%s: 선언 %d ≠ 실측 %d' % (fid, dec, real) for fid, dec, real in got if dec != real]
    assert bad == [], '\n'.join(bad)
```

Run: `python3 -m pytest tools/test_deck_behavior.py -k declared_frame -v`
Expected: `[oauth2]` PASS (선언한 도해가 없어 빈 목록), `[defensive]` FAIL — MUST_EXIST.

- [ ] **Step 2: CSS를 옮긴다**

`ASSET:CSS` 블록을 채운다. 원본 `defensive_programming.html`에서 다음 범위를 이 순서로 복사하고, 범위마다 `/* 출처: defensive_programming.html NNN-MMM */` 한 줄을 앞에 둔다.

1. 15–44 `:root` — **`--bg`·`--text-dim`·`--text-mut` 세 줄은 지운다.** `DECK:STAGE:CSS`가 무대용 값을 정하는데 이 블록이 뒤에 오므로 남기면 덮어쓴다.
2. 176–193 `.quiz` 일가
3. 266–271 `.trace`
4. 284–288 `.gap`
5. 305–309 `.demo`
6. 321–331 `.picker` `.pick` `.verdict`
7. 336–338 `.kv`
8. 348–360 `.tog`
9. 376–398 `.asm-*` `.ctl-*`
10. 399–420 `.jcard` 일가
11. 452–465 `.wgrid` `.wfield` `.reqout` (`@media` 한 줄은 뺀다)
12. 531–662 도해 `.dia` 일가

블록 머리에 파일럿 알려진 이슈 8번의 결론을 적는다: 이 블록은 원본의 사본이 아니라 덱이 쓰는 부품 목록이고, 죽은 규칙은 Task 9 에서 지운다.

- [ ] **Step 3: 무대 규칙을 더한다 — 도해**

`DECK:STAGE:CSS`의 "이후 태스크가 이 아래에" 주석 자리에:

```css
/* ---- 도해 (Task 4) ----
   원본 .dia 는 본문 폭 반응형이고 캡션이 13px 이다. 무대에서는 그림을 슬라이드 폭에
   꽉 채우고 캡션을 하한 위로 올린다. 재생 버튼·좌우 밀기 안내·꼬리표는 발표자가
   말로 하므로 없앤다 — 보이지 않는 요소는 활자 측정에서도 빠진다. */
.slide .dia{margin:0;max-width:none}
.slide .dia-top{margin-bottom:6px}
.slide .dia-btn,.slide .dia-hint,.slide .dia-tag{display:none}
.slide .dia-scroll{overflow:visible}
.slide .dia-scroll svg{width:100%;min-width:0;height:auto;max-height:440px}
.slide .dia-cap{font-size:26px;line-height:1.5;min-height:80px;margin-top:10px}
.slide .dia-dot{width:14px;height:14px}
```

- [ ] **Step 4: 도해 열 장의 마크업을 놓는다**

원본에서 `<figure class="dia" id="…"> … </figure>`를 통째로 잘라 해당 슬라이드의 `<h2>` 아래에 넣는다. 잘라 오면서 `figure` 안의 `<button class="dia-btn">`(재생 버튼)은 지운다. 아홉 장의 자리는 자산 좌표 표대로: `diaBlame`→s06, `diaSilent`→s08, `diaBoundary`→s13, `diaShape`→s17, `diaCommit`→s23, `diaLayers`→s24, `diaPool`→s33, `diaSpecGap`→s40, `diaBudget`→a02.

`diaRadius`(3696줄)는 두 벌을 만든다. 원본 figure 를 복사해 `id`를 `diaRadiusIntro`(s04)·`diaRadiusRecap`(s51)으로 바꾸고, **`id` 바로 뒤에** `data-frames="6"`을 적고, 안쪽 `<g id="radiusBands">`의 id 를 각각 `radiusBandsIntro`·`radiusBandsRecap`으로 바꾼다:

```html
<figure class="dia" id="diaRadiusRecap" data-frames="6">
  …
  <g id="radiusBandsRecap"></g>
  …
</figure>
```

`data-frames`가 `id` 앞에 오면 검사기의 `DIA_FIG`가 못 본다 (Task 1).

`s24`에는 figure 뒤에 마지막 비트 한 줄을 둔다:

```html
<p class="build" data-beat="5"><b>같은 코드가 방어와 삼킴으로 갈리는 조건은 하나입니다.</b> 잡은 층이 그 실패 대신 무엇을 할지 알고 있는가.</p>
```

`s04`는 figure 위에 약속 두 문장을 둔다 (figure 는 항상 보이고 두 문장이 비트 1·2):

```html
<p class="build promise" data-beat="1">경계에서는 엄격하게 검사해서 <b>빨리 죽입니다</b>.</p>
<p class="build promise" data-beat="2">조립하는 자리에서는 부분 실패를 흡수해서 <b>버팁니다</b>.</p>
<figure class="dia" id="diaRadiusIntro" data-frames="6">…</figure>
```

- [ ] **Step 5: 구동기와 단계 배열을 옮긴다**

`ASSET:JS`를 채운다. 순서대로:

1. 파일럿 `oauth2_slides.html` 2579–2620 의 `diaAt`·`wireDia`(덱판)를 그대로. 출처 주석에 "파일럿과 같은 함수"라고 적는다.
2. 원본 4567–4580 `RADIUS`, 4595–4626 `paintRadiusDia` 그대로.
3. 원본 4805–4816 의 `RADIUS.map(...)`을 함수로 감싼다:

```js
/* 출처: defensive_programming.html 4805-4816. 단계 문구는 RADIUS 에서 그대로 나온다 —
   두 지도(s04·s51)와 캡션이 어긋날 수 없는 이유가 이 배열 하나다. 배열 리터럴이
   아니라서 검사기는 단계 수를 못 세고, figure 의 data-frames="6" 이 그 자리를 대신한다. */
function radiusSteps(){
  return RADIUS.map(r => ({
    c: '이 반경이 하는 일은 <b>"' + r.can + '"</b>입니다.'
       + (r.hole === '여기가 종착지다'
            ? ' <span class="ye">여기가 종착지입니다. 이 반경 밖에는 코드가 없습니다.</span>'
            : ' <span class="no">그럼에도 "' + r.hole + '"는 것이 남습니다.</span>'),
    h: 4000,
  }));
}
```

4. `registerAssets()`를 채운다. 원본 4727–4799 의 아홉 `wireDia(...)` 호출을 옮기되 `registerBeats('sNN', …)`로 감싼다. 반경 지도는 **그리기가 먼저**다 — `wireDia`가 `[data-at]`을 찾는 시점에 띠가 있어야 한다:

```js
function registerAssets(){
  /* 출처: defensive_programming.html 4727-4799. registerBeats 로 감싼 것만 다르다. */
  registerBeats('s06', wireDia('diaBlame', [ /* 4727-4735 의 단계 배열 그대로 */ ]));
  registerBeats('s08', wireDia('diaSilent', [ /* 4736-4744 */ ]));
  registerBeats('s13', wireDia('diaBoundary', [ /* 4745-4751 */ ]));
  registerBeats('s17', wireDia('diaShape', [ /* 4752-4758 */ ]));
  registerBeats('s23', wireDia('diaCommit', [ /* 4759-4766 */ ]));
  registerBeats('s24', wireDia('diaLayers', [ /* 4767-4774 */ ]));
  registerBeats('s33', wireDia('diaPool', [ /* 4775-4782 */ ]));
  registerBeats('a02', wireDia('diaBudget', [ /* 4783-4790 */ ]));
  registerBeats('s40', wireDia('diaSpecGap', [ /* 4791-4799 */ ]));

  /* 반경 지도 두 벌. 띠를 먼저 그려야 wireDia 가 [data-at] 을 찾는다. */
  paintRadiusDia($('#radiusBandsIntro'));
  paintRadiusDia($('#radiusBandsRecap'));
  // s04 는 미리 보여 주는 자리라 등록하지 않는다. 마지막 프레임에 세워 두고 그 장의
  // 비트는 .build 둘만 센다. 여섯 비트로 넘기는 것은 s51 하나다.
  const intro = wireDia('diaRadiusIntro', radiusSteps());
  if(intro) intro.go(RADIUS.length - 1);
  registerBeats('s51', wireDia('diaRadiusRecap', radiusSteps()));
}
```

위 주석 자리에는 원본의 단계 배열을 **글자 그대로** 붙여 넣는다. 배열 안의 `h:` 값은 지우지 않는다.

- [ ] **Step 6: 검사와 눈 확인**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: 도해 관련 위반 0 (`SVG 는 있는데 wireDia 호출이 없다`·`프레임 ≠ 단계`·`등록됐는데 … 자산이 없다` 전부 0). 남는 위반은 대본 하한과 합계뿐.

Run: `python3 -m pytest tools/test_deck_behavior.py -k "declared_frame or font_floor or overflow" -v`
Expected: 전부 PASS. `[defensive]`의 활자 하한에서 `.dia-cap`·SVG 글자가 걸리면 Step 3 의 값을 조정한다 — 하한을 낮추지 말고 크기를 올린다.

브라우저에서 `s06`으로 가서 오른쪽 화살표로 여섯 프레임이 넘어가는지, `s04`의 지도가 여섯 띠 전부 켜진 채로 서 있는지, `s51`이 여섯 비트로 도는지 본다.

- [ ] **Step 7: 커밋**

```bash
git add defensive_programming_slides.html tools/test_deck_behavior.py
git commit -m "defprog 덱: 도해 열 장과 반경 지도 두 벌 — data-frames 실측 테스트"
```

---

## Task 5: 자산 이식 ② — 데모 넷과 컨트롤러 넷 · 퀴즈 열다섯 · Prism · Store 스텁

**Files:**
- Modify: `defensive_programming_slides.html` (`<head>` Prism 테마, `ASSET:CSS`, `DECK:STAGE:CSS`, `SLIDES`의 s01·s07·s11·s15·s21·s25·s28·s31·s34·s37·s46·s49·s52·a11·a12, `ASSET:JS`, Prism 스크립트 두 개)
- Modify: `tools/test_deck_behavior.py` (컨트롤러 넷 동작 테스트)

**Interfaces:**
- Consumes: Task 1 의 `REGISTER_MOUNT`(네 함수), Task 4 의 `registerAssets()`
- Produces: `wireEl(mountId)`, `wireAssembly(mountId, {controls, preset, beats})`, `wireJudge(mountId)`, `wireWord(mountId)` — 넷 다 `{n, go(k)}` 또는 마운트가 없으면 `null`. `wireQuizzes()`, `wireQuizBank(slideId)`, `markChangedLines()`, `Store` 스텁, `esc`

- [ ] **Step 1: 실패하는 테스트 — 컨트롤러 넷**

`tools/test_deck_behavior.py` 끝에 추가. 둘째 덱만 보는 테스트라 `deck` 이 아니라 경로를 직접 쓴다 — 파일럿에는 이 데모가 없다.

```python
# --- Task 5 · 데모 컨트롤러 넷 -------------------------------------------------

DEFPROG = os.path.join(ROOT, 'defensive_programming_slides.html')


def _go_slide(page, sid):
    page.evaluate('sid => Deck.go(Deck.slides.findIndex(s => s.id === sid))', sid)


def _beat(page, b):
    page.evaluate('b => { Deck.beat = b; applyBeat(Deck.slides[Deck.index], b); }', b)


def test_el_lab_walks_the_five_values_by_beat(page):
    page.goto('file://' + DEFPROG)
    _go_slide(page, 's07')
    assert page.evaluate('beatCount(Deck.slides[Deck.index])') == 5
    kinds = []
    for b in range(5):
        _beat(page, b)
        kinds.append(page.evaluate("document.querySelector('#elLab07 .pick.on').dataset.k"))
    assert kinds == ['dto', 'map', 'null', 'string', 'list']
    _beat(page, 3)
    assert 'PropertyNotFoundException' in page.inner_text('#elLab07 .el-out')


def test_assembly_21_dies_on_beat_one(page):
    page.goto('file://' + DEFPROG)
    _go_slide(page, 's21')
    _beat(page, 0)
    assert page.query_selector('#asmLab21 .asm-500') is None
    _beat(page, 1)
    assert page.query_selector('#asmLab21 .asm-500') is not None


def test_assembly_28_isolation_leaves_one_blank_and_seven_ok(page):
    page.goto('file://' + DEFPROG)
    _go_slide(page, 's28')
    _beat(page, 0)
    assert page.query_selector('#asmLab28 .asm-500') is not None
    _beat(page, 1)
    assert page.query_selector('#asmLab28 .asm-500') is None
    assert page.evaluate("document.querySelectorAll('#asmLab28 .asm-sec.s-gone').length") == 1
    assert page.evaluate("document.querySelectorAll('#asmLab28 .asm-sec.s-ok').length") == 7


def test_assembly_34_timeout_brings_the_page_under_a_second(page):
    page.goto('file://' + DEFPROG)
    _go_slide(page, 's34')
    ms = lambda: int(re.search(r'(\d+)ms', page.inner_text('#asmLab34 .asm-meter')).group(1))
    _beat(page, 0)
    assert ms() > 3000
    _beat(page, 1)
    assert ms() < 1000
    assert page.evaluate("document.querySelectorAll('#asmLab34 .asm-sec.s-gone').length") == 1


def test_judge_lab_shows_one_card_per_beat_and_reveals_on_click(page):
    page.goto('file://' + DEFPROG)
    _go_slide(page, 's25')
    assert page.evaluate('beatCount(Deck.slides[Deck.index])') == 8
    for b in range(8):
        _beat(page, b)
        visible = page.evaluate(
            "Array.from(document.querySelectorAll('#judgeLab25 .jcard'))"
            ".filter(c => c.offsetParent !== null).map(c => c.dataset.k)")
        assert len(visible) == 1, '비트 %d 에 카드 %d 장' % (b, len(visible))
    _beat(page, 1)   # 결제 금액 카드. 정답은 fast
    page.click('#judgeLab25 .jcard[data-k="pay"] .jbtn[data-a="fast"]')
    why = page.inner_text('#judgeLab25 .jcard[data-k="pay"] .jwhy')
    assert '맞았습니다' in why and '빨리 죽어야' in why


def test_word_lab_fills_the_four_slots_by_beat(page):
    page.goto('file://' + DEFPROG)
    _go_slide(page, 's46')
    assert page.evaluate('beatCount(Deck.slides[Deck.index])') == 4
    _beat(page, 0)
    assert page.evaluate("document.querySelectorAll('#wordLab46 .gap').length") == 3
    _beat(page, 3)
    assert page.evaluate("document.querySelectorAll('#wordLab46 .gap').length") == 0
    out = page.inner_text('#wordLab46 .reqout')
    assert '2초' in out and '경고' in out
```

Run: `python3 -m pytest tools/test_deck_behavior.py -k "el_lab or assembly_ or judge_lab or word_lab" -v`
Expected: 6 FAIL (마운트가 없다).

- [ ] **Step 2: Prism 을 옮긴다**

원본 8–10 의 `<style id="prism-theme">…</style>`를 새 덱 `<head>`의 `<style>` **앞**에 그대로 넣는다. 원본 4302–4349 의 `<script id="prism-src">`·`<script id="prism-markup-jsp">` 두 개를 새 덱의 `<script type="application/json" id="deck-script">` **앞**에 그대로 넣되, 첫 태그를 `<script id="prism-src" data-manual>`로 바꾼다. 자동 하이라이트를 끄고 `wireDemos()`가 명시적으로 부른다 — 그래야 바뀐 줄 표시(`markChangedLines`)가 항상 하이라이트 **뒤**에 돈다.

`tools/check_dead_css.py`는 `id="prism-theme"`인 스타일 블록을 건너뛴다. id 를 바꾸지 않는다.

- [ ] **Step 3: 무대 규칙을 더한다 — 데모와 퀴즈**

`DECK:STAGE:CSS`의 도해 규칙 아래에:

```css
/* ---- 데모 넷 (Task 5) ----
   원본 데모의 글자는 11.5~15.5px 이다. 내용을 나르는 것은 전부 하한(24/20)으로 올리고,
   이름표 띠(.demo-tag)와 안내 문단은 마크업에서 뺐다 — 발표자가 말한다. */
.slide .demo{margin:0;padding:16px 20px}
.slide .pick{font-size:24px;padding:10px 20px}
.slide .kv{font-size:24px;gap:6px 18px;margin:10px 0}
.slide .kv .k{font-size:20px}
.slide .trace{font-size:20px;line-height:1.6;margin:10px 0;padding:12px 16px}
.slide .verdict{font-size:24px;padding:10px 16px}
/* 조립 시뮬레이터. 여덟 칸을 한 줄씩 세우면 720 을 넘는다 — 두 열로 4줄. */
.slide .asm-screen{grid-template-columns:1fr 1fr;min-height:0;padding:10px}
.slide .asm-sec{font-size:24px;padding:8px 14px}
.slide .asm-sec span{font-size:20px}
.slide .asm-500{font-size:28px;min-height:200px}
.slide .asm-500 span{font-size:24px;max-width:none}
.slide .asm-ctl{gap:6px;margin-bottom:8px}
.slide .ctl-row{font-size:24px}
.slide .ctl-k{font-size:24px;min-width:230px}
.slide .ctl-sel,.slide select,.slide option{font-size:24px;padding:6px 10px}
.slide .tog{font-size:20px;padding:8px 14px}
/* 판단 카드. 한 번에 한 장만 서고 크게 그린다. */
.slide .jcard{padding:18px 22px;margin:0}
.slide .jcard.off{display:none}
.slide .jcard .jq{font-size:30px;line-height:1.4}
.slide .jcard .jn{flex:0 0 36px;width:36px;height:36px;font-size:20px;border-radius:10px}
.slide .jbtns{margin:18px 0 0 46px;gap:14px}
.slide .jbtn{font-size:24px;padding:10px 24px}
.slide .jwhy{font-size:24px;line-height:1.5;margin:16px 0 0 46px;padding:14px 18px}
/* 요건 문장 빌더. */
.slide .wgrid{gap:12px 18px}
.slide .wfield{font-size:24px;gap:4px}
.slide .wfield input{font-size:24px;padding:8px 12px}
.slide .reqout{font-size:28px;line-height:1.6;margin:14px 0 10px}
.slide .gap{font-size:24px}

/* ---- 퀴즈 (Task 5) ---- 파일럿과 같은 값. "✅ 체크포인트" 머리띠는 뺀다. */
.slide .quiz{margin:0}
.slide .quiz .q-head{display:none}
.slide .quiz .q{font-size:28px;line-height:1.45;margin:0 0 16px}
.slide .quiz .opt{font-size:24px;line-height:1.45;padding:10px 18px;margin:8px 0}
.slide .quiz .explain{font-size:24px;line-height:1.5;padding:12px 16px;margin-top:12px}
.slide .quiz + p.build{margin:18px 0 0}
.slide .quiz.q-off{display:none}
```

- [ ] **Step 4: 데모 마크업을 놓는다**

원본의 안내 문단과 `.demo-tag`는 옮기지 않는다. 마운트 넷과 세 조립 시뮬레이터:

```html
<!-- s07 -->
<div class="demo" id="elLab07"><div class="picker"></div><div class="el-out"></div></div>

<!-- s21 · s28 · s34 : id 만 다르다 -->
<div class="demo" id="asmLab21"><div class="asm-ctl"></div><div class="asm-screen"></div><div class="asm-meter"></div></div>

<!-- s25 -->
<div class="demo" id="judgeLab25"></div>

<!-- s46 -->
<div class="demo" id="wordLab46"><div class="word-fields"></div><div class="word-out"></div></div>
```

`s01`·`s51`에는 원본 696–707 의 `<pre class="trace"><code>…</code></pre>`를 그대로 놓는다 (두 장 같은 마크업).

- [ ] **Step 5: 퀴즈 열다섯을 놓는다**

원본에서 `data-qid`로 찾아 `<div class="quiz" …> … </div>` 블록을 통째로 옮긴다. 본편 여섯은 해당 장의 `<h2>` 아래, 뒤에 마무리 한 줄:

| 장 | qid | 뒤에 오는 `p.build` (data-beat="1") |
|---|---|---|
| `s11` | `q-trace` | 열 줄이 증명하는 것은 <b>렌더링 시점에 그 자리에 문자열이 있었다</b>는 사실 하나입니다. |
| `s15` | `q-boundary` | 원인이 무엇으로 밝혀지든 <b>선을 그을 자리는 같습니다</b>. 값이 우리 타입이 되는 자리입니다. |
| `s31` | `q-failfast` | 저울은 하나입니다. <b>틀린 것을 보여 주는 대가</b>와 <b>아무것도 못 보여 주는 대가</b>. |
| `s37` | `q-fallback` | 얼마나 오래된 것까지 괜찮은지는 <b>코드 밖에서</b> 받아 와야 하는 답입니다. |
| `s49` | `q-wording` | "정해 주지 않으면 이렇게 하겠습니다"는 <b>침묵을 승인으로</b> 바꿉니다. |
| `s52` | `q-recap` | 안쪽에서 또 검사하고 있다면 <b>경계가 제 일을 못 하고 있다</b>는 신호입니다. |

부록 `a11`에 `q-unknown`·`q-silent`·`q-invariant`·`q-assembly`·`q-swallow` 다섯, `a12`에 `q-slowdown`·`q-specgap`·`q-questions`·`q-process` 넷을 차례로 놓는다. 퀴즈 안의 `<p style="margin:8px 0 0">`처럼 인라인 style 이 있으면 그대로 둔다 (font-size 가 아니라 검사에 안 걸린다).

- [ ] **Step 6: 스크립트를 옮기고 컨트롤러를 쓴다**

`ASSET:JS`의 `radiusSteps()` 뒤, `registerAssets()` 앞에 순서대로:

```js
/* 원본의 진행 기록(localStorage)은 덱에 없다. 데모가 부르는 두 메서드만 남긴 스텁 —
   file:// 에서 localStorage 에 기대지 않는다는 파일럿 규칙이다. */
const Store = { get(k, d){ return d; }, set(){} };
const esc = s => String(s).replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* 출처: defensive_programming.html 4822-4849 (EL 모듈) 그대로 */
const EL = (() => { /* 원본 그대로 */ })();

/* 출처: 4852-4876 의 배선 IIFE. 변경점: 전역 id(#elPicker·#elOut) 대신 마운트 안에서
   찾고, 컨트롤러를 돌려준다. go(k) 는 k 번째 값을 누른 것과 같은 상태를 그린다. */
function wireEl(mountId){
  const root = $('#' + mountId); if(!root) return null;
  const picker = $('.picker', root), out = $('.el-out', root);
  picker.innerHTML = EL.VALUES.map(v =>
    `<button class="pick" data-k="${v.k}">${esc(v.label)}</button>`).join('');
  const VERDICT = {
    value: '<div class="verdict good">값이 나옵니다</div>',
    empty: '<div class="verdict warn">아무 일도 일어나지 않습니다. 그것이 문제입니다</div>',
    throw: '<div class="verdict bad">예외가 던져지고, 페이지는 여기에서 끝납니다</div>',
  };
  function render(k){
    const v = EL.VALUES.find(x => x.k === k);
    const r = EL.resolve(k, 'bannerImageList');
    $$('.pick', picker).forEach(b => b.classList.toggle('on', b.dataset.k === k));
    out.innerHTML = `
      <div class="kv">
        <span class="k">section에 들어 있는 것</span><span>${esc(v.label)}</span>
        <span class="k">EL이 하는 일</span><span class="dim">${esc(v.hint)}</span>
      </div>
      <pre class="trace"><code>${esc(r.text)}</code></pre>
      ${VERDICT[r.result]}`;
  }
  $$('.pick', picker).forEach(b => b.addEventListener('click', () => render(b.dataset.k)));
  render('dto');
  return { n: EL.VALUES.length, go(k){ render(EL.VALUES[Math.max(0, Math.min(EL.VALUES.length - 1, k))].k); } };
}

/* 출처: 5058-5148 (Assembly 엔진), 5156-5268 (SECTION_STATE · renderAssembly · buildControls) 그대로 */
const Assembly = (() => { /* 원본 그대로 */ })();
const SECTION_STATE = { /* 원본 그대로 */ };
function renderAssembly(rootSel, opts){ /* 원본 그대로 */ }
function buildControls(root, controls, state, paint){ /* 원본 그대로 */ }

/* 조립 시뮬레이터를 비트에 매단다. beats[k] 는 {faults, strategy} 이고, go(k) 가 그것을
   state 에 적용해 다시 그린다. 마우스 조작은 살아 있다 — 질문이 나오면 그 자리에서 다른
   결함을 넣어 볼 수 있고, 다음 비트가 다시 덮어쓴다. */
function wireAssembly(mountId, opts){
  const root = $('#' + mountId); if(!root) return null;
  const ctl = renderAssembly('#' + mountId, {controls: opts.controls || ['fault'], preset: opts.preset || {}});
  const beats = opts.beats || [{}];
  function sync(){
    const st = ctl.state;
    $$('.tog', root).forEach(b => {
      b.classList.toggle('on', !!st.strategy[b.dataset.tog]);
      b.textContent = st.strategy[b.dataset.tog] ? '켬' : '끔';
    });
    const tp = $('.picker[data-pick="timeout"]', root);
    if(tp) $$('.pick', tp).forEach(x => x.classList.toggle('on',
      (x.dataset.k === '' ? null : Number(x.dataset.k)) === st.strategy.timeoutMs));
    const fb = $('.picker[data-pick="fallback"]', root);
    if(fb) $$('.pick', fb).forEach(x => x.classList.toggle('on', x.dataset.k === st.strategy.fallback));
    const sel = $('.ctl-sel', root);
    const target = Object.keys(st.faults).find(id => st.faults[id] !== 'ok');
    if(sel && target) sel.value = target;
    const fp = $('.picker[data-pick="fault"]', root);
    const cur = (sel && st.faults[sel.value]) || 'ok';
    if(fp) $$('.pick', fp).forEach(x => x.classList.toggle('on', x.dataset.k === cur));
  }
  return {
    n: beats.length,
    go(k){
      const b = beats[Math.max(0, Math.min(beats.length - 1, k))];
      ctl.state.faults = Object.assign({}, b.faults || {});
      ctl.state.strategy = Object.assign({}, Assembly.DEFAULT_STRATEGY, opts.preset || {}, b.strategy || {});
      ctl.paint(); sync();
    },
  };
}

/* 출처: 5332-5351 의 CARDS·VERDICT 를 최상위로 끌어올렸다. 문구는 그대로. */
const JUDGE_CARDS = [ /* 원본 여덟 장 그대로 */ ];
const JUDGE_VERDICT = {fast:'이 자리는 빨리 죽어야 합니다.', soft:'이 자리는 버텨야 합니다.'};

/* 출처: 5353-5412 의 배선. 변경점: 한 번에 한 장만 보이고(.off), 점수판은 없다.
   Store 는 스텁이라 고른 답은 이 장을 떠나도 남지 않는다 — ← 로 돌아오면 다시 고른다. */
function wireJudge(mountId){
  const root = $('#' + mountId); if(!root) return null;
  const picked = {};
  root.innerHTML = JUDGE_CARDS.map((c, i) => `
    <div class="jcard" data-k="${c.k}">
      <div class="jq"><span class="jn">${i + 1}</span><span>${esc(c.q)}</span></div>
      <div class="jbtns">
        <button class="jbtn" data-a="fast">빨리 죽는다</button>
        <button class="jbtn" data-a="soft">버틴다</button>
      </div>
      <div class="jwhy" hidden></div>
    </div>`).join('');
  function paintCard(card, c){
    const chosen = picked[c.k];
    $$('.jbtn', card).forEach(b => {
      b.disabled = !!chosen;
      b.classList.toggle('hit',  !!chosen && b.dataset.a === c.a);
      b.classList.toggle('miss', !!chosen && b.dataset.a === chosen && chosen !== c.a);
    });
    const why = $('.jwhy', card);
    why.hidden = !chosen;
    if(chosen) why.innerHTML = `<b>${chosen === c.a ? '맞았습니다' : '아쉽습니다'}. ${JUDGE_VERDICT[c.a]}</b> ${esc(c.why)}`;
  }
  const cards = $$('.jcard', root);
  cards.forEach(card => {
    const c = JUDGE_CARDS.find(x => x.k === card.dataset.k);
    $$('.jbtn', card).forEach(b => b.addEventListener('click', () => {
      if(picked[c.k]) return;
      picked[c.k] = b.dataset.a;
      paintCard(card, c);
    }));
    paintCard(card, c);
  });
  const show = i => cards.forEach((card, k) => card.classList.toggle('off', k !== i));
  show(0);
  return { n: cards.length, go(k){ show(Math.max(0, Math.min(cards.length - 1, k))); } };
}

/* 출처: 5420-5449 QUESTIONS 그대로 (s42·s43·a05·a06 이 읽는다) */
const QUESTIONS = [ /* 원본 그대로 */ ];

/* 출처: 5520-5525 의 SLOTS 를 최상위로. 자리 표시 문구가 곧 이번 사건의 예문이다. */
const WORD_SLOTS = [
  {k:'when', label:'조건',            ph:'전시 섹션의 데이터를 2초 안에 받지 못하면'},
  {k:'do',   label:'행동',            ph:'그 섹션은 숨긴다'},
  {k:'show', label:'사용자가 보는 것', ph:'아무것도 표시하지 않고 아래 섹션이 올라온다'},
  {k:'keep', label:'우리가 남기는 것', ph:'섹션 식별자와 소요 시간을 경고로 남긴다'},
];

/* 출처: 5511-5670 의 빌더. 변경점 셋 — 질문 select 와 예시 표(EXAMPLES)를 뺐고, 복사
   버튼을 뺐고(file:// 에서 clipboard 가 막힌다), go(k) 가 k 번째 칸까지 예문으로 채운다.
   발표자가 칸을 직접 고쳐 쓸 수 있고, 다음 비트가 그 칸부터 다시 채운다. */
function wireWord(mountId){
  const root = $('#' + mountId); if(!root) return null;
  const fields = $('.word-fields', root), out = $('.word-out', root);
  const val = {};
  const label = k => WORD_SLOTS.find(s => s.k === k).label;
  function sentenceHTML(){
    const g = k => val[k] ? esc(val[k]) : `<span class="gap">〈${esc(label(k))}〉</span>`;
    return `${g('when')}, ${g('do')}. 사용자에게는 ${g('show')}. 시스템은 ${g('keep')}.`;
  }
  function render(){
    const filled = WORD_SLOTS.filter(s => val[s.k]).length;
    $$('.wfield input', fields).forEach(inp => { inp.value = val[inp.dataset.k] || ''; });
    out.innerHTML = `
      <div class="reqout">${sentenceHTML()}</div>
      ${filled === 4
        ? '<div class="verdict good">이 문장은 그대로 인수 조건이 되고, 그대로 테스트 이름이 됩니다.</div>'
        : '<div class="verdict warn">빈칸이 남아 있습니다. 빈칸으로 배포하면 그 결정은 코드를 쓰는 사람이 혼자 내리게 됩니다.</div>'}`;
  }
  fields.innerHTML = `<div class="wgrid">${WORD_SLOTS.map(s => `
    <label class="wfield"><span>${esc(s.label)}</span>
      <input type="text" data-k="${s.k}" placeholder="예: ${esc(s.ph)}"></label>`).join('')}</div>`;
  $$('.wfield input', fields).forEach(inp => inp.addEventListener('input', e => {
    val[e.target.dataset.k] = e.target.value; render();
  }));
  render();
  return {
    n: WORD_SLOTS.length,
    go(k){
      WORD_SLOTS.forEach((s, i) => { val[s.k] = i <= k ? s.ph : ''; });
      render();
    },
  };
}

/* 출처: oauth2_slides.html 2916-2922 (wireQuizBank) · 3137-3143 (wireQuizzes) 그대로 */
function wireQuizBank(slideId){ /* 파일럿 그대로 */ }
function wireQuizzes(root=document){ /* 파일럿 그대로 */ }

/* 전과 후 코드의 바뀐 줄 표시. Prism 은 code 의 textContent 로 다시 그리므로 마크업에
   미리 넣은 표시가 살아남지 못한다 — 하이라이트가 끝난 뒤 pre[data-chg] 의 줄 번호
   (1부터, 쉼표 구분)에 .chg 를 두른다. 한 줄 안에서만 여닫히는 토큰만 있어야 한다. */
function markChangedLines(){
  $$('pre[data-chg] > code').forEach(code => {
    const want = new Set(code.parentElement.dataset.chg.split(',').map(s => parseInt(s.trim(), 10)));
    code.innerHTML = code.innerHTML.split('\n').map((line, i) =>
      want.has(i + 1) ? `<span class="chg">${line}</span>` : line).join('\n');
  });
}
```

`registerAssets()`의 끝에 데모 등록을 더한다:

```js
  registerBeats('s07', wireEl('elLab07'));
  registerBeats('s21', wireAssembly('asmLab21', {
    beats: [{faults:{}}, {faults:{event:'throw'}}],
  }));
  registerBeats('s28', wireAssembly('asmLab28', {
    controls: ['fault', 'isolate'],
    beats: [{faults:{event:'throw'}, strategy:{isolate:false}},
            {faults:{event:'throw'}, strategy:{isolate:true}}],
  }));
  registerBeats('s34', wireAssembly('asmLab34', {
    controls: ['fault', 'timeout'], preset: {isolate:true},
    beats: [{faults:{reco:'slow'}, strategy:{timeoutMs:null}},
            {faults:{reco:'slow'}, strategy:{timeoutMs:300}}],
  }));
  registerBeats('s25', wireJudge('judgeLab25'));
  registerBeats('s46', wireWord('wordLab46'));
  registerBeats('a11', wireQuizBank('a11'));
  registerBeats('a12', wireQuizBank('a12'));
```

`wireDemos()`를 채운다:

```js
function wireDemos(){
  if(window.Prism) Prism.highlightAll();
  markChangedLines();
  wireQuizzes();   // 본편 여섯 장과 부록 은행 둘을 한 줄이 배선한다
}
```

`registerBeats`에 `null`을 넘기면 코어의 `beatCount`가 `ctrl.n`에서 죽는다. 파일럿과 같이 `registerBeats`는 `null`도 그냥 저장하고 `beatCount`가 `ctrl?ctrl.n:1`로 거른다 — 코어를 고치지 않는다. 마운트 id 가 어긋나면 그 장은 비트 1짜리가 되고, 검사기가 `등록됐는데 … 자산이 없다`로 잡는다.

- [ ] **Step 7: 검사와 테스트**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: 외부 요청 0, 자산 배치 위반 0. 남는 위반은 대본뿐.

Run: `python3 -m pytest tools/test_deck_behavior.py -k "el_lab or assembly_ or judge_lab or word_lab or font_floor or overflow or quiz" -v`
Expected: 컨트롤러 여섯 PASS. 활자 하한과 720 넘침이 `[defensive]`에서 걸리면 Step 3 의 값을 조정한다. `test_appendix_quiz_bank_…`는 아직 `pilot`에 묶여 있다 (Task 8).

브라우저에서 `s07`·`s21`·`s25`·`s46`을 오른쪽 화살표로 돌려 보고, `s25`에서 버튼을 눌러 판정이 펼쳐지는지 본다.

- [ ] **Step 8: 커밋**

```bash
git add defensive_programming_slides.html tools/test_deck_behavior.py
git commit -m "defprog 덱: 데모 넷과 컨트롤러 넷, 퀴즈 열다섯, Prism"
```

---

## Task 6: 본편 54장 콘텐츠 — 막 표지 · 전과 후 여섯 쌍 · 내일 할 것 여섯 장

**Files:**
- Modify: `defensive_programming_slides.html` (`SLIDES` 본편 전부, `DECK:STAGE:CSS`)

**Interfaces:**
- Consumes: Task 4·5 가 놓은 도해·데모·퀴즈, `.build[data-beat]`, `pre[data-chg]`
- Produces: `s00`~`s53` 전부에 내용. 슬라이드 종류 다섯(막 표지 `.act`, 전과 후 `.pair`, 내일 할 것 `.todo`, 도해·데모, 산문 build)이 각자 고정된 꼴을 갖는다

**슬라이드 작성 규칙 (파일럿 Task 6 그대로 + 이 덱의 셋):**

- `<h2>`는 대장의 제목 그대로. 개념 이름을 제목으로 쓰지 않는다.
- 화면에 문장을 늘어놓지 않는다. **말할 것은 대본으로, 화면에는 남길 것만.** 산문 슬라이드는 `<p>`·`<li>` 합쳐 다섯 줄을 넘기지 않는다.
- 단계가 있는 내용은 `.build[data-beat]`로 하나씩 연다.
- 인라인 `style`로 글자 크기를 쓰지 않는다.
- **금지어를 쓰지 않는다.** 부록으로 보낸 개념을 가리킬 때는 이름 대신 하는 일로 말한다. "회로 차단기"가 아니라 "반복 실패한 의존을 잠시 끊는 장치", "격벽"이 아니라 "섹션마다 자기 몫의 자원".
- **전과 후 코드는 한 판 여덟 줄·45자, `.chg` 셋 이하.**
- 각색 유지. 원본이 쓰는 이름만 쓴다.

- [ ] **Step 1: 무대 규칙을 더한다 — 세 가지 꼴**

`DECK:STAGE:CSS`의 퀴즈 규칙 아래에:

```css
/* ---- 막 표지 (Task 6) ---- 반경 번호·이름과 한 문장. 위에 여섯 반경 띠로 지금 어디인지. */
.slide.act{justify-content:center}
.slide.act .act-map{display:flex;gap:10px;margin-bottom:28px}
.slide.act .act-map span{
  font-family:var(--mono);font-size:20px;color:var(--text-mut);
  border:1px solid var(--border-2);border-radius:99px;padding:6px 16px;
}
.slide.act .act-map span.on{color:#1a1005;background:var(--accent);border-color:transparent}
.slide.act .act-no{font-family:var(--mono);font-size:24px;color:var(--accent);margin:0 0 14px}
.slide.act h2{font-size:52px}

/* ---- 전과 후 (Task 6) ---- 좌우 두 판. 왼쪽 "지금", 오른쪽 "고친 뒤". 바뀐 줄만 .chg */
.slide .pair{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start}
.slide .pair h3{font-size:24px;margin:0 0 8px;color:var(--text-mut);font-weight:700}
.slide .pair .after h3{color:var(--ok)}
.slide .pair pre{margin:0;padding:14px 16px;font-size:20px;line-height:1.5;border-radius:12px;
  background:#0a0f18;border:1px solid var(--border);overflow:hidden}
.slide .pair pre code{font-size:20px}
.slide .pair .chg{display:inline-block;width:100%;background:rgba(52,211,153,.16);border-radius:4px}
.slide .pair .before .chg{background:rgba(248,113,113,.16)}
/* s45 는 코드가 아니라 문장 쌍이다. 같은 두 판에 산문을 놓는다. */
.slide .pair .sent{font-size:26px;line-height:1.6;padding:16px 18px;border-radius:12px;
  background:var(--panel);border:1px solid var(--border);margin:0}
.slide .pair .after .sent{border-color:var(--ok)}

/* ---- 내일 할 것 (Task 6) ---- 찾을 것 · 바꿀 것 · 물을 것 세 줄. 왼쪽 이름표는 고정 폭. */
.slide.todo .todo-list{display:grid;gap:18px;margin:0}
.slide.todo .todo-list > div{display:grid;grid-template-columns:150px 1fr;gap:18px;align-items:start}
.slide.todo dt{font-family:var(--mono);font-size:24px;color:var(--accent);margin:0;padding-top:4px}
.slide.todo dd{font-size:26px;line-height:1.55;color:var(--text);margin:0}
.slide.todo dd code{font-size:22px}

/* ---- 산문 build 슬라이드의 목록 ---- */
.slide ul,.slide ol{margin:0;padding-left:1.1em}
.slide li{font-size:26px;line-height:1.6;color:var(--text-dim);margin:0 0 12px}
.slide li b{color:var(--text)}
.slide p.promise{font-size:34px;line-height:1.5;margin:0 0 10px;color:var(--text)}
.slide .suspects li{font-size:26px}
```

- [ ] **Step 2: 막 표지 셋 (s05 · s20 · s39) 과 여섯 반경 띠**

막 표지의 꼴. `.on`은 그 막의 반경에:

```html
  <section class="slide act" id="s05">
    <div class="act-map"><span class="on">1 한 줄</span><span>2 한 함수</span><span>3 한 객체</span><span>4 한 모듈</span><span>5 프로세스 경계</span><span>6 요구사항</span></div>
    <p class="act-no">반경 1 · 한 줄</p>
    <h2>터진 자리와 잘못된 자리는 다른 곳입니다</h2>
  </section>
```

`s20`은 `4 한 모듈`에 `.on`, 문장 "섹션 하나가 죽어서 메인이 죽었습니다". `s39`는 `6 요구사항`에 `.on`, 문장 "기획서에는 정상 경로만 있습니다". 2·3·5막은 도해 슬라이드가 막을 연다 (`s13`·`s17`·`s33`) — 그 장의 `<h2>` 앞에 `<p class="act-no">반경 2 · 한 함수</p>` 한 줄만 둔다.

- [ ] **Step 3: 0막 (s00–s04)**

```html
  <section class="slide" id="s00">
    <h2>방어적 프로그래밍 — 하나가 죽었을 때 전체가 죽지 않게</h2>
    <p>이커머스 운영 개발팀 · 52분 · 화살표 하나로 굴러갑니다</p>
  </section>
  <section class="slide" id="s01">
    <h2>지난 9월 7일, 메인페이지가 통째로 오류를 냈습니다</h2>
    <pre class="trace"><code><!-- 원본 696-707 그대로 --></code></pre>
  </section>
  <!-- s02 는 Task 2 골격 그대로 -->
  <section class="slide" id="s03">
    <h2>방어적 프로그래밍은 예외를 없애는 기술이 아닙니다</h2>
    <p class="build promise" data-beat="1">잘못된 값이 <b>얼마나 멀리 가는지</b>를 미리 정해 두는 일입니다.</p>
    <p class="build promise" data-beat="2">실패 하나가 <b>얼마나 넓게 번지는지</b>를 미리 정해 두는 일입니다.</p>
  </section>
```

`s04`는 Task 4 에서 만들었다.

- [ ] **Step 4: 전과 후 여섯 쌍**

꼴은 하나다. `data-chg`는 1부터 세는 줄 번호다. Prism 언어 클래스는 `language-java`·`language-jsp`·(문장 쌍은 `pre` 없음).

```html
  <section class="slide" id="s09">
    <h2>전과 후 ① — 잡고 로그만 남기는 catch</h2>
    <div class="pair">
      <div class="before build" data-beat="0"><h3>지금</h3>
<pre data-chg="4,5"><code class="language-java">try {
  var banners = client.fetch(sectionId);
  model.put("bannerImageList", banners);
} catch (Exception e) {
  log.error("배너 조회 실패", e);
}</code></pre></div>
      <div class="after build" data-beat="1"><h3>고친 뒤</h3>
<pre data-chg="5,6,7"><code class="language-java">try {
  var banners = client.fetch(sectionId);
  model.put("bannerImageList", banners);
} catch (ClientException e) {
  throw new SectionLoadException(
    "배너 조회: section=" + sectionId
    + ", 받은 값=" + e.received(), e);
}</code></pre></div>
    </div>
  </section>
```

`s14` — 곳곳의 null 검사 → 우리 객체가 되는 자리에서 한 번:

```
[지금 · data-chg="2,4,6"]
// SectionService
if (res != null && res.getBody() != null) …
// MainAssembler
if (section != null && section.get("bannerImageList") != null) …
// mainSections.jsp
<c:if test="${not empty section.bannerImageList}">
// … 그리고 141곳 더

[고친 뒤 · data-chg="3,4,5"]
// SectionClient.parse — 우리 객체가 되는 자리
SectionContent parse(String body) {
  var dto = mapper.readValue(body, SectionContent.class);
  if (dto.getBannerImageList() == null)
    throw new BadResponseException(
      "bannerImageList 없음: " + summarize(body));
  return dto;
}
```

`s18` — `Map<String, Object>` → 필드가 정해진 클래스:

```
[지금 · data-chg="1,3"]
Map<String, Object> section = new HashMap<>();
section.put("id", row.get("SECTION_ID"));
section.put("bannerImageList", row.get("BANNERS"));
model.addAttribute("section", section);
// 무엇이든 들어갑니다. 문자열도, null 도.

[고친 뒤 · data-chg="3,6,7"]
public final class SectionContent {
  private final String id;
  private final List<Banner> bannerImageList;
  SectionContent(String id, List<Banner> b) {
    this.id = Objects.requireNonNull(id);
    this.bannerImageList = new ArrayList<>(b);
  }
}
```

`s29` — 한 JSP 에 섹션 나열 → include 와 c:catch 로 세운 경계 (`language-jsp`, `<`·`>`는 `&lt;`·`&gt;`로):

```
[지금 · data-chg="3,4,6"]
<%-- mainSections.jsp · 한 파일, 한 흐름 --%>
<c:forEach var="s" items="${sections}">
  <c:set var="banners"
         value="${s.bannerImageList}"/>
  <c:if test="${not empty banners}">
    <%-- 섹션 마크업 … 141개의 c:set --%>
  </c:if>
</c:forEach>

[고친 뒤 · data-chg="2,4,6"]
<%-- 없어도 되는 섹션만 이 안에 --%>
<c:catch var="err">
  <jsp:include page="sec/${s.type}.jsp"/>
</c:catch>
<c:if test="${not empty err}">
  <c:set target="${sectionErrors}"
         property="${s.id}" value="${err}"/>
</c:if>
```

`s35` — 타임아웃 없는 호출 → 연결과 읽기 두 값:

```
[지금 · data-chg="1,3"]
RestTemplate rest = new RestTemplate();
// 연결도 읽기도 기다림의 상한이 없습니다
String body = rest.getForObject(url, String.class);

[고친 뒤 · data-chg="2,3,4"]
var f = new SimpleClientHttpRequestFactory();
f.setConnectTimeout(300);   // 연결: 300ms
f.setReadTimeout(700);      // 읽기: 700ms
RestTemplate rest = new RestTemplate(f);
String body = rest.getForObject(url, String.class);
```

`s45` — 문장 쌍. `pre` 대신 `p.sent`:

```html
    <div class="pair">
      <div class="before build" data-beat="0"><h3>지금 · 정상 경로만</h3>
        <p class="sent">메인 화면은 전시 섹션 8개를 위에서부터 순서대로 보여 준다.</p></div>
      <div class="after build" data-beat="1"><h3>고친 뒤 · 네 칸을 채운 요건 문장</h3>
        <p class="sent"><b>전시 섹션의 데이터를 2초 안에 받지 못하면</b> 그 섹션은 <b>숨긴다</b>. 사용자에게는 <b>아무것도 표시하지 않고 아래 섹션이 올라온다</b>. 시스템은 <b>섹션 식별자와 소요 시간을 경고로 남긴다</b>.</p></div>
    </div>
```

- [ ] **Step 5: 내일 할 것 여섯 장**

꼴은 하나다:

```html
  <section class="slide todo" id="s12">
    <h2>내일 할 것 ① — catch 뒤에 로그만 있는 자리</h2>
    <dl class="todo-list">
      <div class="build" data-beat="0"><dt>찾을 것</dt><dd><code>catch (Exception</code> 뒤에 로그 한 줄만 있고, 던지지도 돌려주지도 않는 자리</dd></div>
      <div class="build" data-beat="1"><dt>바꿀 것</dt><dd>무엇을 하려다, 무엇에 대해, 무엇을 받았는지를 담아 다시 던진다. 원본 예외는 <code>cause</code>로 잇는다</dd></div>
      <div class="build" data-beat="2"><dt>물을 것</dt><dd>없음. 개인정보와 자격 증명은 로그에 담지 않는다는 규칙만 지킨다</dd></div>
    </dl>
  </section>
```

나머지 다섯의 세 줄:

| 장 | 찾을 것 | 바꿀 것 | 물을 것 |
|---|---|---|---|
| `s16` | 외부 응답(API·캐시·DB 결과)이 우리 객체가 되는 자리. 뷰와 서비스에 흩어진 null 검사 | 그 자리에서 한 번 검사하고 던진다. 안쪽의 null 검사는 지운다 | 없음 |
| `s19` | 화면에 넘기는 `Map<String, Object>` | 새로 만드는 화면 모델은 필드가 정해진 클래스로. 이미 있는 Map 은 화면에 넘기기 전에 한 번 클래스로 바꾼다 | 없음 |
| `s32` (build 4) | 한 JSP 에 순서대로 나열된 섹션 | 없어도 되는 섹션만 `jsp:include`와 `c:catch`로 감싼다. 잡은 뒤 빈자리에 놓을 것과 남길 기록을 정한다 | 어느 섹션이 없어도 되는지를 기획에 묻는다 |
| `s32` 넷째 줄 | `<dt>순서</dt>` 필수 섹션은 앞에 둔다. 기록은 뷰가 아니라 요청이 끝나는 자리(인터셉터)에서 한 번에 남긴다 | | |
| `s38` | `RestTemplate`·`HttpClient`·URL 연결을 만드는 자리 | 연결과 읽기 타임아웃 두 값을 준다 | 얼마나 기다릴지와, 그 뒤 빈자리에 무엇을 놓을지를 기획에 묻는다 |
| `s50` | SR 접수 문서에서 "없으면"·"늦으면"·"틀리면"이 한 번도 나오지 않는 화면 | 네 질문(①②④⑥)을 묻고, 답을 요건 문장 한 줄로 SR 에 남긴다 | 질문 넷 자체가 물을 것이다 |

`s53`은 같은 `.todo` 꼴로 여섯 줄. `dt`는 ①~⑥, `dd`는 각 "바꿀 것"의 첫 문장 그대로. 마지막에 `<p>` 한 줄: "더 읽을 것: <code>defensive_programming.html</code> 15장과 부록 셋. 부록 C 는 인쇄해서 SR 옆에 둡니다."

- [ ] **Step 6: 산문 build 슬라이드**

각 장의 `.build` 항목. **산문 build 는 `data-beat="1"`부터 시작한다** — 첫 비트는 제목만 있는 화면이고, 누를 때마다 한 줄이 열린다. 대장의 "build N · N+1"이 그 셈이다. 예외는 첫 줄이 곧바로 보여야 하는 내일 할 것(`.todo`)과 `s36`이고, 거기서는 0부터다 (대장의 "build N · N").

| 장 | 항목 |
|---|---|
| `s10` | ① 무엇을 하려다 — 연산 · ② 무엇에 대해 — 식별자 · ③ 무엇을 받았는지 — 타입과 요약 · ④ <b>담지 말 것</b> — 개인정보와 자격 증명. 값 전체가 아니라 요약과 타입만 |
| `s22` | ① 화면에서는 여덟 칸이 따로 보입니다 · ② 코드에서는 `<c:set>` 141번째, `<c:if>` 43번째까지 <b>한 흐름</b>입니다. 사이에 실패를 받아 줄 경계가 없습니다 |
| `s26` | ① 저울은 하나 — <b>틀린 것을 보여 주는 대가</b> 대 <b>아무것도 못 보여 주는 대가</b> · ② 여섯 번째 카드(메인 배너)는 저울로 잴 수 없습니다. 무엇이 필수인지는 <b>요구사항이 정합니다</b> |
| `s27` | ① 경계에서 아무도 타입을 확인하지 않아 잘못된 값이 뷰까지 갔습니다 · ② 조립하는 자리에서 아무도 흡수하지 않아 섹션 하나가 페이지 전체를 데려갔습니다 |
| `s30` | ① <b>받는 것</b> — 던지는 둘(문자열·리스트)만. 조용한 셋(null·Map·빈 값)은 못 받습니다 · ② <b>못 하는 것</b> — 이미 나간 출력을 되돌리지 못합니다 · ③ <b>정해 주지 않는 것</b> — 빈자리에 놓을 것. 잡기만 하면 조용한 빈칸이 하나 생깁니다 |
| `s36` | ① 아무것도 놓지 않는다 · ② 숨긴다 · ③ 직전 값 · ④ 골격만 · ⑤ <b>직전 값은 얼마나 오래된 것까지 괜찮은가</b> — 배너는 하루, 재고는 안 됩니다. 답은 코드 밖에 있습니다 |
| `s41` | ① 기획자는 실패 모드를 모릅니다 · ② 개발자는 자기 일이라 여겨 묻지 않습니다 · ③ QA 는 화면이 없는 요건을 검수 목록에 못 올립니다 · ④ <b>그래서 빈자리를 볼 수 있는 사람은 개발자뿐입니다</b> |
| `s42` | 데이터 ①②③ · 연동 ④⑤⑥ · 행위 ⑦⑧⑨ · 한계 ⑩⑪⑫ (네 줄, 축 이름과 번호만. 전체 문장은 부록 a05·a06) |
| `s43` | ① 이 데이터가 하나도 없으면 화면에 무엇이 보입니까 · ② 이 값이 오래된 것이어도 괜찮습니까. 몇 분까지 · ④ 이 정보를 주는 쪽이 응답하지 않으면 얼마나 기다립니까. 기다린 뒤에는 · ⑥ <b>이 화면에서 어느 부분이 없어도 화면이 성립합니까. 어느 부분이 없으면 띄우면 안 됩니까</b> · ⑤번째 build: <b>이 질문 하나만 기획 단계에서 던졌어도 그날 장애는 없었습니다</b> |
| `s44` | ① <b>기본값을 제안한다</b> — "정해 주지 않으면 이렇게 하겠습니다" · ② <b>비용으로 말한다</b> — 오늘 있었던 일로 · ③ <b>범위로 말한다</b> — 추가 기능이 아니라 그 기능의 완성 조건 |
| `s48` | ① 코드만 고치면 다음 기능에서 같은 구멍이 다시 생깁니다 · ② 회고가 남길 것은 <b>요건 문장 한 줄</b>입니다. 완료 정의와 설계 리뷰에 그 한 줄을 넣는 법은 부록에 |

`s43`의 질문 문구는 `QUESTIONS` 배열의 `q` 그대로다 (원본 5421–5447). 손으로 옮기되 글자를 바꾸지 않는다.

`s47`은 원본 3336–3342 의 `<pre class="language-java">` 블록 그대로 (`pre` 에 `data-chg` 없음).

- [ ] **Step 7: 검사와 눈 확인**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: 금지어 위반 0, 인라인 글자 크기 위반 0. 남는 위반은 대본뿐.

Run: `python3 -m pytest tools/test_deck_behavior.py -k "defensive and (font_floor or overflow or builds)" -v`
Expected: PASS. 720 을 넘는 장이 있으면 줄이지 말고 **쪼갠다**. 쪼개면 대장과 이 계획의 id 가 밀리므로, 대신 그 장의 `.build` 항목을 줄이는 쪽을 먼저 본다.

브라우저 `O` 개요 그리드로 54장을 훑어 **글자만 빽빽한 장**을 찾는다. 다섯 줄을 넘는 산문 슬라이드가 있으면 대본으로 옮긴다.

- [ ] **Step 8: 커밋**

```bash
git add defensive_programming_slides.html
git commit -m "defprog 덱: 본편 54장 — 막 표지, 전과 후 여섯 쌍, 내일 할 것 여섯 장"
```

---

## Task 7: 대본 54장 — 시간을 숫자로 맞춘다

**설계 12절의 확인 지점 2.**

**Files:**
- Modify: `defensive_programming_slides.html` (`<script type="application/json" id="deck-script">`)

**Interfaces:**
- Consumes: `seconds()` 규약 (공백 제외 글자 수 ÷ 5.5), Task 1 의 `check_banned_words`
- Produces: `s00`~`s53` 전부의 대본. 합계 3120초 ±180초, 장당 25~110초, 금지어 0

- [ ] **Step 1: 대본을 쓴다**

규칙:

- **그대로 읽으면 발표가 되는 완성된 문장.** 불릿이 아니다. `~/.claude/output-styles/fluent-korean.md`를 따른다.
- 슬라이드에 이미 쓰여 있는 문장을 그대로 읽지 않는다. 화면은 뼈대, 대본은 살이다.
- **청중은 몰라서 못 하는 사람들이다.** 개념어 다섯(경계·격리·빨리 죽기와 버티기·폴백·요건 문장)은 처음 나오는 장에서 같은 문장 안에서 뜻을 푼다. 경계는 `s13`, 격리는 `s28`, 빨리 죽기와 버티기는 `s25`, 폴백은 `s36`, 요건 문장은 `s45`.
- **금지어를 쓰지 않는다.** 부록으로 보낸 개념을 가리킬 때는 이름 대신 하는 일로 말한다. 검사기가 잡는다.
- 도해 슬라이드의 대본은 **원본 `wireDia` 단계의 `c` 캡션을 뼈대로** 삼는다. 프레임 순서와 같아야 발표자가 화면과 말을 맞출 수 있다. 문단 하나가 프레임 하나다.
- 데모 슬라이드의 대본은 비트마다 한 문단이다. `s21`은 두 문단(정상 → 예외), `s25`는 카드마다 한 문단(여덟), `s46`은 칸마다 한 문단(넷).
- 전과 후 슬라이드는 두 문단이다. 첫 문단이 "지금" 판을 보며 "이 코드, 우리 저장소에 있습니다"로 시작하고, 둘째 문단이 바뀐 줄을 짚는다.
- **막 사이 전환은 `RADIUS[i].hole`의 문장으로 시작한다.** `s12`의 마지막 문장은 "그렇다고 모든 곳에서 터뜨릴 수는 없습니다"이고, `s13`의 첫 문장이 그것을 받는다. 여섯 문장이 여섯 다리다:
  - 1→2막: 그렇다고 모든 곳에서 터뜨릴 수는 없다
  - 2→3막: 검사를 통과한 뒤에도 객체가 이상해질 수 있다
  - 3→4막: 객체가 옳아도 조립이 틀릴 수 있다
  - 4→5막: 죽지 않고 느려지면 이 방어는 통하지 않는다
  - 5→6막: 무엇으로 채울지는 여전히 정해져 있지 않다
  - 6→7막: 여기가 종착지다
- 원본 `.oneline` 열다섯 문장은 그 장을 닫는 문장으로 쓴다. `s27`은 8장의 것("경계에서는 엄격하게 검사해서 빨리 죽이고, 조립하는 자리에서는 부분 실패를 흡수해서 버팁니다")으로 닫는다.
- 각색 유지. 원인을 단정하지 않는다. "왜 문자열이었는지는 지금도 모릅니다"를 `s02`와 `s15`에서 한 번씩 말한다.

배분 목표:

| 막 | 슬라이드 | 목표 | 목표 글자 수 (×5.5) |
|---|---|---|---|
| 0 | s00–s04 | 4:00 | 1,320 |
| 1 | s05–s12 | 8:00 | 2,640 |
| 2 | s13–s16 | 4:00 | 1,320 |
| 3 | s17–s19 | 3:00 | 990 |
| 4 | s20–s32 | 13:30 | 4,455 |
| 5 | s33–s38 | 6:00 | 1,980 |
| 6 | s39–s50 | 11:00 | 3,630 |
| 7 | s51–s53 | 2:30 | 825 |
| **계** | 54 | **52:00** | **17,160** |

- [ ] **Step 2: 합계를 잰다**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: `본편 54장(52:xx)`가 49:00~55:00 안. 벗어나면 늘리지 말고 **깎는다**. 발표는 언제나 예상보다 늘어진다.

- [ ] **Step 3: 막별 배분을 확인한다**

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, 'tools')
import check_slides as cs
d = cs.read_deck('defensive_programming_slides.html')
acts = [('0', 0, 4, 240), ('1', 5, 12, 480), ('2', 13, 16, 240), ('3', 17, 19, 180),
        ('4', 20, 32, 810), ('5', 33, 38, 360), ('6', 39, 50, 660), ('7', 51, 53, 150)]
tot = 0
for name, a, b, goal in acts:
    s = sum(cs.seconds(d.script.get('s%02d' % i, [])) for i in range(a, b + 1))
    tot += s
    mark = 'ok' if abs(s - goal) <= 25 else '<<<'
    print('막%s  %s  목표 %s  차 %+.0f초  %s' % (name, cs._fmt(s), cs._fmt(goal), s - goal, mark))
print('합계 %s  목표 52:00  차 %+.0f초' % (cs._fmt(tot), tot - 3120))
EOF
```

Expected: 막별 차이 ±25초 안. `<<<`가 찍힌 막을 조절한다. 4막과 6막이 남으면 그 막 안에서 깎는다 — 다른 막을 늘려 메우지 않는다.

- [ ] **Step 4: 슬라이드별 상·하한과 금지어**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: `상한 110초를 넘는다`·`하한 25초에 못 미친다` 0건. `본편에 부록 용어` 0건. 상한을 넘으면 그 장의 대본을 앞뒤 장으로 나눈다. 하한에 못 미치면 앞뒤와 합친다. 금지어가 걸리면 이름을 하는 일로 바꾼다.

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming_slides.html
git commit -m "defprog 덱: 본편 대본 54장 — 합계 52분"
```

- [ ] **Step 6: 확인 지점 — 사용자에게 보고하고 멈춘다**

Step 2·3 의 출력(합계와 막별 배분)을 그대로 보고한다. 시간이 맞는지, 대본의 말투가 이 청중에게 맞는지 확인받는다. `s09`(전과 후 ①)와 `s43`(네 질문)의 대본 전문을 함께 보인다 — 이 둘이 이 덱의 어조를 대표한다.

---

## Task 8: 부록 13장과 대본 — 그리고 미뤄 둔 테스트를 푼다

**Files:**
- Modify: `defensive_programming_slides.html` (`SLIDES` 부록, `deck-script`)
- Modify: `tools/test_check_slides.py` (`SHIPPED`)
- Modify: `tools/test_deck_behavior.py` (`LATER` 테스트를 `deck`으로)

**Interfaces:**
- Consumes: Task 5 의 `wireQuizBank`·`diaBudget` 등록, Task 6 의 `.todo`·`.pair` 꼴
- Produces: `a00`~`a12` 내용과 대본. `SHIPPED`에 둘째 덱. 퀴즈 은행 테스트가 두 덱을 돈다

- [ ] **Step 1: 부록 슬라이드를 쓴다**

`a00`은 파일럿 `a00`과 같은 꼴(목록 넷 + 돌아가는 법 한 줄):

```html
  <section class="slide appendix" id="a00">
    <h2>부록 — 질문이 나올 때만 펼칩니다</h2>
    <ul>
      <li><b>한 객체 · 더 깊이</b> — 생성자에서 조건을 강제하면 검사할 필요가 없어지는 이유</li>
      <li><b>느린 것 · 더 깊이</b> — 타임아웃 값을 예산에서 나누는 법, 반복 실패를 끊는 장치, 섹션마다 자기 몫의 자원</li>
      <li><b>요구사항 · 더 깊이</b> — 열두 질문 전체, 완료 정의와 리뷰 템플릿, 자바·스프링 대응표</li>
      <li><b>JSP · 더 깊이</b> — 응답 버퍼와 오류 페이지, 잡은 실패를 한 번에 남기는 인터셉터</li>
    </ul>
    <p>본편으로 돌아갈 때는 <code>O</code> 로 개요를 열어 고르시면 됩니다.</p>
  </section>
```

| 장 | 내용 |
|---|---|
| `a01` | 원본 1523–1529 (세터 DTO)를 "지금", 1537–1545 (생성자 강제)를 "고친 뒤"로 `.pair` 꼴. 여덟 줄에 맞게 주석 줄을 뺀다 |
| `a02` | `diaBudget` (Task 4 에서 놓았다). 이 장부터 부록이라 "타임아웃 예산"이라는 말을 써도 된다 |
| `a03` | build 3: ① 반복 실패한 의존을 잠시 끊는 장치를 페이지 전체에 하나로 걸면, 실패하지 않은 필수 자리까지 건너뛴다 · ② 재시도는 이미 무너진 상대에게 부하를 곱한다. 간격을 두 배씩 늘리고 무작위 오차를 섞는다 · ③ 재시도해도 되는 연산은 한 번 실행한 결과와 여러 번 실행한 결과가 같은 연산뿐이다. 이 장의 `<h2>`는 대장 그대로 "회로 차단기와 재시도"이고 본문에서도 이름을 쓴다 — 부록이다 |
| `a04` | build 2: ① 격벽이 없으면 느린 섹션이 붙든 시간이 다음 섹션에 그대로 더해진다 · ② 섹션마다 자기 몫의 스레드·커넥션을 떼어 주면 가장 느린 하나가 값이 된다 |
| `a05` | build 6: `QUESTIONS`의 q1~q6 문장 그대로, 축 이름을 앞에 |
| `a06` | build 6: q7~q12 |
| `a07` | build 2: ① 완료 정의에 넣는 한 줄 — "이 기능의 실패 요건 문장이 있는가" · ② 설계 리뷰의 고정 질문 — 열두 질문 중 그 화면에 해당하는 것을 리뷰 템플릿으로 |
| `a08` | 표 하나. 원본 부록 A(4000줄 근처, `id="ap-java"`)의 대응표를 여섯 줄로 줄인다: `Objects.requireNonNull` · Bean Validation · `@ControllerAdvice` · Resilience4j 넷 · HTTP 클라이언트 타임아웃 자리 둘 · 트랜잭션 경계와 예외. 표 글자는 24px |
| `a09` | build 3: ① 버퍼가 차기 전에는 상태 코드도 헤더도 바꿀 수 있다 · ② 버퍼가 넘쳐 나가는 순간이 응답 커밋이고, 그 뒤에는 오류 페이지로 갈 수 없다 · ③ 버퍼를 키우면 미룰 수는 있어도 없앨 수는 없다 |
| `a10` | 원본 4215–4234 의 인터셉터 코드를 여덟 줄로 축약한 `pre` 하나 (`preHandle`에서 맵을 만들고 `afterCompletion`에서 한 번에 남긴다) |
| `a11`·`a12` | Task 5 에서 퀴즈를 놓았다. `<h2>` 아래에 퀴즈들만 |

- [ ] **Step 2: 부록 대본을 쓴다**

장마다 25~110초. 부록은 합계에서 빠지지만 질문이 나와 띄우는 순간 소리 내어 읽게 되므로 본편과 같은 규칙으로 쓴다. 부록에서는 금지어를 써도 되지만, 처음 쓰는 문장에서 뜻을 푼다.

- [ ] **Step 3: 미뤄 둔 테스트를 푼다**

`tools/test_check_slides.py`: `SHIPPED = ['oauth2_slides.html', 'defensive_programming_slides.html']`.

`tools/test_deck_behavior.py`: `test_appendix_quiz_bank_shows_exactly_one_question_per_beat(page, pilot)` → `(page, deck)`, 본문의 `page.goto('file://' + pilot)` → `page.goto('file://' + deck)`. 픽스처 주석의 LATER 목록에서 이 줄을 지운다.

- [ ] **Step 4: 검사와 테스트**

Run: `python3 tools/check_slides.py defensive_programming_slides.html`
Expected: `본편 54장(52:xx) + 부록 13장` · `✓ 통과` · exit 0.

Run: `python3 -m pytest tools/ -v`
Expected: 전부 PASS. `test_the_shipped_deck_passes_every_check[defensive_programming_slides.html]`과 `test_appendix_quiz_bank_…[defensive]`가 처음으로 돈다.

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming_slides.html tools/test_check_slides.py tools/test_deck_behavior.py
git commit -m "defprog 덱: 부록 13장과 대본 — 검사기 전부 통과"
```

---

## Task 9: 마무리 검사 — 죽은 CSS · 완주 · 알려진 이슈 노트

**Files:**
- Modify: `defensive_programming_slides.html` (`ASSET:CSS` 가지치기)
- Create: `docs/superpowers/notes/2026-09-08-defprog-slides-known-issues.md`

**Interfaces:**
- Consumes: 완성된 덱, `tools/check_dead_css.py`
- Produces: 통과 기록과 남겨 둔 것 목록

- [ ] **Step 1: 죽은 CSS 를 가지친다**

Run: `python3 tools/check_dead_css.py --report defensive_programming_slides.html`

보고서의 미사용 셀렉터를 지우되, 파일럿 알려진 이슈 6번의 규칙대로 **템플릿 리터럴 안에서 조립되는 클래스는 남긴다.** 이 덱에서 그런 것: `.s-ok` `.s-dim` `.s-warn` `.s-gone` `.s-cache` `.s-skel` `.s-open` `.asm-500`(`SECTION_STATE`·`renderAssembly`), `.hit` `.miss` `.off`(`wireJudge`), `.good` `.warn` `.bad`(`.verdict` 변형), `.on`(`.pick`·`.tog`·`.act-map span`), `.chg`(`markChangedLines`), `.q-off`(`wireQuizBank`), `.vis`(`wireDia`), `.correct` `.wrong` `.show`(`wireQuizzes`). 도해 CSS 의 `.pop` `.draw` `.breathe` `.wire` 등은 SVG 마크업 안의 `class` 에 있으므로 검사기가 센다 — 보고서에 뜬 것만 지운다.

지운 뒤 `python3 -m pytest tools/test_deck_behavior.py -k "defensive and (font_floor or overflow)"`로 화면이 그대로인지 확인한다.

- [ ] **Step 2: 완주 검사**

```bash
python3 - <<'EOF'
import os
from playwright.sync_api import sync_playwright
url = 'file://' + os.path.abspath('defensive_programming_slides.html')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.goto(url)
    seen, presses = set(), 0
    while True:
        seen.add(pg.evaluate('Deck.slides[Deck.index].id'))
        before = pg.evaluate('[Deck.index, Deck.beat]')
        pg.keyboard.press('ArrowRight'); presses += 1
        if pg.evaluate('[Deck.index, Deck.beat]') == before:
            break
    print('presses', presses, 'slides', len(seen), 'errors', errors)
    b.close()
EOF
```

Expected: `slides 67`, `errors []`. 누름 수는 본편 비트 합계 + 부록 비트 합계 − 1 이다. 대장의 비트를 더하면 본편 183 + 부록 47 = 230 이므로 **229** 이어야 한다. 크게 다르면 어느 장의 비트가 대장과 어긋난 것이다 — `Deck.slides.map(s=>[s.id, beatCount(s)])`로 찾는다.

- [ ] **Step 3: 전체 검사**

```bash
python3 tools/check_slides.py oauth2_slides.html defensive_programming_slides.html
python3 -m pytest tools/ -q
```

Expected: 두 덱 다 `✓ 통과`. pytest 실패 0.

- [ ] **Step 4: 알려진 이슈 노트**

`docs/superpowers/notes/2026-09-08-defprog-slides-known-issues.md`에 파일럿 노트와 같은 꼴로 적는다. 반드시 들어갈 항목:

1. **실제 프로젝터 가독성 미검증** — 파일럿 5번 그대로. 이 덱은 도해 열 장 전부가 SVG 글자를 가지므로 리허설 때 회의실에서 한 번 봐야 한다.
2. **`Store` 스텁** — `s25`에서 고른 답은 장을 떠나면 사라진다. `←`로 돌아오면 다시 고른다. 의도한 동작이다.
3. **죽은 CSS 보고서의 생존자 목록** — Step 1 에서 남긴 셀렉터와 이유.
4. **엔진을 고쳐야 했다면** — 두 덱에 같이 반영한 내역. 없었으면 "없었다"고 적는다.
5. **완주 기록** — Step 2·3 의 숫자.

- [ ] **Step 5: 커밋**

```bash
git add defensive_programming_slides.html docs/superpowers/notes/2026-09-08-defprog-slides-known-issues.md
git commit -m "defprog 덱: 죽은 CSS 가지치기 · 완주 검사 · 알려진 이슈 노트"
```

- [ ] **Step 6: 사용자에게 보고한다**

검사기 두 줄, pytest 한 줄, 완주 숫자, 노트의 다섯 항목을 보고한다. `index.html`은 손대지 않았다는 것과, 리허설 전에 실제 회의실에서 한 번 봐야 한다는 것을 함께 말한다.
