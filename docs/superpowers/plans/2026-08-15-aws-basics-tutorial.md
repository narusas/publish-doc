# AWS 기초 튜토리얼 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** "서버 한 대를 빌린 줄 알았는데 리소스가 아홉 개 생겨 있었다"에서 출발해 계정·리전/AZ·ARN·EC2·EBS·ENI·S3를 해체하고, 그 부품으로 로드밸런서·관리형·컴퓨트 세 갈래·요금·IaC를 다시 조립하는 단일 HTML 인터랙티브 튜토리얼 `aws_basics.html`을 만든다.

**Architecture:** `aws_network_security.html`의 골격(사이드바 · 자동 목차 · 스크롤스파이 진행률 · 용어사전 드로어 · 퀴즈 엔진 · `wirePicker`/`wireTogs` 배선)을 복제하고 내용을 교체한다. 각 장은 `<section id data-title>` 하나이고, 각 데모는 `데이터 객체 + render(k) + wirePicker(...)` 형태의 IIFE 하나다. 외부 의존성은 0이며 `file://`로 열어도 완전히 동작해야 한다.

**Tech Stack:** 순수 HTML + CSS + 바닐라 JS (ES2020). 임베딩 Prism 1.29.0 (core + clike + bash + json). 빌드 도구 없음. 검사 스크립트만 Python 3 표준 라이브러리.

**Spec:** [`docs/superpowers/specs/2026-08-15-aws-basics-tutorial-design.md`](../specs/2026-08-15-aws-basics-tutorial-design.md)

**사실 근거:** [`docs/superpowers/notes/2026-08-15-aws-basics-facts.md`](../notes/2026-08-15-aws-basics-facts.md) — **모든 태스크는 서술을 쓰기 전에 이 파일의 해당 V항목을 읽는다.**

---

## Global Constraints

프로젝트 전체에 적용된다. 모든 태스크의 요구사항에 암묵적으로 포함된다.

- **외부 의존성 0.** CDN·웹폰트·원격 이미지·`fetch`·`XMLHttpRequest` 전면 금지. 리소스는 전부 인라인. (다른 튜토리얼 파일로 가는 상대경로 `<a href>`는 허용)
- **단일 파일.** 산출물은 `aws_basics.html` 하나. `file://`로 열어 모든 기능이 동작해야 한다.
- **localStorage 접두어는 `awsbase:`.** 키는 `awsbase:visited`, `awsbase:solved`, `awsbase:ckl` 셋뿐. (`netsec:` `iamtut:`과 절대 충돌 금지)
- **언어는 한국어, 존댓말 서술.** 시리즈 톤 — 오해를 먼저 깨고 사실을 세우는 순서.
- **문체 규범**: spec §7의 cognitive-rhythm 규범을 따른다. 절 첫머리에 "이 절에서는 ~를 다룬다"를 쓰지 않고, 절 끝에 "다음은 ~를 본다"를 붙이지 않는다. 본문 자체를 화제로 삼는 문장(진행 예고, 범위 선언)을 쓰지 않는다. 같은 어미를 세 문장 연속으로 쓰지 않는다.
- **사실 규칙**: 근거 파일에 없는 AWS 동작은 **쓰지 말고 비워 둔 채 보고한다.** 완화해서 뭉개지 않는다. 근거 파일의 인용문과 요약이 어긋나면 인용문을 믿는다.
- **접근성:** 모든 인터랙티브 요소에 `:focus-visible` 아웃라인, `prefers-reduced-motion: reduce` 시 트랜지션 무력화, 토글에 `aria-pressed`, 드로어에 `aria-expanded`.
- **시리즈 색상:** 이 문서의 강조색은 `--accent:#34d399` (에메랄드). `index.html` 카드에는 `--awsb:#34d399`로 넣는다.
- **커밋 규칙:** 태스크마다 1커밋. 커밋 전 반드시 검사 스크립트가 **exit 0**으로 통과해야 한다.
  - Task 2~18 (문서를 증분으로 채우는 동안): `python3 tools/check_tutorial.py --allow-missing-anchors aws_basics.html`
    히어로의 지도가 아직 만들지 않은 섹션을 가리키므로 앵커 검사만 유예한다. **다른 검사는 전부 적용된다.**
  - Task 19 이후 (모든 섹션이 존재): 플래그 없이 `python3 tools/check_tutorial.py aws_basics.html`
  - 어느 경우든 **exit 0이 게이트다.** `grep`으로 출력을 걸러 통과한 척하지 않는다.
- **건드리지 않을 것:** `aws_network_security.html` `https_tutorial.html` `iam_tutorial.html` `network_basics.html` `oauth2_tutorial.html` `rbac_tutorial.html`에 퇴고 중인 커밋되지 않은 변경이 있다. **어떤 태스크에서도 열지 않는다.** Task 1에서 골격을 복제할 때만 `aws_network_security.html`을 **읽기 전용으로** 연다. `index.html`은 Task 19에서 카드 추가만 얹는다.

---

## 파일 구조

| 파일 | 책임 | 태스크 |
|---|---|---|
| `aws_basics.html` | 산출물 본체. 18개 `<section>` (히어로 1 + 본문 15 + 부록 2) | Task 1~18, 20 |
| `index.html` | 시리즈 인덱스에 카드 1장 추가 | Task 19 |
| `docs/superpowers/notes/2026-08-15-aws-basics-known-issues.md` | 알고도 남긴 것 기록 | Task 20 |

### `aws_basics.html` 내부 구조

파일 안의 순서는 고정이다. 모든 태스크가 같은 자리에 끼워 넣는다.

```
<head>
  <style id="prism-theme">   … Task 1
  <style>                    … 디자인 시스템 (Task 1에서 완성, 이후 태스크는 장 전용 CSS만 append)
</head>
<body>
  <aside id="sidebar">       … Task 1
  <main id="content">
    <section id="intro">     … Task 2
    <section id="split">     … Task 3
    … (장 순서대로)
    <section id="appendix-map"> … Task 18
  </main>
  <aside id="glossary"> <div id="tooltip"> <div id="scrim">  … Task 1
  <script>Prism …</script>   … Task 1
  <script>
    const GLOSSARY = { … }   … Task 1에서 생성, 각 장 태스크가 항목 추가
    // @GLOSSARY_END
    유틸 · 학습 엔진          … Task 1
    /* 데모 N — 이름 */ IIFE  … 각 장 태스크가 파일 끝에 append
  </script>
</body>
```

### 섹션 id와 목차 번호

목차는 `data-title` 기준으로 자동 생성되며 첫 섹션은 `·`, 이후 1부터 매겨진다.

| # | id | data-title | 태스크 |
|---|---|---|---|
| · | `intro` | 개요 | 2 |
| 1 | `split` | 아홉 개로 쪼개졌다 | 3 |
| 2 | `account` | 계정 | 4 |
| 3 | `region` | 리전과 AZ | 5 |
| 4 | `arn` | ARN | 6 |
| 5 | `ec2` | EC2 인스턴스 | 7 |
| 6 | `ebs` | EBS | 8 |
| 7 | `eni` | ENI | 9 |
| 8 | `s3` | S3 | 10 |
| 9 | `entry` | 앞에 선 것들 | 11 |
| 10 | `managed` | 관리형 | 12 |
| 11 | `compute` | 어디에 올리나 | 13 |
| 12 | `cost` | 요금 | 14 |
| 13 | `doors` | 콘솔·CLI·API | 15 |
| 14 | `tag` | 태그와 IaC | 16 |
| 15 | `wrap` | 마무리 | 17 |
| 16 | `appendix-cli` | 부록 A · 진짜 명령어 | 18 |
| 17 | `appendix-map` | 부록 B · 다른 이름 | 18 |

### 퀴즈 id — 장마다 정확히 1개, 총 15개

`q-split` `q-account` `q-region` `q-arn` `q-ec2` `q-ebs` `q-eni` `q-s3` `q-entry` `q-managed` `q-compute` `q-cost` `q-doors` `q-tag` `q-wrap`

### 데모 컨테이너 id — 히어로 자가진단 + 14종

| 장 | 데모 | 루트 id | 입력 id | 출력 id |
|---|---|---|---|---|
| · | 자가진단 | `diag` | `.d-yes` | `diagResult` |
| 1 | 해체기 | `splitMap` | `splitPicker` | `splitOut` |
| 2 | 계정 경계 판정기 | `acctEval` | `acctPicker` | `acctOut` |
| 3 | 리전·AZ 지도 | `azMap` | `azPicker` | `azOut` |
| 4 | ARN 해부기 | `arnLab` | `arnPicker` | `arnOut` |
| 5 | 인스턴스 상태 기계 | `lifecycle` | `lifePicker` | `lifeOut` |
| 6 | 볼륨 수명 | `volLab` | `volPicker` | `volOut` |
| 7 | ENI 붙였다 떼기 | `eniLab` | `eniPicker` | `eniOut` |
| 8 | S3 vs EBS | `storeCmp` | `storePicker` | `storeOut` |
| 9 | 입구 고르기 | `entryPick` | `entryPicker` | `entryOut` |
| 10 | 책임 분계선 | `respLine` | `respPicker` | `respOut` |
| 11 | 세 갈래 선택기 | `computePick` | `computePicker` | `computeOut` |
| 12 | 요금 계산기 | `costCalc` | `costTogs` | `costOut` |
| 13 | 같은 일 세 가지 방법 | `doorCmp` | `doorPicker` | `doorOut` |
| 14 | 드리프트 | `driftSim` | `driftPicker` | `driftOut` |

### 히어로가 세우는 "아홉 개" — 문서 전체의 미결 목록

이 아홉 개가 Task 2에서 제시되고, Task 3의 해체기가 전부 담고, Task 17의 마무리가 회수한다.
**표기와 순서를 어느 태스크에서도 바꾸지 않는다.**

| # | 이름 | 정체를 밝히는 장 |
|---|---|---|
| 1 | EC2 인스턴스 | 5장 |
| 2 | EBS 루트 볼륨 | 6장 |
| 3 | ENI (네트워크 인터페이스) | 7장 |
| 4 | 보안 그룹 | 7장 (이름만 · 네트워크 보안 문서로 인계) |
| 5 | 키 페어 | 5장 |
| 6 | 서브넷 | 3장 · 7장 |
| 7 | 라우팅 테이블 | 9장 |
| 8 | 인터넷 게이트웨이 | 9장 |
| 9 | 탄력적 IP | 7장 · 12장 |

---

## Task 1: 골격 복제와 사장 CSS 제거

빌드 도구도 테스트 러너도 없는 저장소다. 3000줄짜리 단일 HTML을 열일곱 번 증분 편집하는 동안 "내가 뭘 깨뜨렸나"를 눈으로 확인하는 건 실패한다. `tools/check_tutorial.py`가 이 프로젝트의 테스트이고, 모든 태스크의 게이트다.

복제 원본이 CSS 클래스 **226개를 정의하고 96개만 쓴다**. 남은 130개는 IAM·네트워크 전용 컴포넌트라 이 문서에서 영영 안 쓰인다. 골격을 복제한 직후가 걷어낼 유일한 시점이다 — 장을 채우기 시작하면 무엇이 새로 쓰이는지 섞여서 판별이 안 된다.

**Files:**
- Create: `aws_basics.html`
- Read-only 참조: `aws_network_security.html`

**Interfaces:**
- Consumes: 없음
- Produces:
  - `aws_basics.html` — 이후 모든 태스크가 편집한다.
  - JS 전역: `$(sel, root?)` `$$(sel, root?)` → Element / Element[]; `LS.get(k, d)` `LS.set(k, v)` (접두어 `awsbase:`); `esc(s)` → string; `wirePicker(rootSel, onPick(k, btn))`; `wireTogs(rootSel, onChange(stateObj))` → stateObj; `updateProgress()`; `GLOSSARY` 객체(키: 용어 문자열, 값: 설명 문자열).
  - CSS 클래스: `.demo` `.demo-h` `.pick` `.tog` `.out` `.quiz` `.opt` `.explain` `.callout` `.myth` `.m-row` `.m-x` `.m-txt` `.kv` `.oneline` `.ol-ic` `.ol-t` `.ol-b` `.lvl` `.term` `.link` `.map-grid` `.diag` `.d-yes` `.ckl` `.dim` — 각 장 태스크가 이 이름들만 쓴다. 새 클래스가 필요하면 그 장의 `<style>` 블록에 추가하고 즉시 사용한다.

- [ ] **Step 1: 원본을 복사한다**

```bash
cd /Users/narusas/Dropbox/Mac/Documents/study/publish-doc
cp aws_network_security.html aws_basics.html
```

이후 `aws_network_security.html`은 **다시 열지 않는다.** 그 파일에는 커밋되지 않은 퇴고 변경이 얹혀 있다.

- [ ] **Step 2: 저장소 키를 바꾼다**

`aws_basics.html`에서 `netsec:` 세 군데를 전부 `awsbase:`로 바꾼다.

```bash
python3 - <<'PY'
import re, pathlib
p = pathlib.Path('aws_basics.html')
s = p.read_text(encoding='utf-8')
n = s.count('netsec:')
s = s.replace('netsec:', 'awsbase:')
p.write_text(s, encoding='utf-8')
print('replaced', n)
PY
```

Expected: `replaced 3`

- [ ] **Step 3: 바뀌었는지 확인한다**

```bash
grep -c 'netsec:' aws_basics.html; grep -c 'awsbase:' aws_basics.html
```

Expected: `0` 그리고 `3`. `netsec:`이 하나라도 남으면 두 문서가 진행률을 공유해 서로를 덮어쓴다.

- [ ] **Step 4: 메타와 제목을 바꾼다**

`<title>`과 `meta description`을 교체한다.

```html
<title>AWS 기초 튜토리얼 — 서버 한 대가 아홉 개로 쪼개지는 이야기</title>
<meta name="description" content="서버 한 대를 빌린 줄 알았는데 리소스가 아홉 개 생겨 있었다에서 출발하는 AWS 기초 인터랙티브 튜토리얼. 계정·리전·AZ·ARN·EC2·EBS·ENI·S3가 왜 따로 떨어져 있는지, 그 부품으로 어떻게 서비스를 짓는지 직접 눌러 확인합니다.">
```

- [ ] **Step 5: 색을 바꾼다**

`:root` 블록에서 강조색과 축 색을 교체한다. 로즈 계열(`--accent:#fb7185` / `--accent-2:#f472b6`)과 관문 고정색(`--g-route` `--g-nacl` `--g-sg` `--g-fw` `--g-waf` `--g-os`) 여섯 개를 지우고 아래로 대체한다.

```css
  --accent:    #34d399;   /* 메인(에메랄드) */
  --accent-2:  #22d3ee;   /* 보조(시안) */

  /* 수명 축 — 5·6·7장의 모든 데모에서 동일하게 사용 */
  --keep:      #34d399;   /* 살아남는다 */
  --gone:      #f87171;   /* 사라진다 */
  --fresh:     #fbbf24;   /* 새로 받는다 (값이 바뀐다) */

  /* 책임 축 — 10·11장 */
  --own-me:    #f472b6;   /* 내가 진다 */
  --own-aws:   #38bdf8;   /* AWS가 진다 */
```

`--keep`과 `--ok`가 같은 값인 것은 의도한 것이다. 이 문서에서 "살아남는다"는 곧 좋은 소식이다.

- [ ] **Step 6: 본문과 데모를 비운다**

`<main id="content">`와 `</main>` 사이를 통째로 지우고, `<script>` 안의 `/* ====== 데모 1 …` 주석부터 파일 끝의 `</script>` 직전까지(모든 데모 IIFE)를 지운다. `GLOSSARY` 객체는 **빈 객체로 만들되 `// @GLOSSARY_END` 마커는 남긴다.**

```js
const GLOSSARY = {
  // @GLOSSARY_END
};
```

`유틸 · 학습 엔진` 블록(`const $ = …`부터 `초기 렌더` 끝까지)은 **한 줄도 건드리지 않는다.**

- [ ] **Step 7: 사이드바 제목과 히어로 자리를 채운다**

`<aside id="sidebar">` 안의 문서 제목을 "AWS 기초"로 바꾼다. `<main>` 안에는 검사기를 통과시킬 최소 섹션 하나만 둔다.

```html
<main id="content">
  <section id="intro" data-title="개요" class="hero">
    <h1>서버 한 대를 주문했는데</h1>
  </section>
</main>
```

- [ ] **Step 8: 검사기를 돌린다 — 통과해야 한다**

Run: `python3 tools/check_tutorial.py --allow-missing-anchors aws_basics.html; echo "exit=$?"`
Expected: `OK aws_basics.html (섹션 1 · 퀴즈 0 · 데모 0)` 그리고 `exit=0`

퀴즈 0·데모 0인데 통과하는 게 맞다. 검사기는 개수의 하한을 두지 않고 **정합성**만 본다.

- [ ] **Step 9: 사장 CSS의 기준선을 잰다**

Run: `python3 tools/check_dead_css.py aws_basics.html`
Expected: `FAIL aws_basics.html: 정의 226 · 사용 N · 미사용 M` 형태. 본문을 비웠으므로 미사용이 130보다 크게 나온다. **출력 전체를 파일로 남긴다.**

```bash
python3 tools/check_dead_css.py aws_basics.html > /tmp/dead-before.txt 2>&1 || true
```

- [ ] **Step 10: 이 문서에서 안 쓸 컴포넌트를 걷어낸다**

`/tmp/dead-before.txt`의 목록에서 **아래 접두어에 해당하는 CSS 규칙 블록을 지운다.** 전부 IAM·네트워크 보안 전용이라 이 문서에 다시 나타나지 않는다.

- `.ar-*` `.ac-*` (AssumeRole 애니메이션)
- `.ev-*` (관문 파이프라인)
- `.esc-*` (권한 상승 사다리)
- `.ladder` `.tag-card` `.tag-eq` `.tag-lab` `.tag-row`
- `.tcp` `.tc-h` `.ack` `.synack` (TCP 핸드셰이크 도해)
- `.terminal` `.term-box` `.term-input-row` `.term-prompt` `.term-screen` (가짜 터미널 — 부록 A는 `<pre>`+Prism으로 간다)
- `.tuple-layout` `.tog-col` `.am-*` `.tk` `.tv` `.tg-t`

**남길 것**: Global Constraints의 Produces 목록에 있는 클래스 전부. `.wrap` `.tight` `.dim` 같은 유틸도 남긴다 — 이름은 짧아도 본문에서 곧 쓴다.

지울지 말지 애매하면 **남긴다.** 사장 CSS는 게시를 막지 않지만 실수로 지운 규칙은 레이아웃을 깨뜨린다.

- [ ] **Step 11: 줄어들었는지 확인한다**

Run: `python3 tools/check_dead_css.py aws_basics.html`
Expected: 미사용 개수가 Step 9보다 **최소 60 이상 줄어 있다.** 여전히 `FAIL`인 것은 정상이다 — 본문이 비어 있으니 아직 대부분이 미사용이다. 이 검사기는 **보고용이고 게이트가 아니다.** (exit 1을 낸다)

- [ ] **Step 12: 검사기를 다시 돌린다 — CSS를 지우다 마크업을 건드리지 않았는지**

Run: `python3 tools/check_tutorial.py --allow-missing-anchors aws_basics.html; echo "exit=$?"`
Expected: `exit=0`

- [ ] **Step 13: 브라우저로 연다**

`file://` 로 `aws_basics.html`을 열어 확인한다.
- 사이드바가 뜨고 목차에 `· 개요` 한 줄이 있다
- 개발자도구 Network 탭에 **외부 요청 0건**
- 콘솔에 에러 0건
- 용어사전 버튼을 누르면 빈 드로어가 열리고 닫힌다

- [ ] **Step 14: 커밋**

```bash
git add aws_basics.html
git commit -m "AWS 기초: 골격 복제와 사장 CSS 정리

aws_network_security.html의 뼈대를 복제하고 저장소 키를 awsbase:로 갈랐다.
복제하면 딸려 오는 IAM·네트워크 전용 CSS를 걷어냈다 — 장을 채우기 시작하면
무엇이 새로 쓰이는지 섞여서 판별이 안 되므로 지금이 유일한 시점이다."
```

---

## Task 2: 히어로 — 한 대를 주문했는데 아홉 개가 생겼다

**Files:**
- Modify: `aws_basics.html` (`<section id="intro">` 교체, 스크립트 끝에 자가진단 IIFE 추가, GLOSSARY 항목 추가)

**Interfaces:**
- Consumes: Task 1의 `$` `$$` `LS` `wirePicker` `GLOSSARY`
- Produces: `#diag` 자가진단(Task 17의 마무리가 회수한다), 아홉 개 목록의 표기와 순서(Task 3·17이 그대로 쓴다), `.map-grid` 지도 링크 17개(Task 20의 앵커 검사가 전부 해석돼야 한다)

- [ ] **Step 1: 히어로 마크업을 쓴다**

`<section id="intro" data-title="개요" class="hero">`의 내용을 아래 순서로 채운다.

1. **제목과 도입.** 김주임이 "서버 한 대"를 주문했고, 콘솔의 리소스 목록에는 아홉 줄이 생겼다는 장면. 마지막 문장은 열린 채로 둔다 — 왜 아홉인지 여기서 답하지 않는다.
2. **아홉 개 목록.** `.kv`로 낸다. 이 계획서 "히어로가 세우는 아홉 개" 표의 이름과 순서 그대로. 각 항목에 **한 줄짜리 정체 힌트만** 붙이고 설명하지 않는다.
3. **무대 소개.** `.persona` 하나 — 김주임(개발자, 입사 3개월, 첫 서비스 배포). 박팀장·이보안은 이름만 스치듯. `iam_tutorial.html`과 같은 인물이라는 것을 밝힌다.
4. **30초 자가진단** `#diag`.
5. **지도** `.map-grid` — 17개 섹션으로 가는 링크. `href`는 `#split` `#account` `#region` `#arn` `#ec2` `#ebs` `#eni` `#s3` `#entry` `#managed` `#compute` `#cost` `#doors` `#tag` `#wrap` `#appendix-cli` `#appendix-map`.
6. **읽는 법.** 1부는 해체, 2부는 조립. 🟢/🔵 표시의 뜻.

**쓰지 말 것**: "이 문서에서는 A, B, C를 다룹니다" 형태의 태도 없는 의제 목록. 지도는 링크 그리드이지 문장이 아니므로 이 금지에 걸리지 않는다.

- [ ] **Step 2: 자가진단 문항을 쓴다**

`.d-yes` 버튼 여섯 개. `data-w`는 가중치다.

```html
<div id="diag" class="diag">
  <button class="d-yes" data-w="3">EC2를 띄워는 봤는데, 왜 그 화면이 나한테 서브넷을 고르라고 했는지는 모른다</button>
  <button class="d-yes" data-w="3">인스턴스를 지웠는데 다음 달 청구서에 스토리지 요금이 남아 있었다</button>
  <button class="d-yes" data-w="2">서버를 껐다 켰더니 접속하던 IP가 바뀌어 있었다</button>
  <button class="d-yes" data-w="2">S3와 EBS 중 무엇을 써야 하는지 물으면 대답이 막힌다</button>
  <button class="d-yes" data-w="1">ARN을 복사해 붙여는 넣지만 그 문자열의 칸이 무슨 뜻인지는 모른다</button>
  <button class="d-yes" data-w="1">리전을 잘못 골라서 만든 리소스가 안 보였던 적이 있다</button>
</div>
<div id="diagResult" class="out"></div>
```

- [ ] **Step 3: 자가진단 IIFE를 스크립트 끝에 붙인다**

```js
/* ============================================================
   데모 0 — 히어로 자가진단
   ============================================================ */
(function(){
  const diag = $('#diag'); if(!diag) return;
  const res = $('#diagResult');
  function update(){
    const on = $$('.d-yes.on', diag);
    const score = on.reduce((s,x)=>s+(+x.dataset.w), 0);
    let msg;
    if(score===0) msg = "해당하는 항목을 눌러보세요. 하나도 없다면 구성은 이미 손에 잡혀 있는 겁니다 — <b>9장(앞에 선 것들)</b>과 <b>11장(어디에 올리나)</b>부터 골라 읽어도 좋아요.";
    else if(score>=8) msg = "<b>🟢 1장부터 순서대로가 빠릅니다.</b> 콘솔을 눌러 본 적은 있지만 무엇이 무엇인지가 아직 흩어져 있는 상태예요. <b>1장(해체) → 3장(리전·AZ) → 5·6·7장(EC2·EBS·ENI)</b>이 이 문서의 척추입니다.";
    else if(score>=4) msg = "<b>🟢 부품 이름은 아는 단계네요.</b> 그렇다면 <b>5장(인스턴스는 서버가 아니다)</b>과 <b>6장(디스크가 따로 노는 이유)</b>, 그리고 <b>12장(안 쓰는데 돈이 나간다)</b>이 가장 값을 합니다.";
    else msg = "<b>🔵 기초는 갖춰져 있습니다.</b> <b>9장(앞에 선 것들)</b>·<b>10장(관리형)</b>·<b>14장(태그와 IaC)</b> 같은 조립 쪽부터 보셔도 좋아요.";
    res.innerHTML = msg + ` <span class="dim">(체크 ${on.length}개 · 가중치 ${score})</span>`;
    res.classList.add('show');
  }
  $$('.d-yes', diag).forEach(b => b.addEventListener('click', () => { b.classList.toggle('on'); update(); }));
})();
```

- [ ] **Step 4: GLOSSARY에 첫 항목을 넣는다**

```js
const GLOSSARY = {
  "리소스": "AWS에서 만들고 지우는 것 하나하나. 인스턴스도, 볼륨도, 네트워크 인터페이스도 각각 별개의 리소스이고 각각 따로 과금됩니다.",
  "콘솔": "브라우저로 쓰는 AWS 관리 화면. 13장에서 보듯 콘솔이 하는 일은 결국 API 호출이라, 콘솔에서 되는 것은 전부 자동화할 수 있습니다.",
  // @GLOSSARY_END
};
```

본문에서 이 두 단어를 처음 쓸 때 `<span class="term" data-t="리소스">리소스</span>` 형태로 감싼다. **감싼 용어는 반드시 GLOSSARY에 있어야 한다 — 없으면 검사기가 FAIL한다.**

- [ ] **Step 5: 검사기를 돌린다**

Run: `python3 tools/check_tutorial.py --allow-missing-anchors aws_basics.html; echo "exit=$?"`
Expected: `OK aws_basics.html (섹션 1 · 퀴즈 0 · 데모 0)` · `exit=0`

앵커 유예를 빼면 `#split` 이하 17개가 전부 없어서 FAIL한다. 정상이다.

- [ ] **Step 6: 브라우저로 확인한다**

- 자가진단 버튼 여섯 개가 눌리고, 누를 때마다 문구와 `(체크 N개 · 가중치 M)`이 갱신된다
- 하나도 안 누른 상태에서는 결과가 뜨지 않는다
- 지도의 링크를 누르면 아직 아무 데도 가지 않는다(섹션이 없으므로) — 콘솔 에러는 없어야 한다

- [ ] **Step 7: 커밋**

```bash
git add aws_basics.html
git commit -m "히어로: 한 대를 주문했는데 아홉 개가 생겼다

아홉 개 목록이 문서 전체의 미결 목록이 된다. 여기서는 이름과 한 줄 힌트만
놓고 정체를 밝히지 않는다. 무대는 iam_tutorial의 나루 클라우드를 그대로
쓰되 김주임의 첫 배포로 시계를 되감았다."
```

---

## Task 3: 1장 · 아홉 개의 정체 — 왜 쪼개 놓았나 🟢

**근거 읽기**: 없음(이 장은 개념 프레이밍이다). 단, 뒤 장을 미리 당겨 쓰지 않는다 — 각 조각의 상세는 해당 장에 있다.

**Files:**
- Modify: `aws_basics.html`

**Interfaces:**
- Consumes: Task 2의 아홉 개 목록(같은 이름·같은 순서)
- Produces: `#splitMap` 해체기 — Task 17의 마무리가 같은 아홉 개를 회수한다. `D9` 데이터 객체의 키 아홉 개(`ec2` `ebs` `eni` `sg` `key` `subnet` `rtb` `igw` `eip`)는 Task 17이 그대로 참조한다.

- [ ] **Step 1: 절 진입을 쓴다**

첫머리는 독자가 품을 반문으로 연다 — "한 대를 빌렸는데 왜 아홉 개인가. 하나로 묶어 두면 안 되나." 반문에 즉답하지 않고 일단 받아 준 뒤, 온프렘 서버 한 대에서는 그 아홉이 **한 몸이었다**는 사실로 넘어간다.

쪼갠 이유는 셋이고, 각각을 아홉 개 중 구체적인 하나에 착지시킨다.

1. **수명을 따로 두려고** — 인스턴스를 지워도 볼륨은 남길 수 있다(6장에서 조건을 본다)
2. **값을 따로 매기려고** — 꺼 둔 인스턴스에는 요금이 안 붙지만 그 디스크에는 붙는다(12장)
3. **다시 조립하려고** — 같은 ENI를 다른 인스턴스에 붙일 수 있다(7장)

- [ ] **Step 2: 해체기 마크업**

```html
<div class="demo" id="splitMap">
  <div class="demo-h">🧩 서버 한 대를 눌러 해체해 보세요</div>
  <div class="pick-row" id="splitPicker">
    <button class="pick" data-k="ec2">EC2 인스턴스</button>
    <button class="pick" data-k="ebs">EBS 루트 볼륨</button>
    <button class="pick" data-k="eni">ENI</button>
    <button class="pick" data-k="sg">보안 그룹</button>
    <button class="pick" data-k="key">키 페어</button>
    <button class="pick" data-k="subnet">서브넷</button>
    <button class="pick" data-k="rtb">라우팅 테이블</button>
    <button class="pick" data-k="igw">인터넷 게이트웨이</button>
    <button class="pick" data-k="eip">탄력적 IP</button>
  </div>
  <div class="out" id="splitOut"></div>
</div>
```

- [ ] **Step 3: 해체기 IIFE**

각 조각은 네 축을 갖는다 — `was`(온프렘에서는 무엇이었나) · `life`(수명) · `bill`(과금) · `ch`(어느 장에서 다루나). **`bill` 값은 12장(Task 14)과 어긋나면 안 된다.**

```js
/* ============================================================
   데모 1 — 해체기 (1장)
   ============================================================ */
(function(){
  const out = $('#splitOut'); if(!out) return;
  const D9 = {
    ec2:    {n:"EC2 인스턴스", was:"본체 — CPU와 메모리", life:"terminate하면 사라진다", bill:"켜 둔 시간만큼", ch:"5장"},
    ebs:    {n:"EBS 루트 볼륨", was:"안에 꽂힌 디스크", life:"인스턴스를 지워도 남을 수 있다", bill:"켜져 있든 꺼져 있든 크기만큼", ch:"6장"},
    eni:    {n:"ENI", was:"랜카드", life:"인스턴스와 따로 살고 따로 죽는다", bill:"그 자체는 무료", ch:"7장"},
    sg:     {n:"보안 그룹", was:"방화벽 설정 파일", life:"인스턴스와 무관하게 존재한다", bill:"무료", ch:"7장에서 이름만"},
    key:    {n:"키 페어", was:"서버실 열쇠", life:"만들 때 받은 개인키는 다시 못 받는다", bill:"무료", ch:"5장"},
    subnet: {n:"서브넷", was:"랙이 놓인 층", life:"AZ 하나에 갇혀 옮길 수 없다", bill:"무료", ch:"3장 · 7장"},
    rtb:    {n:"라우팅 테이블", was:"스위치의 경로 설정", life:"서브넷에 붙였다 뗄 수 있다", bill:"무료", ch:"9장"},
    igw:    {n:"인터넷 게이트웨이", was:"건물 밖으로 나가는 회선", life:"VPC에 하나 붙는다", bill:"게이트웨이 자체는 무료", ch:"9장"},
    eip:    {n:"탄력적 IP", was:"고정 공인 IP 한 개", life:"놓아주기 전까지 내 것이다", bill:"쥐고 있는 동안 시간당", ch:"7장 · 12장"}
  };
  function render(k){
    const d = D9[k]; if(!d) return;
    out.innerHTML = `
      <div class="kv">
        <dt>온프렘에서는</dt><dd>${esc(d.was)}</dd>
        <dt>수명</dt><dd>${esc(d.life)}</dd>
        <dt>요금</dt><dd>${esc(d.bill)}</dd>
        <dt>정체를 밝히는 곳</dt><dd>${esc(d.ch)}</dd>
      </div>`;
    out.classList.add('show');
  }
  wirePicker('#splitPicker', render);
})();
```

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-split" data-answer="c">
  <div class="q">아홉 개로 쪼개 놓아서 <b>생기는 일</b>은 무엇일까요?</div>
  <button class="opt" data-opt="a">관리할 것이 늘어나는 대신 성능이 좋아진다</button>
  <button class="opt" data-opt="b">한 번에 만들고 한 번에 지울 수 있게 된다</button>
  <button class="opt" data-opt="c">각 조각의 수명과 요금이 서로 독립해진다</button>
  <button class="opt" data-opt="d">보안 경계가 조각 수만큼 늘어난다</button>
  <div class="explain">…</div>
</div>
```

해설에 넣을 것: C가 정답이고 셋으로 갈라 쓴다 — 수명이 독립하니 인스턴스를 지워도 볼륨이 남고(6장), 요금이 독립하니 꺼 둔 서버에도 디스크 값이 나가고(12장), 조립이 독립하니 같은 ENI를 다른 인스턴스에 붙인다(7장). B가 가장 흔한 오답인데 **정확히 반대**다 — 쪼갠 대가로 한 번에 지우는 게 어려워졌고, 그 어려움을 메우려고 나온 것이 14장의 IaC다. A는 쪼갬이 성능과 무관하다는 점에서, D는 보안 경계가 조각 수가 아니라 계정·VPC·ENI라는 정해진 자리에 붙는다는 점에서 틀렸다.

- [ ] **Step 5: GLOSSARY 추가**

`"인스턴스"` `"볼륨"` `"온프렘"` 세 항목. 본문에서 처음 쓸 때 `.term`으로 감싼다.

- [ ] **Step 6: 검사기**

Run: `python3 tools/check_tutorial.py --allow-missing-anchors aws_basics.html; echo "exit=$?"`
Expected: `OK aws_basics.html (섹션 2 · 퀴즈 1 · 데모 1)` · `exit=0`

- [ ] **Step 7: 브라우저 확인**

아홉 버튼이 전부 눌리고 `.kv` 네 줄이 갱신된다. 퀴즈에서 오답을 누르면 정답에 표시가 뜨고 해설이 열린다. 새로고침해도 푼 기록이 남는다.

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "1장: 아홉 개의 정체 — 왜 쪼개 놓았나

쪼갠 이유 셋을 각각 아홉 개 중 하나에 착지시킨다. 해체기의 요금 축은
12장과 같은 값을 말해야 하므로 여기서 정한 문구를 12장이 따른다."
```

---

## Task 4: 2장 · 계정 — 모든 것이 담기는 그릇 🟢

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 3의 `.term` 관례
- Produces: "계정은 격리 단위이자 청구 단위"라는 문장 — Task 12(10장 책임 분계)와 Task 14(12장 요금)가 되받는다

- [ ] **Step 1: 절 진입**

1장이 아홉 개를 흩어 놓았으니, 그 아홉이 **어디에 담겨 있는지**를 묻는 것으로 연다. 답의 절반만 먼저 준다 — 계정 하나에 담겨 있다. 나머지 절반(그래서 무엇이 달라지나)은 데모 뒤에 채운다.

핵심 셋:
- 리소스는 반드시 계정 하나에 속한다. 계정을 옮길 수 없다.
- 계정은 **청구 단위**다. 청구서는 계정마다 나온다.
- 계정이 다르면 기본은 서로 보이지 않는다. 넘어가려면 **양쪽이 다 허락해야 한다** — 상세는 `iam_tutorial.html`로 인계한다.

루트 계정은 "만들 때 쓴 이메일로 로그인하는 그것"까지만. 권한 이야기는 IAM 문서의 몫이다.

- [ ] **Step 2: 계정 경계 판정기**

```html
<div class="demo" id="acctEval">
  <div class="demo-h">🪣 이 일이 계정 경계를 넘을 수 있을까요</div>
  <div class="pick-row" id="acctPicker">
    <button class="pick" data-k="s3">dev 계정의 EC2가 prod 계정의 S3 버킷을 읽는다</button>
    <button class="pick" data-k="name">dev와 prod가 같은 이름의 S3 버킷을 각각 만든다</button>
    <button class="pick" data-k="move">dev 계정의 EC2 인스턴스를 prod 계정으로 옮긴다</button>
    <button class="pick" data-k="bill">두 계정의 요금을 한 장의 청구서로 받는다</button>
    <button class="pick" data-k="az">dev의 ap-northeast-2a와 prod의 ap-northeast-2a가 같은 건물이다</button>
  </div>
  <div class="out" id="acctOut"></div>
</div>
```

- [ ] **Step 3: 판정기 IIFE**

`az` 항목의 답은 3장(Task 5)에서 근거와 함께 밝힌다. 여기서는 **아니오**라고만 답하고 이유는 다음 장으로 넘긴다 — 이것이 2장이 남기는 미결이다.

```js
/* ============================================================
   데모 2 — 계정 경계 판정기 (2장)
   ============================================================ */
(function(){
  const out = $('#acctOut'); if(!out) return;
  const D = {
    s3:   {v:"조건부", c:"warn", t:"넘을 수 있지만 <b>양쪽이 다 허락해야</b> 합니다. 보내는 계정이 \"가도 좋다\"고 하고, 받는 계정이 \"와도 좋다\"고 해야 통과해요. 한쪽만 열면 아무 일도 일어나지 않습니다. 그 두 문의 정체는 <a class=\"link\" href=\"iam_tutorial.html\">IAM 튜토리얼</a>이 다룹니다."},
    name: {v:"아니오", c:"bad", t:"S3 버킷 이름은 계정 안에서가 아니라 <b>훨씬 넓은 범위에서 유일</b>해야 합니다. 남이 먼저 쓴 이름은 내 계정에서도 못 씁니다. 얼마나 넓은 범위인지는 <a class=\"link\" href=\"#s3\">8장</a>에서 정확히 봅니다."},
    move: {v:"아니오", c:"bad", t:"인스턴스는 계정을 옮길 수 없습니다. 옮기려면 <b>AMI로 떠서 공유한 뒤 저쪽에서 새로 띄우는</b> 것뿐이고, 그건 옮긴 게 아니라 <b>새로 만든 것</b>입니다. ID도 바뀌고 <a class=\"link\" href=\"#arn\">ARN</a>도 바뀝니다."},
    bill: {v:"예", c:"ok", t:"계정을 조직으로 묶으면 청구를 한곳으로 모을 수 있습니다. <b>격리는 그대로 두고 청구만 합치는</b> 겁니다 — 두 성질이 따로 논다는 게 여기서 드러나요."},
    az:   {v:"아니오", c:"bad", t:"같은 이름인데 <b>다른 건물</b>일 수 있습니다. 왜 그런지는 <a class=\"link\" href=\"#region\">바로 다음 장</a>에서 실제 출력을 놓고 봅니다."}
  };
  function render(k){
    const d = D[k]; if(!d) return;
    out.innerHTML = `<div class="verdict ${d.c}">${d.v}</div><p>${d.t}</p>`;
    out.classList.add('show');
  }
  wirePicker('#acctPicker', render);
})();
```

`.verdict` 클래스가 Task 1에서 남긴 목록에 없다면 이 장의 `<style>` 블록에 추가한다.

```css
.verdict{display:inline-block; font-weight:800; font-size:13px; letter-spacing:.5px;
  border-radius:8px; padding:4px 12px; margin-bottom:10px;}
.verdict.ok{color:var(--ok); border:1px solid var(--ok); background:rgba(52,211,153,.10)}
.verdict.warn{color:var(--warn); border:1px solid var(--warn); background:rgba(251,191,36,.10)}
.verdict.bad{color:var(--bad); border:1px solid var(--bad); background:rgba(248,113,113,.10)}
```

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-account" data-answer="b">
  <div class="q">계정을 <b>둘로 나누면</b> 따라오는 것은 무엇일까요?</div>
  <button class="opt" data-opt="a">리소스를 두 계정에 나눠 담아도 요금은 항상 따로 청구된다</button>
  <button class="opt" data-opt="b">한쪽에서 실수로 지운 것이 다른 쪽에 닿지 않는다</button>
  <button class="opt" data-opt="c">같은 이름의 S3 버킷을 각각 만들 수 있게 된다</button>
  <button class="opt" data-opt="d">리소스를 계정 사이로 옮길 수 있게 된다</button>
</div>
```

해설: B가 정답. 계정은 이 문서에 나오는 어떤 경계보다 단단하다. A는 격리와 청구가 따로 논다는 점에서 틀렸고(조직으로 묶으면 청구는 합쳐진다), C는 8장이 다룰 유일성 범위 때문에 틀렸고, D는 정반대다 — 나눌수록 옮기기 어려워진다.

- [ ] **Step 5: GLOSSARY** — `"계정"` `"루트 사용자"` `"AMI"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 3 · 퀴즈 2 · 데모 2` · `exit=0`

- [ ] **Step 7: 브라우저 확인** — 다섯 항목이 각각 다른 판정을 내고, `#s3` `#region` `#arn`로 가는 링크는 아직 목적지가 없다(Task 20에서 전부 해석된다)

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "2장: 계정 — 모든 것이 담기는 그릇

격리와 청구가 같은 단위에 걸려 있으면서도 따로 뗄 수 있다는 것이 이 장의
핵심이다. AZ 이름 항목은 답만 주고 이유를 3장으로 넘겨 미결로 남긴다."
```

---

## Task 5: 3장 · 리전과 AZ — 왜 자꾸 어디냐고 묻는가 🟢

**근거 읽기**: facts **V6**. `ap-northeast-2a`가 계정마다 다른 건물이라는 것과, 공식 문서의 실제 CLI 출력 표(us-west-2a→usw2-az2).

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 4가 남긴 미결(같은 AZ 이름이 다른 건물인 이유)
- Produces: "서브넷은 AZ에 갇힌다" — Task 9(7장)와 Task 11(9장)이 회수한다

- [ ] **Step 1: 절 진입 — 앞 장의 미결을 당사자의 질문으로 되받는다**

"같은 `ap-northeast-2a`인데 다른 건물이라니, 이름이 다르면 될 일 아닌가." 반문을 그대로 쓰고 받아 준 뒤 무너뜨린다.

이 장이 세울 것:
- **리전은 서로 격리된 별개의 세계다.** 서울에서 만든 것은 도쿄 콘솔에 없다. 리소스가 안 보인다는 문의의 대부분이 이것이다.
- **AZ는 리전 안의 독립된 위치**이고, 서브넷은 AZ 하나에 갇힌다.
- **글로벌인 것들의 예외** — S3 버킷 이름(8장에서 정확히), IAM, CloudFront, Route 53.

- [ ] **Step 2: 오해 격파 — AZ 이름은 계정마다 다르게 매핑된다**

`.myth` 상자로 낸다. facts V6의 인용을 근거로 삼되 **원문을 그대로 번역해 옮기고, 없는 말을 보태지 않는다.**

핵심 세 줄:
1. AWS는 물리 AZ를 계정마다 **무작위로** 이름에 매핑한다.
2. 그래서 내 `us-east-1a`와 남의 `us-east-1a`가 다른 곳일 수 있다.
3. 계정을 넘어 같은 곳을 가리키려면 **AZ ID**(`use1-az1`)를 쓴다.

섞은 이유까지 적는다 — 모두가 `a`에 몰리는 것을 막으려고. 이유를 알면 외울 필요가 없어진다.

- [ ] **Step 3: 리전·AZ 지도 데모**

`azPicker`로 리전을 고르면 그 리전의 AZ 목록과 **이름↔ID 매핑**을 보여 준다. `us-west-2`는 facts V6에 확보한 **공식 문서의 실제 출력**을 그대로 쓴다. 다른 리전은 매핑을 지어내지 않는다 — "이 계정에서는 이렇게 나온다"는 예시가 아니라 **확인된 출력 하나**만 진짜로 쓰고, 나머지 리전은 AZ 개수와 코드만 보여 준다.

```js
/* ============================================================
   데모 3 — 리전·AZ 지도 (3장)
   ============================================================ */
(function(){
  const out = $('#azOut'); if(!out) return;
  // us-west-2의 매핑은 AWS 공식 문서의 describe-availability-zones 출력 그대로다.
  // 다른 리전의 매핑은 계정마다 다르므로 지어내지 않는다.
  const REAL = [
    {name:"us-west-2a", id:"usw2-az2"},
    {name:"us-west-2b", id:"usw2-az1"},
    {name:"us-west-2c", id:"usw2-az3"},
    {name:"us-west-2d", id:"usw2-az4"}
  ];
  const D = {
    usw2: {t:"US West (Oregon) · us-west-2", real:true,
           note:"AWS 공식 문서에 실린 실제 출력입니다. <b>a가 az1이 아닙니다.</b> 이 계정에서는 <code>us-west-2b</code>가 <code>usw2-az1</code>이에요. 다른 계정에서 같은 명령을 치면 다르게 나옵니다."},
    apne2:{t:"Asia Pacific (Seoul) · ap-northeast-2", real:false,
           note:"이 리전의 매핑도 계정마다 다릅니다. 내 계정의 매핑은 <code>aws ec2 describe-availability-zones</code>로 직접 확인해야 하고, 그게 이 데모가 서울 리전의 값을 지어내지 않는 이유입니다."},
    global:{t:"리전이 없는 것들", real:false,
           note:"IAM · CloudFront · Route 53은 리전을 고르지 않습니다. S3는 버킷을 리전에 만들지만 <b>이름만은 리전을 넘어 유일</b>해야 해요 — 얼마나 넓은 범위인지는 <a class=\"link\" href=\"#s3\">8장</a>에서 봅니다."}
  };
  function render(k){
    const d = D[k]; if(!d) return;
    let html = `<div class="kv"><dt>대상</dt><dd>${d.t}</dd></div>`;
    if(d.real){
      html += '<table class="az-t"><thead><tr><th>ZoneName (계정마다 다름)</th><th>ZoneId (모든 계정 공통)</th></tr></thead><tbody>';
      REAL.forEach(z => { html += `<tr><td><code>${z.name}</code></td><td><code>${z.id}</code></td></tr>`; });
      html += '</tbody></table>';
    }
    html += `<p>${d.note}</p>`;
    out.innerHTML = html; out.classList.add('show');
  }
  wirePicker('#azPicker', render);
})();
```

`.az-t` 스타일을 이 장의 `<style>`에 추가한다.

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-region" data-answer="d">
  <div class="q">동료가 "우리 서비스를 <code>ap-northeast-2a</code>에 몰아 두지 말고 <code>2a</code>와 <code>2c</code>에 나누자"고 합니다. 여기서 <b>틀린 것</b>은?</div>
  <button class="opt" data-opt="a">AZ를 나누면 한 곳이 죽어도 다른 곳이 산다는 기대</button>
  <button class="opt" data-opt="b">서브넷을 AZ마다 따로 만들어야 한다는 전제</button>
  <button class="opt" data-opt="c">두 AZ가 같은 리전 안에 있다는 전제</button>
  <button class="opt" data-opt="d">동료의 2a와 내 2a가 같은 건물이라는 전제</button>
</div>
```

해설: D. 계정이 다르면 같은 이름이 다른 곳을 가리킬 수 있고, 계정을 넘어 위치를 맞추려면 AZ ID를 쓴다. A·B·C는 전부 맞는 말이라 오답이다 — **틀린 것을 고르는 문제**라는 점을 해설 첫 줄에 밝혀 준다. B는 7장에서, C는 이 장에서 이미 세웠다.

- [ ] **Step 5: GLOSSARY** — `"리전"` `"가용 영역"` `"AZ ID"` `"서브넷"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 4 · 퀴즈 3 · 데모 3` · `exit=0`

- [ ] **Step 7: 브라우저 확인** — `usw2`를 고르면 표에 네 줄이 뜨고 `a`가 `az2`인 것이 보인다

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "3장: 리전과 AZ — 왜 자꾸 어디냐고 묻는가

AZ 이름의 무작위 매핑은 공식 문서의 실제 출력을 그대로 쓴다. 다른 리전의
매핑은 계정마다 다르므로 지어내지 않고, 직접 확인하는 명령만 알려 준다."
```

---

## Task 6: 4장 · ARN — AWS가 물건을 세는 법 🟢

**근거 읽기**: facts **V11**. 네 개의 실제 ARN 예시와 "파티션 개수는 쓰지 않는다"는 제약.

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 5의 "글로벌인 것들"
- Produces: ARN 문법 — Task 15(13장)의 API 호출과 `iam_tutorial.html` 인계의 발판

- [ ] **Step 1: 절 진입 — 고백으로 연다**

"솔직히 말하면 나도 한동안 ARN을 복사해 붙여 넣기만 했다"는 식의 고백. 자기비판이 아니라 바로 뒤 논증의 발판이다 — 그 문자열의 **빈 칸에 뜻이 있다**는 것.

- [ ] **Step 2: 문법을 놓는다**

```
arn:파티션:서비스:리전:계정:리소스
```

각 칸을 한 줄씩. **파티션은 개수를 숫자로 쓰지 않는다** — 공식 문서 두 곳이 셋과 넷으로 어긋나 있다(facts V11). "중국과 GovCloud는 별도 파티션"까지만 쓴다.

이름과 ID의 차이도 여기서 짚는다. 콘솔이 보여 주는 이름과 API가 쓰는 `i-0abc…`는 다른 것이다.

- [ ] **Step 3: ARN 해부기**

네 예시는 전부 facts V11에 확보한 공식 문서의 것이다. **지어내지 않는다.**

```js
/* ============================================================
   데모 4 — ARN 해부기 (4장)
   ============================================================ */
(function(){
  const out = $('#arnOut'); if(!out) return;
  const D = {
    iam: {arn:"arn:aws:iam::123456789012:user/john",
          f:["aws","iam","","123456789012","user/john"],
          why:"리전 칸이 비어 있습니다. IAM 사용자는 <b>리전에 속하지 않기</b> 때문이에요 — 서울에서 만든 사용자가 도쿄에서도 그대로 통합니다. <a class=\"link\" href=\"#region\">3장에서 본 글로벌</a>이 ARN에서는 이런 모양으로 나타납니다."},
    s3:  {arn:"arn:aws:s3:::amzn-s3-demo-bucket/*",
          f:["aws","s3","","","amzn-s3-demo-bucket/*"],
          why:"리전도 계정도 비어 있습니다. 버킷 이름 자체가 <b>이미 유일</b>해서 더 좁힐 것이 없기 때문이에요. 이름이 얼마나 넓은 범위에서 유일한지는 <a class=\"link\" href=\"#s3\">8장</a>에서 봅니다. 끝의 <code>/*</code>는 버킷 안 모든 객체를 뜻해요."},
    sns: {arn:"arn:aws:sns:us-east-1:123456789012:example-sns-topic-name",
          f:["aws","sns","us-east-1","123456789012","example-sns-topic-name"],
          why:"빈 칸이 없습니다. 리전 안에, 계정 안에 있는 평범한 리소스예요. 대부분의 리소스가 이 모양입니다."},
    vpc: {arn:"arn:aws:ec2:us-east-1:123456789012:vpc/vpc-0e9801d129EXAMPLE",
          f:["aws","ec2","us-east-1","123456789012","vpc/vpc-0e9801d129EXAMPLE"],
          why:"리소스 칸이 <code>종류/식별자</code> 두 토막입니다. 그리고 서비스 칸이 <code>vpc</code>가 아니라 <b><code>ec2</code></b>예요 — 콘솔의 메뉴 이름과 API의 서비스 이름이 늘 같지는 않습니다."}
  };
  const LABELS = ["파티션","서비스","리전","계정","리소스"];
  function render(k){
    const d = D[k]; if(!d) return;
    let cells = d.f.map((v,i) =>
      `<div class="arn-c ${v?'':'empty'}"><div class="arn-l">${LABELS[i]}</div>
       <div class="arn-v">${v ? esc(v) : '— 비어 있음'}</div></div>`).join('');
    out.innerHTML = `<div class="arn-full"><code>${esc(d.arn)}</code></div>
      <div class="arn-row">${cells}</div><p>${d.why}</p>`;
    out.classList.add('show');
  }
  wirePicker('#arnPicker', render);
})();
```

`.arn-full` `.arn-row` `.arn-c` `.arn-c.empty` `.arn-l` `.arn-v` 스타일을 이 장의 `<style>`에 추가한다. 빈 칸은 `--text-mut`에 점선 테두리로 눈에 띄게 한다.

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-arn" data-answer="a">
  <div class="q"><code>arn:aws:s3:::my-bucket</code>에서 <b>리전과 계정 칸이 비어 있는 이유</b>는?</div>
  <button class="opt" data-opt="a">버킷 이름 자체가 이미 유일해서 더 좁힐 것이 없다</button>
  <button class="opt" data-opt="b">S3는 리전을 고르지 않는 글로벌 서비스이기 때문이다</button>
  <button class="opt" data-opt="c">버킷을 만든 계정이 소유권을 주장하지 않기 때문이다</button>
  <button class="opt" data-opt="d">생략해도 되는 칸이라 관례적으로 비워 둔다</button>
</div>
```

해설: A. B가 가장 흔한 오답이고 **절반만 맞다** — 버킷은 리전에 만들지만(3장), 이름만은 리전을 넘어 유일하다. 그래서 리전을 적을 필요가 없는 것이지 리전이 없는 게 아니다. 이 절반의 차이가 8장의 주제가 된다. C는 소유 계정이 분명히 있다는 점에서, D는 빈 칸이 관례가 아니라 뜻이라는 점에서 틀렸다.

- [ ] **Step 5: GLOSSARY** — `"ARN"` `"파티션"` `"리소스 ID"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 5 · 퀴즈 4 · 데모 4` · `exit=0`

- [ ] **Step 7: 브라우저 확인** — 네 예시에서 빈 칸이 시각적으로 구별된다

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "4장: ARN — AWS가 물건을 세는 법

빈 칸에 뜻이 있다는 것이 이 장의 전부다. 예시 넷은 전부 공식 문서의 것이고,
파티션 개수는 문서끼리 어긋나 있어 숫자로 쓰지 않았다."
```

---

## Task 7: 5장 · EC2 — 인스턴스는 서버가 아니다 🟢

**근거 읽기**: facts **V1**(퍼블릭 IP), **V8**(인스턴스 스토어 전체 표).

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 3의 아홉 개 중 `ec2` `key`
- Produces: 상태 넷의 표기(`running` `stopped` `terminated` `rebooting`) — Task 8·9·14가 그대로 쓴다

- [ ] **Step 1: 절 진입**

독자가 당연히 품을 반문으로 연다 — "인스턴스가 서버지 뭔가." 받아 준 뒤 무너뜨린다: 서버는 껐다 켜도 같은 서버지만, 인스턴스는 **껐다 켜면 달라지는 것이 있다**.

- AMI(틀)에서 인스턴스(찍어 낸 것)가 나온다. 같은 AMI로 백 개를 찍으면 백 개가 똑같이 시작한다.
- 인스턴스 타입은 장비 사양의 이름표다. 바꿀 수 있고, 바꾸려면 꺼야 한다.
- 키 페어는 만들 때 받은 개인키를 **다시 못 받는다.**

- [ ] **Step 2: 인스턴스 상태 기계**

facts V8의 표와 V1의 인용을 그대로 근거로 삼는다. **재부팅에서 퍼블릭 IP가 유지된다는 문장은 V1 원문에 없으므로**, 퍼블릭 IP 행의 `reboot` 칸은 "해제 사유 목록에 없음"으로 적고 단정하지 않는다.

```js
/* ============================================================
   데모 5 — 인스턴스 상태 기계 (5장)
   ============================================================ */
(function(){
  const out = $('#lifeOut'); if(!out) return;
  // 인스턴스 스토어 행은 AWS 공식 문서의 데이터 지속성 표 그대로다.
  const D = {
    reboot: {t:"재부팅 (reboot)", rows:[
      ["EC2 인스턴스","keep","그대로 살아 있습니다. 껐다 켜는 게 아니라 재시작이에요."],
      ["EBS 볼륨","keep","그대로입니다."],
      ["인스턴스 스토어","keep","<b>살아남습니다.</b> 공식 문서가 재부팅만은 유지된다고 못 박아 뒀어요."],
      ["퍼블릭 IPv4","keep","공식 문서가 적어 둔 해제 사유는 중지·최대 절전·종료 셋입니다. 재부팅은 그 목록에 없어요."]
    ]},
    stop:   {t:"중지 (stop)", rows:[
      ["EC2 인스턴스","keep","인스턴스는 남습니다. 이 동안 인스턴스 요금은 나가지 않아요."],
      ["EBS 볼륨","keep","<b>남고, 요금도 계속 나갑니다.</b> 껐으니 공짜라는 기대가 깨지는 첫 자리예요."],
      ["인스턴스 스토어","gone","<b>전부 사라집니다.</b> 모든 블록이 암호학적으로 지워져요."],
      ["퍼블릭 IPv4","fresh","<b>해제되고, 다시 켜면 새 주소를 받습니다.</b> 붙여 뒀던 IP로는 더 이상 접속되지 않아요."]
    ]},
    term:   {t:"종료 (terminate)", rows:[
      ["EC2 인스턴스","gone","되돌릴 수 없습니다. 같은 AMI로 새로 띄울 수는 있지만 그건 다른 인스턴스예요."],
      ["EBS 볼륨","warn","<b>경우에 따라 남습니다.</b> 무엇이 갈림길인지는 <a class=\"link\" href=\"#ebs\">6장</a>에서 봅니다."],
      ["인스턴스 스토어","gone","사라집니다."],
      ["퍼블릭 IPv4","gone","해제됩니다."]
    ]},
    resize: {t:"인스턴스 타입 변경", rows:[
      ["EC2 인스턴스","keep","같은 인스턴스입니다. 다만 <b>먼저 중지해야</b> 하므로 위의 중지 결과가 그대로 따라옵니다."],
      ["EBS 볼륨","keep","그대로입니다."],
      ["인스턴스 스토어","gone","<b>사라집니다.</b> 새 타입이 인스턴스 스토어를 지원해도 데이터는 옮겨지지 않아요."],
      ["퍼블릭 IPv4","fresh","중지를 거치므로 새 주소를 받습니다."]
    ]}
  };
  const CLS = {keep:"살아남는다", gone:"사라진다", fresh:"새로 받는다", warn:"조건부"};
  function render(k){
    const d = D[k]; if(!d) return;
    let rows = d.rows.map(([n,c,t]) =>
      `<tr><td>${esc(n)}</td><td><span class="badge ${c}">${CLS[c]}</span></td><td>${t}</td></tr>`).join('');
    out.innerHTML = `<div class="kv"><dt>동작</dt><dd>${esc(d.t)}</dd></div>
      <table class="life-t"><tbody>${rows}</tbody></table>`;
    out.classList.add('show');
  }
  wirePicker('#lifePicker', render);
})();
```

`.badge.keep` `.badge.gone` `.badge.fresh` `.badge.warn`은 Task 1에서 정한 `--keep` `--gone` `--fresh` `--warn`을 쓴다.

- [ ] **Step 3: OS에서 친 명령도 갈린다**

facts V8의 "User-initiated OS events" 두 줄을 `.callout`으로 낸다. 터미널에서 `reboot`을 치면 인스턴스 스토어가 살고 `shutdown`을 치면 죽는다. **같은 터미널에서 한 단어 차이로 갈린다.**

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-ec2" data-answer="c">
  <div class="q">배포 스크립트가 <code>/mnt/cache</code>에 빌드 결과를 쌓아 둡니다. 그 경로가 <b>인스턴스 스토어</b>일 때, 다음 중 데이터가 <b>남아 있는</b> 경우는?</div>
  <button class="opt" data-opt="a">인스턴스 타입을 t3.small에서 t3.medium으로 올렸다</button>
  <button class="opt" data-opt="b">밤에 인스턴스를 중지했다가 아침에 다시 켰다</button>
  <button class="opt" data-opt="c">터미널에서 <code>reboot</code>을 쳤다</button>
  <button class="opt" data-opt="d">터미널에서 <code>shutdown</code>을 쳤다</button>
</div>
```

해설: C. 재부팅만 살아남는다. D가 가장 잔인한 오답이다 — 같은 터미널에서 한 단어 차이인데 결과가 정반대다. B는 "잠깐 껐을 뿐"이라는 감각이 통하지 않는 자리이고, A는 타입 변경이 내부적으로 중지를 거치기 때문이다.

- [ ] **Step 5: GLOSSARY** — `"인스턴스 타입"` `"인스턴스 스토어"` `"키 페어"` `"퍼블릭 IPv4"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 6 · 퀴즈 5 · 데모 5` · `exit=0`

- [ ] **Step 7: 브라우저 확인** — 네 동작에서 배지 색이 축(살아남는다/사라진다/새로 받는다)대로 나온다

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "5장: EC2 — 인스턴스는 서버가 아니다

수명 표는 공식 문서의 데이터 지속성 표를 근거로 삼았다. 재부팅 시 퍼블릭
IP가 유지된다는 문장은 원문에 없으므로 '해제 사유 목록에 없다'까지만 쓴다."
```

---

## Task 8: 6장 · EBS — 디스크가 따로 노는 이유 🟢

**근거 읽기**: facts **V3**. 다섯 행짜리 기본값 표와 "최종 결정권은 AMI에 있다"는 단서. **설계가 한 번 틀렸던 자리다.**

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 7의 `terminate` 표기와 "조건부"로 남긴 EBS 행
- Produces: `DeleteOnTermination` 다섯 행 표 — Task 14(12장 요금)와 Task 15(13장 콘솔·CLI)가 되받는다

- [ ] **Step 1: 절 진입 — 앞 장이 남긴 "조건부"를 되받는다**

5장의 종료 표에서 EBS만 "경우에 따라"였다. 그 경우가 무엇인지 묻는 것으로 연다.

세울 것:
- 볼륨은 인스턴스 밖에 있고 붙였다 뗄 수 있다. 그래서 인스턴스보다 오래 살 수 있다.
- 다만 **같은 AZ 안에서만** 붙는다(3장 회수).
- 스냅샷은 증분이고 S3에 저장된다.

- [ ] **Step 2: 오해 격파 — 기본값은 하나가 아니다**

`.myth`로 낸다. "루트는 지워지고 데이터 볼륨은 남는다"는 요약이 **틀렸다**는 것을 표로 보인다. facts V3의 다섯 행을 그대로 옮긴다.

| 볼륨 | 언제 붙였나 | 방법 | 종료하면 |
|---|---|---|---|
| 루트 | 시작할 때 | 콘솔·CLI | **삭제** |
| 루트 | 시작 후 | 콘솔·CLI | 보존 |
| 데이터 | 시작할 때 | 콘솔 | 보존 |
| 데이터 | 시작할 때 | **CLI** | **삭제** |
| 데이터 | 시작 후 | 콘솔·CLI | 보존 |

같은 "시작할 때 붙인 데이터 볼륨"인데 콘솔은 남기고 CLI는 지운다. **13장과 부딪히는 것처럼 보이지만 모순이 아니다** — 문은 하나이고 콘솔이 대신 채워 넣는 값이 다를 뿐이다. 이 문장을 6장에 심어 두고 13장이 회수한다.

그리고 못을 박는다: 최종 결정권은 AMI에 있으므로 **"기본값은 X다"라고 외우면 안 된다.** 확인하는 법(콘솔의 Storage 탭 · Block devices · Delete on termination 열)을 알려 준다.

- [ ] **Step 3: 볼륨 수명 데모**

```html
<div class="demo" id="volLab">
  <div class="demo-h">💽 이 볼륨은 인스턴스를 지우면 어떻게 될까요</div>
  <div class="pick-row" id="volPicker">
    <button class="pick" data-k="root-launch">루트 · 시작할 때</button>
    <button class="pick" data-k="root-after">루트 · 시작 후 교체</button>
    <button class="pick" data-k="data-console">데이터 · 시작할 때 · 콘솔</button>
    <button class="pick" data-k="data-cli">데이터 · 시작할 때 · CLI</button>
    <button class="pick" data-k="data-after">데이터 · 시작 후</button>
  </div>
  <div class="out" id="volOut"></div>
</div>
```

IIFE는 다섯 키를 위 표 그대로 판정하고, `data-cli`에는 **"여기가 사고가 나는 자리"**라는 경고를 붙인다. 보존되는 항목에는 "보존된 볼륨은 요금이 계속 나간다"는 공식 문서의 단서를 함께 넣는다(12장으로 이어진다).

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-ebs" data-answer="b">
  <div class="q">스크립트로 인스턴스를 띄우면서 데이터 볼륨을 함께 붙였습니다. 인스턴스를 <code>terminate</code>하면 그 볼륨은?</div>
  <button class="opt" data-opt="a">데이터 볼륨이므로 남는다</button>
  <button class="opt" data-opt="b">CLI로 붙였다면 함께 지워진다</button>
  <button class="opt" data-opt="c">루트가 아니므로 남지만 요금은 멈춘다</button>
  <button class="opt" data-opt="d">스냅샷이 자동으로 만들어진 뒤 지워진다</button>
</div>
```

해설: B. A가 가장 흔한 오답이고, **콘솔로 붙였다면 A가 맞다**는 게 이 문제의 함정이다. 같은 일을 콘솔로 했는지 CLI로 했는지가 데이터의 생사를 가른다. C는 보존된 볼륨에 요금이 계속 나간다는 점에서(12장), D는 자동 스냅샷이 없다는 점에서 틀렸다. 그리고 최종 결정권이 AMI에 있으므로 **확인하는 습관**이 답을 외우는 것보다 낫다.

- [ ] **Step 5: GLOSSARY** — `"EBS"` `"스냅샷"` `"루트 볼륨"` `"DeleteOnTermination"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 7 · 퀴즈 6 · 데모 6` · `exit=0`

- [ ] **Step 7: 브라우저 확인** — 다섯 항목의 판정이 표와 한 글자도 어긋나지 않는다

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "6장: EBS — 디스크가 따로 노는 이유

DeleteOnTermination의 기본값은 축이 셋이다. 시작할 때 붙인 데이터 볼륨이
콘솔이냐 CLI냐로 생사가 갈리는 자리를 이 장의 중심에 놓았다. 최종 결정권이
AMI에 있으므로 기본값을 외우게 하지 않고 확인하는 법을 알려 준다."
```

---

## Task 9: 7장 · ENI — 랜카드가 리소스가 되면 🟢

**근거 읽기**: facts **V1**(사설 IP는 ENI에 남고 퍼블릭 IP는 계정 것이 아니다).

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 5의 "서브넷은 AZ에 갇힌다", Task 7의 퍼블릭 IP 거동
- Produces: "인스턴스는 AZ를 옮길 수 없다" — Task 11(9장)이 회수. 보안 그룹 인계 문장 — Task 17(마무리)이 되받는다

- [ ] **Step 1: 절 진입**

5장에서 "껐다 켜면 IP가 바뀐다"고 했다. **왜 IP만 그런지**를 묻는 것으로 연다.

답의 절반을 먼저 준다 — 사설 IP는 ENI에 붙어 있고, 퍼블릭 IP는 **아무 데도 붙어 있지 않기** 때문이다. 나머지 절반(그럼 EIP는 뭔가)은 데모 뒤에 채운다.

facts V1의 두 인용을 근거로:
- 사설 IP는 중지·시작을 넘어 ENI에 남고, 종료할 때 해제된다.
- 퍼블릭 IP는 Amazon의 풀에서 빌려 온 것이고 **내 계정 소유가 아니다.**

- [ ] **Step 2: ENI가 서브넷에 갇힌다**

ENI는 서브넷에 속하고, 서브넷은 AZ에 갇힌다(3장). 두 문장을 이으면 **인스턴스는 AZ를 옮길 수 없다**가 나온다. 옮기려면 스냅샷을 떠서 다른 AZ에 새로 만드는 것뿐이고, 그건 옮긴 게 아니다(2장의 계정 이동과 같은 구조다).

보안 그룹은 여기 붙는다는 것만 한 줄로 놓고 `aws_network_security.html`로 인계한다. **규칙 문법은 다루지 않는다.**

- [ ] **Step 3: ENI 데모**

`eniPicker` 항목 넷: `stop-start` / `detach-attach` / `eip` / `move-az`. 각각 사설 IP · 퍼블릭 IP · 보안 그룹 · AZ 네 행의 결과를 낸다. 5장 데모와 **같은 배지 색 축**을 쓴다.

`move-az`는 "불가"로 판정하고, 이유를 두 문장으로 나눠 보인다(ENI는 서브넷에, 서브넷은 AZ에).

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-eni" data-answer="d">
  <div class="q">인스턴스를 중지했다 켰더니 접속하던 주소가 바뀌었습니다. <b>바뀌지 않은 것</b>은?</div>
  <button class="opt" data-opt="a">인스턴스 ID</button>
  <button class="opt" data-opt="b">사설 IP</button>
  <button class="opt" data-opt="c">보안 그룹</button>
  <button class="opt" data-opt="d">셋 다 그대로다</button>
</div>
```

해설: D. 바뀐 건 퍼블릭 IP 하나뿐이고, 그것만 ENI에 붙어 있지 않다. 나머지는 전부 리소스에 붙어 있어서 중지를 넘어 살아남는다. **하나만 다르다는 것이 이 장의 요지**이고, 그 하나를 고정하려고 EIP가 있다 — 그리고 EIP는 12장에서 다시 만난다.

- [ ] **Step 5: GLOSSARY** — `"ENI"` `"사설 IP"` `"탄력적 IP"` `"보안 그룹"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 8 · 퀴즈 7 · 데모 7` · `exit=0`

- [ ] **Step 7: 브라우저 확인**

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "7장: ENI — 랜카드가 리소스가 되면

퍼블릭 IP만 ENI에 붙어 있지 않다는 한 가지가 5장의 '왜 IP만 바뀌나'를 푼다.
ENI는 서브넷에, 서브넷은 AZ에 갇히므로 인스턴스는 AZ를 옮길 수 없다 —
9장에서 로드밸런서가 서브넷을 요구하는 이유가 여기서 나온다."
```

---

## Task 10: 8장 · S3 — 파일 서버가 아니다 🟢

**근거 읽기**: facts **V5**. 파티션 안에서의 유일성, 그리고 계정 리전 네임스페이스.

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 5의 "글로벌인 것들", Task 6의 S3 ARN 빈 칸, Task 4가 남긴 미결(같은 이름 버킷)
- Produces: 없음(1부의 마지막 장)

- [ ] **Step 1: 절 진입 — 두 장이 남긴 미결을 한꺼번에 받는다**

2장은 "같은 이름 버킷을 못 만든다"고만 했고, 4장은 "ARN에 계정 칸이 비어 있다"고만 했다. 둘 다 같은 사실을 가리키고 있었다는 것으로 연다.

- **이름은 파티션 안에서 유일하다.** "전 세계에서 유일"은 흔한 요약인데 정확하지 않다 — 중국과 GovCloud는 별도 파티션이라 같은 이름이 따로 존재할 수 있다.
- 그래서 **남이 먼저 쓴 이름은 내가 못 쓴다.** 지운 이름을 남이 가져가면 그쪽으로 요청이 갈 수 있다는 공식 문서의 경고까지 옮긴다.

- [ ] **Step 2: 파일 서버가 아니라는 것**

- 디렉터리가 없다. 슬래시가 든 이름이 있을 뿐이다.
- 객체는 **통째로 쓰고 통째로 읽는다.** 일부만 고칠 수 없다.
- 마운트해서 쓰는 물건이 아니다. HTTP API로 주고받는다.

- [ ] **Step 3: S3 vs EBS 데모**

같은 작업을 양쪽에 시켜 보는 형태다. `storePicker` 항목 다섯: `edit-part`(파일 일부 수정) / `mount`(마운트해서 쓰기) / `concurrent`(서버 열 대가 동시에 읽기) / `outlive`(인스턴스보다 오래 살기) / `az`(다른 AZ에서 붙이기).

각 항목에서 S3 열과 EBS 열의 판정이 갈리고, 갈리는 **이유**가 한 줄씩 붙는다. `az` 항목은 7장을 회수한다 — EBS는 AZ에 갇히고 S3는 갇히지 않는다.

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-s3" data-answer="c">
  <div class="q">로그 파일을 S3에 두고 <b>새 줄을 계속 덧붙이려</b> 합니다. 가장 정확한 설명은?</div>
  <button class="opt" data-opt="a">append 모드로 열어 쓰면 된다</button>
  <button class="opt" data-opt="b">버킷에 추가 쓰기 권한을 주면 된다</button>
  <button class="opt" data-opt="c">덧붙일 수 없다 — 매번 객체 전체를 다시 써야 한다</button>
  <button class="opt" data-opt="d">1MB를 넘으면 자동으로 이어 쓰기로 바뀐다</button>
</div>
```

해설: C. 객체는 통째로가 원칙이고, 그래서 로그를 S3에 실시간으로 쌓는 구조는 대개 **모아서 주기적으로 올리는** 모양이 된다. A는 파일시스템의 감각을 그대로 가져온 것이고 — S3는 파일시스템이 아니다. B는 권한 문제가 아니라 **모델의 문제**라서, D는 그런 전환이 없어서 틀렸다.

- [ ] **Step 5: GLOSSARY** — `"버킷"` `"객체"` `"객체 스토리지"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 9 · 퀴즈 8 · 데모 8` · `exit=0`

- [ ] **Step 7: 브라우저 확인**

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "8장: S3 — 파일 서버가 아니다

2장과 4장이 각각 남긴 미결이 같은 사실을 가리키고 있었다는 것으로 연다.
'전 세계에서 유일'은 정확하지 않다 — 파티션 안에서다."
```

---

## Task 11: 9장 · 앞에 무엇이 서 있나 🟢

**근거 읽기**: facts **V7**. ALB 최소 두 AZ / NLB 최소 한 AZ, ALB의 `/27`과 여덟 개 여유 IP, NLB의 고정 IP, ALB 주소는 서비스가 쥐고 있다는 것.

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 5의 AZ, Task 9의 ENI와 EIP
- Produces: NAT Gateway의 존재 — Task 14(12장)가 요금으로 되받는다

- [ ] **Step 1: 절 진입 — 2부의 시작**

1부가 아홉 개를 흩어 놓았으니, 2부는 그걸로 뭘 짓느냐다. 첫 질문은 독자가 실제로 막히는 자리에서 가져온다 — "인스턴스는 떴는데, 사람들이 여기로 어떻게 오나."

**이 장은 통제를 다루지 않는다.** 무엇을 막느냐는 `aws_network_security.html`이고, 여기서는 **무엇이 서 있느냐**만 본다. 이 선을 본문에 선언하지 말고, 다루는 내용으로 지킨다.

- IGW — 퍼블릭 IP를 가진 것만 지나간다.
- NAT GW — 나가기만 하는 문. 안에서 밖으로는 되고 밖에서 안으로는 안 된다.
- ALB — HTTP를 읽는다. 경로로 나눌 수 있다.
- NLB — 포트만 본다. 대신 **주소를 고정할 수 있다.**

- [ ] **Step 2: 서브넷 요구가 갈리는 자리**

facts V7을 근거로. ALB는 **서로 다른 AZ의 서브넷을 최소 둘** 요구하고, NLB는 **최소 하나**다. 이유를 3장·7장으로 착지시킨다 — 로드밸런서는 AZ마다 ENI를 하나씩 만들고, ENI는 서브넷 안에 있어야 하니까.

ALB의 서브넷은 `/27` 이상에 여유 IP 여덟 개가 필요하다는 것도 넣는다. 이건 실제로 확장 실패를 만드는 조건이다.

- [ ] **Step 3: 입구 고르기 데모**

요구사항을 고르면 필요한 것이 나온다. `entryPicker` 항목 다섯:

| 키 | 요구사항 | 답 |
|---|---|---|
| `path` | `/api`는 A로, 나머지는 B로 보내고 싶다 | ALB |
| `staticip` | 상대 회사 방화벽에 우리 IP를 등록해야 한다 | NLB + EIP |
| `outbound` | 서버는 밖으로 나가야 하지만 밖에서는 못 들어오게 | NAT GW |
| `direct` | 인스턴스 하나에 그냥 직접 붙고 싶다 | IGW + 퍼블릭 IP |
| `noip` | 인스턴스에 퍼블릭 IP를 아예 안 주고 싶다 | 로드밸런서를 앞에 세운다 |

각 답에 **왜 나머지로는 안 되는지**를 한 줄씩. `staticip`은 ALB로 안 되는 이유(주소를 서비스가 쥐고 있어 바꾸거나 놓아줄 수 없다)를 facts V7의 인용대로 적는다.

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-entry" data-answer="a">
  <div class="q">ALB를 만들려는데 콘솔이 서브넷을 <b>두 개 이상</b> 고르라고 합니다. 왜일까요?</div>
  <button class="opt" data-opt="a">서로 다른 AZ마다 로드밸런서의 ENI가 하나씩 필요하기 때문</button>
  <button class="opt" data-opt="b">한 서브넷의 IP가 부족할 때를 대비한 예비 서브넷이기 때문</button>
  <button class="opt" data-opt="c">퍼블릭 서브넷과 프라이빗 서브넷을 각각 지정해야 하기 때문</button>
  <button class="opt" data-opt="d">HTTP용과 HTTPS용 서브넷이 따로 필요하기 때문</button>
</div>
```

해설: A. 3장(AZ)과 7장(ENI는 서브넷에 산다)이 여기서 만난다. B는 예비가 아니라 **둘 다 동시에 쓴다**는 점에서, C는 그런 속성 자체가 없다는 점에서(라우팅 테이블에 IGW가 걸렸느냐일 뿐 — 상세는 네트워크 보안 문서), D는 리스너와 서브넷이 무관하다는 점에서 틀렸다.

- [ ] **Step 5: GLOSSARY** — `"인터넷 게이트웨이"` `"NAT 게이트웨이"` `"ALB"` `"NLB"` `"리스너"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 10 · 퀴즈 9 · 데모 9` · `exit=0`

- [ ] **Step 7: 브라우저 확인**

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "9장: 앞에 무엇이 서 있나

ALB가 서브넷 둘을 요구하는 이유가 3장과 7장에서 나온다. ALB와 NLB의 두 번째
갈림길은 주소다 — NLB는 고정할 수 있고 ALB의 주소는 서비스가 쥐고 있다.
통제는 다루지 않는다. 그건 aws_network_security.html의 몫이다."
```

---

## Task 12: 10장 · 관리형 — 무엇을 남기고 무엇을 가져가는가 🟢

**근거 읽기**: facts **V10**. 열한 행짜리 책임 표와 "RDS는 호스트 접근을 허용하지 않는다"는 인용.

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 4의 "계정은 격리 단위"
- Produces: 책임 분계선 개념 — Task 13(11장 세 갈래)이 같은 축을 쓴다

- [ ] **Step 1: 절 진입 — 이론을 먼저 내지 않는다**

"책임 공유 모델"이라는 이름을 **먼저 꺼내지 않는다.** 먼저 김주임이 DB를 올리는 장면을 놓는다 — EC2에 직접 설치할 것인가, RDS를 쓸 것인가. 무엇이 달라지는지를 표로 본 **다음에** 이름을 붙인다.

- [ ] **Step 2: 책임 표**

facts V10의 열한 행을 그대로 옮긴다. 세 열(온프렘 · EC2 · RDS)의 색을 `--own-me` / `--own-aws`로 칠하면 **경계선이 계단처럼 내려가는 것**이 눈에 보인다.

그리고 맨 윗줄을 짚는다 — 열한 줄 중 **애플리케이션 최적화만 세 열이 전부 내 것**이다. AWS가 아무리 가져가도 쿼리는 끝까지 내 몫이라는 이야기이고, 공식 문서도 따로 못을 박아 두었다(V10의 두 번째 인용).

- [ ] **Step 3: 가져가는 대신 못 하게 되는 것**

facts V10의 첫 인용을 그대로. RDS는 **호스트에 접근하게 해 주지 않고**, 높은 권한이 필요한 일부 절차와 객체도 막는다. 확장을 설치하거나 OS 설정을 바꿔야 하는 워크로드는 여기서 막힌다.

탈출구(RDS Custom)는 **한 줄만** 언급하고 넘어간다. 이 문서의 범위 밖이다.

- [ ] **Step 4: 책임 분계선 데모**

`respPicker`로 `onprem` / `ec2` / `rds` 셋을 고르면, 열한 행이 각각 누구 몫인지 칠해지고 **아래에 두 줄 요약**이 붙는다 — "줄어든 일"과 "못 하게 된 일". `rds`를 고를 때만 "못 하게 된 일"에 내용이 찬다.

- [ ] **Step 5: 퀴즈**

```html
<div class="quiz" data-qid="q-managed" data-answer="b">
  <div class="q">EC2에 직접 설치한 PostgreSQL을 RDS로 옮겼습니다. <b>더 이상 할 수 없게 되는</b> 것은?</div>
  <button class="opt" data-opt="a">읽기 전용 복제본을 두는 것</button>
  <button class="opt" data-opt="b">DB 서버에 SSH로 들어가 설정 파일을 여는 것</button>
  <button class="opt" data-opt="c">느린 쿼리를 찾아 인덱스를 거는 것</button>
  <button class="opt" data-opt="d">백업을 매일 받는 것</button>
</div>
```

해설: B. 관리형이 가져간 것의 다른 얼굴이다. A와 D는 오히려 **RDS가 대신 해 주는 쪽**이고, C는 세 열 어디서나 끝까지 내 몫으로 남는 그 한 줄이다 — 관리형으로 옮긴다고 느린 쿼리가 빨라지지는 않는다.

- [ ] **Step 6: GLOSSARY** — `"관리형 서비스"` `"RDS"` `"책임 공유 모델"` `"읽기 전용 복제본"` 추가

- [ ] **Step 7: 검사기** — Expected: `섹션 11 · 퀴즈 10 · 데모 10` · `exit=0`

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "10장: 관리형 — 무엇을 남기고 무엇을 가져가는가

책임 표의 열한 줄 중 맨 윗줄만 세 열이 전부 내 것이다. AWS가 아무리
가져가도 쿼리는 끝까지 내 몫이라는 것이 이 표가 스스로 말하는 것이다.
이론 이름은 표를 본 다음에 붙인다."
```

---

## Task 13: 11장 · 내 앱을 어디에 올리나 🟢

**근거 읽기**: facts **V9**. Lambda 함수 타임아웃 900초, 메모리 128MB~10,240MB, zip 50MB/250MB, 컨테이너 이미지 10GB, 1,769MB에서 1 vCPU. **"Lambda는 15분이 최대"라고 쓰지 않는다.**

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 12의 책임 축(`--own-me` / `--own-aws`)
- Produces: 없음

- [ ] **Step 1: 절 진입**

앞 장이 DB의 분계선을 그었으니, 같은 질문을 **내 코드**에 던지는 것으로 연다.

세 갈래와 **각각의 단위**:
- EC2 — 장비를 빌린다. 단위는 인스턴스.
- 컨테이너(ECS·Fargate·EKS) — 프로세스를 맡긴다. 단위는 태스크.
- Lambda — 함수만 던진다. 단위는 실행 한 번.

단위가 다르면 **요금을 세는 법도 다르다**. 인스턴스는 켜 둔 시간, 실행은 부른 횟수와 걸린 시간.

- [ ] **Step 2: 갈림의 축**

- 상시인가 간헐인가
- 상태가 있나 (있으면 Lambda에 얹기 어렵다)
- 기동 시간을 견딜 수 있나
- **실행 한계** — Lambda **함수**의 타임아웃은 900초다. 이 표현을 벗어나지 않는다.

facts V9의 수치 중 본문에 쓸 것은 900초 · 128MB~10,240MB · 1,769MB에서 1 vCPU · 컨테이너 이미지 10GB. 나머지는 넣지 않는다.

신규 계정은 기본 할당량이 더 낮게 시작한다는 단서도 한 줄 넣는다(V9 인용).

- [ ] **Step 3: 세 갈래 선택기**

`computePicker` 항목 넷: `always`(하루 종일 도는 API 서버) / `spiky`(하루 몇 번, 몇 초씩) / `batch`(밤에 두 시간 도는 정산 배치) / `stateful`(웹소켓 연결을 유지해야 함).

각 항목에서 세 갈래를 **점수가 아니라 이유로** 갈라 준다. `batch`는 900초를 넘으므로 Lambda 함수가 탈락하는 자리다 — 여기서 수치가 실제로 결정을 바꾸는 것을 보인다.

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-compute" data-answer="c">
  <div class="q">밤마다 <b>40분씩</b> 도는 정산 배치를 옮기려 합니다. Lambda 함수로 가려 할 때 가장 먼저 막히는 것은?</div>
  <button class="opt" data-opt="a">메모리 상한</button>
  <button class="opt" data-opt="b">배포 패키지 크기</button>
  <button class="opt" data-opt="c">함수 타임아웃</button>
  <button class="opt" data-opt="d">동시 실행 수</button>
</div>
```

해설: C. 함수 타임아웃은 900초, 곧 15분이다. 40분짜리 작업은 시작부터 성립하지 않는다. A는 10,240MB까지 올릴 수 있어서, B는 컨테이너 이미지로 10GB까지 가능해서, D는 밤에 한 번 도는 배치가 동시 실행과 무관해서 아니다. 쪼개서 이어 붙이는 방법이 없지는 않지만, **그건 이미 다른 설계**다.

- [ ] **Step 5: GLOSSARY** — `"컨테이너"` `"Fargate"` `"Lambda"` `"콜드 스타트"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 12 · 퀴즈 11 · 데모 11` · `exit=0`

- [ ] **Step 7: 커밋**

```bash
git add aws_basics.html
git commit -m "11장: 내 앱을 어디에 올리나

세 갈래의 단위가 다르고, 단위가 다르니 요금을 세는 법도 다르다.
'Lambda는 15분이 최대'가 아니라 '함수의 타임아웃은 900초'로 쓴다 —
같은 공식 문서의 MicroVM 항목과 어긋나기 때문이다."
```

---

## Task 14: 12장 · 안 쓰는데 돈이 나간다 🟢

**근거 읽기**: facts **V2**(2024-02-01 시행, 시간당 $0.005, 붙어 있어도 같은 값, 프리 티어 750시간, BYOIP 제외), **V4**(NAT GW 시간당 $0.045 + GB당 $0.045 + 자신의 퍼블릭 IP), **V3**(보존된 볼륨은 요금이 계속 나간다).

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 3의 요금 축 문구, Task 8의 보존 볼륨, Task 9의 EIP·NAT GW, Task 11의 NAT GW
- Produces: 체크리스트 항목 — Task 17(마무리)이 쓴다

- [ ] **Step 1: 절 진입**

1장에서 "각각 따로 과금된다"고 했다. 그 문장의 **청구서 쪽 얼굴**을 보는 것으로 연다. 김주임이 월말에 청구서를 열었더니, 지난주에 지운 인스턴스 자리에 항목이 남아 있다.

- [ ] **Step 2: 오해 격파 — "안 쓰는 EIP만 돈이 나간다"**

`.myth`로 낸다. 이건 **2024년 2월 이전의 상식**이다. 지금은 쓰는 것과 노는 것의 시간당 값이 **같다**(V2). 그래서 축이 "붙였나 놀리나"가 아니라 **"몇 개나 갖고 있나"**로 바뀐다.

함께 적을 것: 시행일(2024-02-01), 프리 티어에 첫 12개월 월 750시간이 포함된다는 것, BYOIP는 제외라는 것. EC2뿐 아니라 RDS·EKS 노드 등 퍼블릭 IPv4를 붙일 수 있는 모든 곳에 적용된다는 것.

- [ ] **Step 3: 무엇이 시간당이고 무엇이 요청당인가**

- 시간당: 인스턴스(켜져 있을 때) · EBS 볼륨(꺼져 있어도) · 퍼블릭 IPv4 · NAT Gateway
- 용량당: EBS 크기 · S3 저장량 · 스냅샷
- 요청·처리당: S3 요청 · Lambda 실행 · NAT Gateway 처리 GB
- 데이터 전송은 **나가는 방향**이 비싸다

- [ ] **Step 4: NAT Gateway는 세 겹이다**

V4를 근거로. AZ 수만큼의 시간당 요금 + 처리 GB당 요금 + 자신이 쥔 퍼블릭 IPv4의 시간당 요금. 공식 문서가 실은 계산식을 그대로 옮긴다.

- [ ] **Step 5: 요금 계산기**

`wireTogs`로 만든다. 토글 여섯 개:

```html
<div class="demo" id="costCalc">
  <div class="demo-h">💸 이번 달에 무엇이 켜져 있나요</div>
  <div class="tog-row" id="costTogs">
    <button class="tog on" data-k="ec2">EC2 인스턴스 1대 (running)</button>
    <button class="tog" data-k="stopped">그 인스턴스를 중지했다</button>
    <button class="tog on" data-k="ebs">EBS 30GB</button>
    <button class="tog" data-k="orphan">지운 인스턴스가 남긴 EBS 30GB</button>
    <button class="tog" data-k="eip">안 붙여 둔 EIP 1개</button>
    <button class="tog" data-k="nat">NAT Gateway 1개</button>
  </div>
  <div class="out" id="costOut"></div>
</div>
```

출력은 **금액 합계를 내지 않는다.** 리전마다 값이 다르고, 이 문서가 확보한 것은 공식 페이지에 적힌 몇 개뿐이다. 대신 항목마다 **"꺼도 나가는가"를 배지로** 내고, 공식 문서에서 확인된 값(퍼블릭 IPv4 시간당 $0.005, NAT GW 시간당 $0.045 + GB당 $0.045)만 그 항목에 붙인다. **EBS와 인스턴스의 단가는 적지 않는다 — 근거 파일에 없다.**

`stopped`를 켜면 `ec2` 행이 "요금 멈춤"으로, `ebs` 행은 **그대로 나감**으로 바뀐다. 이 대비가 이 데모의 전부다.

- [ ] **Step 6: 퀴즈**

```html
<div class="quiz" data-qid="q-cost" data-answer="d">
  <div class="q">인스턴스를 <b>중지</b>해 두었습니다. 이번 달 요금이 <b>계속 나가는</b> 것은?</div>
  <button class="opt" data-opt="a">인스턴스 사용 시간</button>
  <button class="opt" data-opt="b">인스턴스 스토어 용량</button>
  <button class="opt" data-opt="c">그 인스턴스가 쓰던 퍼블릭 IPv4</button>
  <button class="opt" data-opt="d">붙어 있는 EBS 볼륨</button>
</div>
```

해설: D. 중지는 인스턴스 요금을 멈추지만 디스크는 그대로 있다 — 6장에서 본 "따로 논다"의 청구서 쪽 얼굴이다. A는 멈추고, B는 인스턴스 스토어가 애초에 별도 과금이 아니며 중지하면 데이터도 사라지고(5장), C는 중지하는 순간 해제되므로(7장) 그 주소에는 더 이상 값이 붙지 않는다. **다만 EIP로 잡아 둔 주소라면 이야기가 다르다** — 그건 놓아주기 전까지 내 것이고, 내 것인 동안 값이 나간다.

- [ ] **Step 7: GLOSSARY** — `"프리 티어"` `"데이터 전송"` `"Cost Explorer"` 추가

- [ ] **Step 8: 검사기** — Expected: `섹션 13 · 퀴즈 12 · 데모 12` · `exit=0`

- [ ] **Step 9: 커밋**

```bash
git add aws_basics.html
git commit -m "12장: 안 쓰는데 돈이 나간다

'안 쓰는 EIP만 과금'은 2024년 2월 이전의 상식이다. 쓰는 것과 노는 것이
같은 값이라 축이 개수로 바뀐다. 금액 합계는 내지 않는다 — 리전마다
다르고, 근거 파일이 확보한 단가는 두 개뿐이다."
```

---

## Task 15: 13장 · 콘솔·CLI·API는 같은 문 세 개 🟢

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 6의 ARN, Task 8의 콘솔/CLI 기본값 갈림
- Produces: 부록 A의 명령어들이 이 장의 연장이 된다

- [ ] **Step 1: 절 진입 — 6장이 심어 둔 모순을 회수한다**

6장에서 같은 일을 콘솔로 하면 볼륨이 남고 CLI로 하면 지워졌다. **문이 다른 건가?** 이 반문으로 연다.

답: 문은 하나다. 콘솔도 CLI도 SDK도 밑에서는 같은 API를 부른다. 다른 건 **콘솔이 대신 채워 넣는 기본값**이다. 그래서 콘솔에서 되는 일은 전부 자동화할 수 있고, 동시에 **콘솔이 조용히 채워 준 것을 모르면 CLI에서 놀란다.**

- [ ] **Step 2: 자격 증명이 어디서 오나**

환경변수 · 프로필 · 인스턴스 역할 — 이름과 우선순위 감각까지만. 상세는 `iam_tutorial.html`로 인계한다.

- [ ] **Step 3: 같은 일 세 가지 방법 데모**

`doorPicker`로 `console` / `cli` / `sdk`를 고르면 **같은 작업**(태그 붙은 인스턴스 목록 조회)이 세 모양으로 보이고, 그 아래에 **셋 다 같은 API 호출**(`ec2:DescribeInstances`)이라는 것이 나온다. 4장의 ARN이 요청의 `Resource` 자리에서 다시 나타나는 것을 함께 보인다.

CLI 예시는 Prism `bash`, SDK 예시는 Prism `clike`로 하이라이트한다. **실행되지 않는 예시여도 문법은 정확해야 한다.**

- [ ] **Step 4: 퀴즈**

```html
<div class="quiz" data-qid="q-doors" data-answer="b">
  <div class="q">같은 작업인데 콘솔로 했을 때와 CLI로 했을 때 <b>결과가 달랐다면</b> 무엇을 의심해야 할까요?</div>
  <button class="opt" data-opt="a">콘솔과 CLI가 서로 다른 API를 부른다</button>
  <button class="opt" data-opt="b">콘솔이 내가 지정하지 않은 값을 대신 채웠다</button>
  <button class="opt" data-opt="c">CLI의 버전이 콘솔보다 낡았다</button>
  <button class="opt" data-opt="d">리전이 다르게 잡혔다</button>
</div>
```

해설: B. 6장의 `DeleteOnTermination`이 정확히 그 자리였다. D도 실제로 자주 겪는 일이라 확인할 값어치가 있지만, **같은 리전에서도 결과가 갈리는** 이 문제의 답은 아니다. A는 같은 API라는 이 장의 요지에 어긋나고, C는 버전이 파라미터의 기본값을 바꾸지는 않는다.

- [ ] **Step 5: GLOSSARY** — `"AWS CLI"` `"SDK"` `"프로필"` `"인스턴스 역할"` 추가

- [ ] **Step 6: 검사기** — Expected: `섹션 14 · 퀴즈 13 · 데모 13` · `exit=0`

- [ ] **Step 7: 커밋**

```bash
git add aws_basics.html
git commit -m "13장: 콘솔·CLI·API는 같은 문 세 개

6장이 심어 둔 모순(같은 일인데 콘솔과 CLI의 결과가 다르다)을 여기서 푼다.
문은 하나이고 콘솔이 대신 채워 넣는 값이 다를 뿐이다."
```

---

## Task 16: 14장 · 손으로 만든 것은 사라진다 🟢

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 3의 아홉 개, Task 14의 청구서
- Produces: 없음

- [ ] **Step 1: 절 진입**

12장에서 청구서에 정체불명 항목이 있었다. **그게 무엇이었는지 어떻게 아나**로 연다. 답은 태그다. 태그가 없으면 청구서의 항목이 익명이 된다.

- 태그의 실제 쓸모: 비용 배분 · 소유자 추적 · 일괄 조작
- 콘솔에서 클릭한 아홉 개를 누가 기억하는가 — 아무도 안 한다. 그래서 IaC가 나온다.
- IaC(CloudFormation·Terraform)는 **만든 순서가 파일로 남는다**는 것까지만. 문법은 다루지 않는다.
- 드리프트: 콘솔에서 손으로 고치면 파일과 실물이 어긋난다.

- [ ] **Step 2: 드리프트 데모**

`driftPicker` 항목 넷: `apply`(파일대로 만든다) / `manual`(콘솔에서 규칙 하나를 손으로 바꾼다) / `replan`(다시 계획을 본다) / `reapply`(다시 적용한다). 상태가 순서대로 변하는 것을 보여 주고, `reapply`에서 **손으로 한 변경이 되돌아간다**는 것을 낸다.

`manual` 단계에 한 줄 붙인다 — 급할 때 콘솔에서 고치는 건 흔한 일이고, 문제는 고친 것이 아니라 **기록하지 않은 것**이다.

- [ ] **Step 3: 퀴즈**

```html
<div class="quiz" data-qid="q-tag" data-answer="a">
  <div class="q">청구서에 "EBS 볼륨 · 120GB"가 있는데 누구 것인지 아무도 모릅니다. 다음에 이 일을 <b>막는</b> 것은?</div>
  <button class="opt" data-opt="a">모든 리소스에 소유자 태그를 강제하는 규칙</button>
  <button class="opt" data-opt="b">볼륨 이름을 알아보기 쉽게 짓는 규칙</button>
  <button class="opt" data-opt="c">월말마다 청구서를 검토하는 절차</button>
  <button class="opt" data-opt="d">인스턴스를 지울 때 볼륨도 함께 지우는 설정</button>
</div>
```

해설: A. 청구서는 이름이 아니라 태그로 갈린다. B는 콘솔에서만 보이고 비용 배분에 쓰이지 않으며, C는 **이미 나간 돈을 확인**할 뿐 다음을 막지 못한다. D는 이 사고 하나는 막지만 6장에서 봤듯 기본값이 상황마다 갈려서 규칙으로 삼기 어렵고, 무엇보다 **볼륨을 일부러 남겨야 할 때** 같은 문제가 다시 생긴다.

- [ ] **Step 4: GLOSSARY** — `"태그"` `"IaC"` `"드리프트"` `"CloudFormation"` 추가

- [ ] **Step 5: 검사기** — Expected: `섹션 15 · 퀴즈 14 · 데모 14` · `exit=0`

- [ ] **Step 6: 커밋**

```bash
git add aws_basics.html
git commit -m "14장: 손으로 만든 것은 사라진다

12장의 정체불명 청구 항목이 여기서 태그 이야기가 된다. 급할 때 콘솔에서
고치는 게 문제가 아니라 기록하지 않는 게 문제다."
```

---

## Task 17: 15장 · 마무리 — 내 계정에는 지금 몇 개가 켜져 있나

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 2의 아홉 개 목록과 자가진단, 전 장의 결론
- Produces: `.ckl` 체크리스트 — `awsbase:ckl` 키를 쓴다

- [ ] **Step 1: 히어로의 아홉 개를 회수한다**

Task 2의 아홉 개를 같은 순서로 다시 놓되, 이번에는 **한 줄 답**이 붙어 있다. 독자가 첫 화면에서 본 목록이 열다섯 장을 지나 채워지는 모양이다.

**추상론으로 닫지 않는다.** 김주임의 첫 배포 장면으로 돌아가 착지시킨다.

- [ ] **Step 2: 체크리스트**

`.ckl`로 낸다. `data-k`는 `awsbase:ckl`에 저장된다. 항목 여덟:

1. 내 계정의 AZ 이름이 어느 AZ ID에 붙어 있는지 확인해 봤다 (3장)
2. 지금 켜져 있는 인스턴스 수를 안다 (5장)
3. **아무 인스턴스에도 안 붙어 있는 EBS 볼륨**이 있는지 확인했다 (6장·12장)
4. 갖고 있는 퍼블릭 IPv4 개수를 안다 (7장·12장)
5. NAT Gateway가 몇 개 있는지 안다 (9장·12장)
6. 소유자 태그가 없는 리소스가 있는지 확인했다 (14장)
7. 콘솔에서 손으로 만든 것 중 파일로 안 남은 게 무엇인지 안다 (14장)
8. 청구서에서 가장 비싼 세 줄을 말할 수 있다 (12장)

각 항목에 **확인하는 명령**을 부록 A로 거는 링크를 붙인다.

- [ ] **Step 3: 두 문서로 인계한다**

- "누가 이걸 만질 수 있나" → [`iam_tutorial.html`](iam_tutorial.html)
- "패킷이 어디까지 갈 수 있나" → [`aws_network_security.html`](aws_network_security.html)

7장에서 이름만 걸어 둔 보안 그룹이 저쪽에서 본론이 된다는 것을 밝힌다.

- [ ] **Step 4: 하나는 열어 둔다**

미결 하나를 남기고 끝낸다. 겸양이 아니라 독자의 참여 여지다. 자가진단(Task 2)을 다시 눌러 보라는 권유가 이 자리에 온다 — 같은 문항인데 이제 다르게 읽힐 것이다.

- [ ] **Step 5: 퀴즈**

```html
<div class="quiz" data-qid="q-wrap" data-answer="c">
  <div class="q">이 문서를 한 문장으로 줄인다면?</div>
  <button class="opt" data-opt="a">AWS는 서비스가 많으니 필요한 것만 골라 쓰면 된다</button>
  <button class="opt" data-opt="b">클라우드는 온프렘보다 싸고 빠르다</button>
  <button class="opt" data-opt="c">한 몸이던 것이 쪼개졌고, 쪼개진 것마다 수명과 값이 따로 붙는다</button>
  <button class="opt" data-opt="d">콘솔보다 CLI를 쓰는 편이 정확하다</button>
</div>
```

해설: C. 1장에서 세운 것이 열네 장을 지나 그대로 남는다. D는 13장의 요지를 뒤집은 것이다 — 문은 하나이고, 다른 건 콘솔이 대신 채우는 값이다. A는 이 문서가 만들려 한 것(부품의 관계)과 어긋나고, B는 이 문서가 한 번도 주장하지 않은 것이다.

- [ ] **Step 6: 검사기** — Expected: `섹션 16 · 퀴즈 15 · 데모 14` · `exit=0`

- [ ] **Step 7: 체크리스트 저장 확인**

브라우저에서 항목 셋을 체크하고 새로고침한다. 그대로 남아 있어야 한다. 개발자도구에서 `localStorage`에 `awsbase:ckl`만 있고 `netsec:ckl`은 없어야 한다.

- [ ] **Step 8: 커밋**

```bash
git add aws_basics.html
git commit -m "15장: 마무리 — 내 계정에는 지금 몇 개가 켜져 있나

히어로의 아홉 개가 여기서 한 줄씩 답을 받는다. 추상론으로 닫지 않고
김주임의 첫 배포로 돌아가 착지시켰다. 미결 하나는 열어 둔다."
```

---

## Task 18: 부록 A · 진짜 명령어, 부록 B · 다른 이름 같은 이야기

**Files:** Modify `aws_basics.html`

**Interfaces:**
- Consumes: Task 17의 체크리스트 링크(`#appendix-cli`의 항목 id를 가리킨다)
- Produces: 없음

- [ ] **Step 1: 부록 A — 진짜 명령어**

체크리스트 여덟 항목에 대응하는 실제 명령. 전부 **읽기 전용**이고, 실행해도 아무것도 바꾸지 않는다는 것을 밝힌다.

```bash
# 내가 지금 누구로 로그인해 있나
aws sts get-caller-identity

# 내 계정에서 AZ 이름이 어느 AZ ID에 붙어 있나 (3장)
aws ec2 describe-availability-zones --region ap-northeast-2 \
  --query 'AvailabilityZones[].{name:ZoneName,id:ZoneId}' --output table

# 켜져 있는 인스턴스 (5장)
aws ec2 describe-instances \
  --filters Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].{id:InstanceId,type:InstanceType,az:Placement.AvailabilityZone}' \
  --output table

# 아무 데도 안 붙어 있는 볼륨 (6장·12장)
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].{id:VolumeId,size:Size,az:AvailabilityZone,created:CreateTime}' \
  --output table

# 갖고 있는 탄력적 IP (7장·12장)
aws ec2 describe-addresses \
  --query 'Addresses[].{ip:PublicIp,attached:InstanceId}' --output table

# NAT 게이트웨이 (9장·12장)
aws ec2 describe-nat-gateways \
  --query 'NatGateways[?State==`available`].{id:NatGatewayId,subnet:SubnetId}' \
  --output table

# 인스턴스에 붙은 볼륨의 DeleteOnTermination (6장)
aws ec2 describe-instances --instance-ids i-0123456789abcdef0 \
  --query 'Reservations[].Instances[].BlockDeviceMappings[].{dev:DeviceName,del:Ebs.DeleteOnTermination}' \
  --output table
```

각 명령 아래에 **무엇을 보라는 것인지** 한 줄. 특히 마지막 것은 6장의 표를 눈으로 확인하는 명령이다.

- [ ] **Step 2: 부록 B — 다른 이름 같은 이야기**

GCP·Azure 대응표. **이름만 맞추고 동작 설명은 넣지 않는다** — 이 문서의 근거 파일에 두 클라우드 항목이 없다. 표 머리에 "맞춰 놓은 것은 이름까지"라고 밝힌다. (`auth_basics.html` 부록 B의 전례를 따른다. `known-issues` §7 참고.)

| AWS | GCP | Azure |
|---|---|---|
| 계정 | 프로젝트 | 구독 |
| 리전 | 리전 | 지역 |
| 가용 영역 | 영역(zone) | 가용성 영역 |
| EC2 인스턴스 | Compute Engine 인스턴스 | 가상 머신 |
| EBS 볼륨 | 영속 디스크 | 관리 디스크 |
| S3 버킷 | Cloud Storage 버킷 | Blob 컨테이너 |
| VPC | VPC 네트워크 | 가상 네트워크 |
| ARN | 리소스 이름 | 리소스 ID |
| 태그 | 라벨 | 태그 |

- [ ] **Step 3: 검사기 — 이제 앵커 유예를 뺀다**

Run: `python3 tools/check_tutorial.py aws_basics.html; echo "exit=$?"`
Expected: `OK aws_basics.html (섹션 18 · 퀴즈 15 · 데모 14)` · `exit=0`

**여기서 처음으로 플래그 없이 돌린다.** 히어로 지도의 링크 17개와 본문의 모든 상호참조가 실제 섹션을 가리켜야 한다. FAIL하면 어긋난 앵커를 전부 고친 뒤 진행한다.

- [ ] **Step 4: 커밋**

```bash
git add aws_basics.html
git commit -m "부록 A·B: 진짜 명령어와 다른 이름 같은 이야기

명령은 전부 읽기 전용이다. 부록 B는 이름만 맞추고 동작 설명은 넣지
않는다 — 두 클라우드는 이 문서의 근거 파일이 다루지 않았다."
```

---

## Task 19: `index.html`에 카드 추가

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `aws_basics.html`이 존재하고 검사기를 통과한 상태
- Produces: 없음

`index.html`은 지금 커밋되지 않은 변경이 없다(Task 1 시점 기준). 있다면 **카드 추가만 별도로 얹고 나머지는 건드리지 않는다.**

- [ ] **Step 1: 색 변수 추가**

`:root`의 시리즈 색 목록에 `--awsb:#34d399;`를 추가한다.

- [ ] **Step 2: 카드를 IAM 앞에 넣는다**

읽는 순서가 `aws_basics` → `iam_tutorial` → `aws_network_security`이므로, `iam_tutorial.html` 카드 **바로 앞**에 넣는다.

```html
<a class="card" href="aws_basics.html" style="--c:var(--awsb)">
  <div class="top">
    <span class="ic">🧩</span>
    <span class="no">AWS Basics</span>
    <span class="new">NEW</span>
  </div>
  <h2>AWS 기초 — 서버 한 대가 아홉 개로 쪼개지는 이야기</h2>
  <p>"<b>한 대를 주문했는데 콘솔에는 리소스가 아홉 개 생겨 있었다</b>"에서 출발합니다.
  온프렘에서 한 몸이던 CPU·디스크·랜카드가 AWS에서는 왜 따로 생기고 따로 죽고 따로 과금되는지를
  하나씩 해체한 다음, 그 부품으로 로드밸런서와 관리형 DB와 요금과 IaC를 다시 조립합니다.
  뒤의 AWS 문서 두 편이 <b>전제하고 시작하는 것</b>이 여기 있습니다.</p>
  <div class="tags"><i>계정</i><i>리전 · AZ</i><i>ARN</i><i>EC2</i><i>EBS</i><i>ENI</i><i>S3</i><i>ALB · NAT</i><i>RDS</i><i>컨테이너 · Lambda</i><i>요금</i><i>태그 · IaC</i></div>
  <span class="go">열어 보기 <span class="ar">→</span></span>
</a>
```

- [ ] **Step 3: 문서 수와 meta description을 고친다**

- `<span>🗂️ <b>7개 문서</b></span>` → `8개 문서`
- `meta description`의 목록 맨 앞에 "AWS 기초"를 넣는다

- [ ] **Step 4: 확인**

```bash
grep -c '8개 문서' index.html
grep -c 'aws_basics.html' index.html
python3 tools/check_tutorial.py aws_basics.html; echo "exit=$?"
```
Expected: `1`, `1`, `exit=0`

브라우저로 `index.html`을 열어 카드가 IAM 앞에 있고 색이 에메랄드이며 링크가 열리는지 확인한다.

- [ ] **Step 5: 커밋**

```bash
git add index.html
git commit -m "시리즈 인덱스: AWS 기초 카드를 IAM 앞에 추가

읽는 순서가 aws_basics → iam_tutorial → aws_network_security이므로
카드도 그 순서로 놓는다."
```

---

## Task 20: 최종 검수

**Files:**
- Modify: `aws_basics.html` (발견된 문제 수정)
- Create: `docs/superpowers/notes/2026-08-15-aws-basics-known-issues.md`

**Interfaces:**
- Consumes: 전부
- Produces: 남겨 둔 것 기록

- [ ] **Step 1: 구조 검사**

```bash
python3 tools/check_tutorial.py aws_basics.html; echo "exit=$?"
python3 tools/check_dead_css.py aws_basics.html
```
첫 번째는 `exit=0`이어야 한다. 두 번째는 보고용이고, 미사용 비율을 기록해 둔다.

- [ ] **Step 2: 외부 의존성 0 확인**

브라우저 개발자도구 Network 탭을 열고 `file://`로 새로 연다. **요청 0건**이어야 한다. 검사기가 정적으로도 보지만 실측을 한 번 한다.

- [ ] **Step 3: 저장소 키 격리 확인**

`aws_basics.html`을 열어 진행률을 만든 뒤, 같은 브라우저에서 `iam_tutorial.html`과 `aws_network_security.html`을 연다. **서로의 진행률이 섞이지 않아야 한다.**

```
localStorage에 awsbase:visited / awsbase:solved / awsbase:ckl 만 새로 생긴다
netsec: 와 iamtut: 키는 값이 변하지 않는다
```

- [ ] **Step 4: 문체 규범 훑기 — 누출 검사**

```bash
grep -n '다음은 \|다음 장에서는\|이 절에서는\|이 장에서는 .*를 다룹니다\|살펴보겠습니다\|알아보겠습니다' aws_basics.html
grep -n '열린 긴장\|군더더기 문장\|인지 리듬\|나열의 착지\|화제 테스트' aws_basics.html
```
Expected: 두 번째는 **0건**(규범의 표지어가 본문에 새면 안 된다). 첫 번째에 걸린 것은 하나씩 판정해 — 상황을 갱신하는 문장이면 남기고, 진행 예고면 지운다. 절 끝의 "다음은 ~를 본다"는 전부 지운다.

- [ ] **Step 5: 어미 3연속 검사**

각 장을 눈으로 읽으며 같은 어미가 세 문장 연속인 곳을 찾는다. 특히 `~입니다`가 몰리기 쉽다. 하나를 체언 종결이나 주저형, 연결어미로 바꾼다.

- [ ] **Step 6: 사실 대조 — 근거 파일과 본문을 맞춘다**

`docs/superpowers/notes/2026-08-15-aws-basics-facts.md`를 열고, 본문에서 **수치·기본값·최상급·"항상/절대"가 들어간 문장**을 전부 찾아 근거와 대조한다. 특히:

- 6장의 `DeleteOnTermination` 다섯 행이 표와 한 글자도 어긋나지 않는가
- 11장에 "Lambda는 15분이 최대"라는 표현이 없는가 (`grep -n '15분' aws_basics.html`)
- 4장에 파티션 개수가 숫자로 적혀 있지 않은가 (`grep -n '파티션.*[3-4]개\|세 개.*파티션\|네 개.*파티션' aws_basics.html`)
- 12장에 근거 없는 단가가 없는가 — 확인된 것은 퍼블릭 IPv4 $0.005/시, NAT GW $0.045/시 + $0.045/GB **둘뿐**이다
- 5장 퍼블릭 IP 재부팅 행이 "해제 사유 목록에 없다"로 되어 있고 "유지된다"로 단정하지 않았는가

근거가 없는데 쓴 문장이 있으면 **지우고 기록한다.** 완화해서 뭉개지 않는다.

- [ ] **Step 7: 회수 구조 확인**

spec §6의 표를 열고, 심은 곳과 거두는 곳이 실제로 본문에 있는지 행마다 확인한다. 한쪽만 있으면 채우거나 그 행을 포기하고 기록한다.

- [ ] **Step 8: 상호참조 링크 확인**

```bash
grep -o 'href="[a-z_]*\.html[^"]*"' aws_basics.html | sort -u
```
`iam_tutorial.html` `aws_network_security.html` 두 파일만 나와야 한다. 각 링크의 앵커가 대상 파일에 실제로 있는지 확인한다. **대상 파일은 읽기만 하고 수정하지 않는다.**

- [ ] **Step 9: 모바일 확인**

브라우저를 980px 아래로 줄이고 `☰ 목차`를 연다. **드로어 안의 항목이 눌려야 한다.** 복제 원본이 이 버그를 고친 유일한 파일이라 그대로 살아 있어야 하지만, CSS를 걷어내며 깨졌을 수 있다. 항목을 누르면 드로어가 닫히고 해당 섹션으로 이동해야 하며, 화면을 덮는 오버레이가 남지 않아야 한다.

- [ ] **Step 10: 접근성 확인**

- Tab만으로 모든 `.pick` `.tog` `.opt` `.term`에 닿고 포커스 링이 보인다
- `.tog`에 `aria-pressed`가 붙어 있다
- OS의 "동작 줄이기"를 켜면 트랜지션이 죽는다

- [ ] **Step 11: 남겨 둔 것을 기록한다**

`docs/superpowers/notes/2026-08-15-aws-basics-known-issues.md`를 만들고, 알고도 고치지 않은 것을 적는다. 최소한 다음을 판정해 기록한다.

- 사장 CSS의 최종 비율 (Task 1에서 걷어낸 뒤 남은 것)
- 밀도 파형 — 장별 글자 수를 재서 여섯 장 이상 연속으로 몰린 곳이 있는지
- 부록 B가 1차 출처 검증을 받지 않았다는 것
- 근거가 없어 비워 둔 자리 전부
- 기존 두 AWS 문서에서 이 문서로 거는 **역방향 링크가 아직 없다는 것** (퇴고 브랜치가 정리된 뒤 별건)
- `known-issues` §1의 모바일 드로어 버그가 다른 세 파일에 여전히 남아 있다는 것

```bash
python3 - <<'PY'
import re, pathlib
s = pathlib.Path('aws_basics.html').read_text(encoding='utf-8')
for m in re.finditer(r'<section id="([^"]+)"[^>]*>(.*?)</section>', s, re.S):
    text = re.sub(r'<[^>]+>', '', m.group(2))
    print(f'{m.group(1):16s} {len(text):6d}자')
PY
```

- [ ] **Step 12: 최종 검사와 커밋**

```bash
python3 tools/check_tutorial.py aws_basics.html; echo "exit=$?"
git add aws_basics.html docs/superpowers/notes/2026-08-15-aws-basics-known-issues.md
git commit -m "최종 검수: 사실 대조와 남겨 둔 것 기록

근거 파일과 본문의 수치를 행 단위로 맞추고, 문체 규범의 진행 예고 문장을
걷어냈다. 게시를 막지 않는다고 판정한 항목은 known-issues에 남긴다."
```

---

## 자체 검토 결과

계획을 다 쓴 뒤 spec과 대조했다. 고친 것을 기록해 둔다.

**1. 스펙 커버리지.** spec §5의 18개 섹션이 Task 2~18에 전부 배정됐다. §6 회수 구조 8행은 각각 심는 태스크와 거두는 태스크가 Interfaces에 명시돼 있다. §7 문체 규범은 Global Constraints와 Task 20 Step 4~5가 받는다. §8 구현 규약 13행은 Task 1과 Task 19가 나눠 받는다. §9 검증 11건은 이미 완료돼 각 장 태스크의 "근거 읽기"로 들어갔다. §10 완료 기준 9행은 Task 20의 Step 1~11에 대응한다.

**2. 빠졌던 것 하나를 채웠다.** spec §5의 5장이 "키 페어는 만들 때 받은 개인키를 다시 못 받는다"를 요구하는데 초안의 Task 7에 없었다. Step 1에 넣었다.

**3. 이름 일관성.** 데모 컨테이너 id를 계획 앞머리 표와 각 태스크의 코드 블록에서 대조했다. 3장의 출력 id가 표에서는 `azOut`인데 Task 5 코드에서 `azMapOut`으로 어긋나 있어 `azOut`으로 맞췄다. 아홉 개 목록의 키(`ec2` `ebs` `eni` `sg` `key` `subnet` `rtb` `igw` `eip`)는 Task 3의 `D9`와 히어로 표에서 같다.

**4. 검사기 기대값.** 각 태스크의 Expected 섹션 수·퀴즈 수·데모 수를 1부터 세어 맞췄다. 최종은 섹션 18 · 퀴즈 15 · 데모 14다. 데모가 15가 아닌 것은 히어로 자가진단이 `.diag`이지 `.demo`가 아니기 때문이고, 15장은 체크리스트만 두기 때문이다.

**5. 근거 없는 수치를 쓸 자리를 막았다.** Task 14(요금)가 금액 합계를 내려 하면 근거 없는 단가가 필요해진다. 합계를 내지 않고 "꺼도 나가는가"만 배지로 내도록 고쳤고, 쓸 수 있는 단가 두 개를 명시했다.
