# AWS 네트워크 보안 튜토리얼 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** SG·NACL·라우팅·Network Firewall·WAF·VPC Endpoint를 "관문의 순서 → 연동 구성" 2부 구성으로 다루는 단일 HTML 인터랙티브 튜토리얼 `aws_network_security.html`을 만든다.

**Architecture:** 기존 `iam_tutorial.html`의 골격(사이드바 · 자동 목차 · 스크롤스파이 진행률 · 용어사전 드로어 · 퀴즈 엔진 · `wirePicker` 데모 배선)을 그대로 복제하고 내용을 교체한다. 각 장은 `<section id data-title>` 하나이고, 각 데모는 `데이터 객체 + render(k) + wirePicker(...)` 형태의 IIFE 하나다. 외부 의존성은 0이며 `file://`로 열어도 완전히 동작해야 한다.

**Tech Stack:** 순수 HTML + CSS + 바닐라 JS (ES2020). 임베딩 Prism 1.29.0 (core + clike + bash + json). 빌드 도구 없음. 검사 스크립트만 Python 3 표준 라이브러리.

## Global Constraints

프로젝트 전체에 적용된다. 모든 태스크의 요구사항에 암묵적으로 포함된다.

- **외부 의존성 0.** CDN·웹폰트·원격 이미지·`fetch`·`XMLHttpRequest` 전면 금지. 리소스는 전부 인라인. (다른 튜토리얼 파일로 가는 상대경로 `<a href>`는 허용)
- **단일 파일.** 산출물은 `aws_network_security.html` 하나. `file://`로 열어 모든 기능이 동작해야 한다.
- **localStorage 접두어는 `netsec:`.** 키는 `netsec:visited`, `netsec:solved`, `netsec:ckl` 셋뿐. (`iamtut:`과 절대 충돌 금지)
- **언어는 한국어.** 시리즈 톤 — 존댓말 서술, 짧은 단정문, 오해를 먼저 깨고 사실을 세우는 순서.
- **접근성:** 모든 인터랙티브 요소에 `:focus-visible` 아웃라인, `prefers-reduced-motion: reduce` 시 트랜지션 무력화, 토글에 `aria-pressed`, 드로어에 `aria-expanded`.
- **시리즈 색상:** 이 문서의 강조색은 `--vpc:#fb7185` (로즈). `index.html` 카드에도 같은 값을 쓴다.
- **커밋 규칙:** 태스크마다 1커밋. 커밋 전 반드시 검사 스크립트가 **exit 0**으로 통과해야 한다.
  - Task 4~18 (문서를 증분으로 채우는 동안): `python3 tools/check_tutorial.py --allow-missing-anchors aws_network_security.html`
    히어로의 `.map-grid`가 아직 만들지 않은 섹션을 가리키므로 앵커 검사만 유예한다. **다른 검사는 전부 적용된다.**
  - Task 19 이후 (모든 섹션이 존재): 플래그 없이 `python3 tools/check_tutorial.py aws_network_security.html`
  - 어느 경우든 **exit 0이 게이트다.** `grep`으로 출력을 걸러 통과한 척하지 않는다.
- **건드리지 않을 것:** `index.html`과 `network_tutorial.html`에 이미 커밋되지 않은 작업 중 변경이 있다. `index.html`은 Task 20에서 **카드 추가만** 얹고, `network_tutorial.html`은 어떤 태스크에서도 열지 않는다.

## 파일 구조

| 파일 | 책임 | 태스크 |
|---|---|---|
| `docs/superpowers/notes/2026-08-12-aws-facts.md` | AWS 동작 사실 검증 결과(V1~V5)와 근거 URL | Task 1 |
| `tools/check_tutorial.py` | 단일 HTML 튜토리얼의 구조 불변식 검사기. 시리즈 7개 파일 전부에 재사용 가능 | Task 2 |
| `aws_network_security.html` | 산출물 본체. 18개 `<section>` (히어로 1 + 본문 15 + 부록 2) | Task 3~19 |
| `index.html` | 시리즈 인덱스에 카드 1장 추가 | Task 20 |

### `aws_network_security.html` 내부 구조

파일 안의 순서는 고정이다. 모든 태스크가 같은 자리에 끼워 넣는다.

```
<head>
  <style id="prism-theme">   … Task 3
  <style>                    … 디자인 시스템 (Task 3에서 완성, 이후 태스크는 장 전용 CSS만 append)
</head>
<body>
  <aside id="sidebar">       … Task 3
  <main id="content">
    <section id="intro">     … Task 4
    <section id="outside">   … Task 5
    … (장 순서대로)
    <section id="appendix-map"> … Task 19
  </main>
  <div id="glossary"> <div id="tooltip"> <div id="scrim">  … Task 3
  <script>Prism …</script>   … Task 3
  <script>
    const GLOSSARY = { … }   … Task 3에서 생성, 각 장 태스크가 항목 추가
    // @GLOSSARY_END
    유틸 · 학습 엔진          … Task 3
    /* 데모 N — 이름 */ IIFE  … 각 장 태스크가 파일 끝에 append
  </script>
</body>
```

**섹션 id와 목차 번호** (`data-title` 기준, 목차는 자동 생성되며 첫 섹션은 `·`, 이후 1부터 매겨진다):

| # | id | data-title | 태스크 |
|---|---|---|---|
| · | `intro` | 개요 | 4 |
| 1 | `outside` | 방화벽은 서버 밖에 | 5 |
| 2 | `vpc` | VPC 기초 | 6 |
| 3 | `route` | 경로가 곧 통제 | 7 |
| 4 | `sg` | Security Group | 8 |
| 5 | `nacl` | NACL | 9 |
| 6 | `order` | 관문의 순서 | 10 |
| 7 | `trace` | 어디서 막혔나 | 11 |
| 8 | `ref` | SG 참조 | 12 |
| 9 | `nfw` | Network Firewall | 13 |
| 10 | `waf` | WAF | 14 |
| 11 | `endpoint` | VPC Endpoint | 15 |
| 12 | `peering` | VPC 잇기 | 16 |
| 13 | `blueprint` | 3-tier 레퍼런스 | 17 |
| 14 | `pitfall` | 함정과 원칙 | 18 |
| 15 | `wrap` | 마무리 | 18 |
| 16 | `appendix-cli` | 부록 A · 진짜 명령어 | 19 |
| 17 | `appendix-map` | 부록 B · 다른 이름 | 19 |

**퀴즈 id** — 장마다 정확히 1개, 총 15개:
`q-outside` `q-vpc` `q-route` `q-sg` `q-nacl` `q-order` `q-trace` `q-ref` `q-nfw` `q-waf` `q-endpoint` `q-peering` `q-blueprint` `q-pitfall` `q-wrap`

**데모 컨테이너 id** — 총 14종:

| 장 | 데모 | 루트 id | 입력 id | 출력 id |
|---|---|---|---|---|
| 1 | iptables vs SG | `fwCmp` | `fwPicker` | `fwOut` |
| 2 | VPC 지도 | `vpcMap` | `vpcPicker` | `vpcOut` |
| 2 | CIDR 분할기 | `cidrCalc` | `cidrPicker` | `cidrOut` |
| 3 | 라우팅 시뮬레이터 | `routeSim` | `routePicker` | `routeOut` |
| 4 | SG 규칙 편집기 | `sgEditor` | `sgRules` / `sgProbe` | `sgOut` |
| 5 | SG vs NACL | `naclCmp` | `naclPicker` | `naclOut` |
| 6 | 관문 체인 | `chain` | `chainScenario` / `chainFault` | `chainStage` / `chainOut` |
| 7 | Flow Log 해부기 | `flowLog` | `flowPicker` | `flowOut` |
| 7 | 증상 판별 트리 | `triage` | `triagePicker` | `triageOut` |
| 8 | SG 참조 빌더 | `sgRef` | `sgRefPicker` | `sgRefOut` |
| 9 | 삽입 라우팅 | `nfwRoute` | `nfwPicker` | `nfwOut` |
| 10 | WAF 규칙 테스트 | `wafTest` | `wafPicker` | `wafOut` |
| 11 | Endpoint × IAM | `vpceEval` | `vpcePicker` / `iamPicker` | `vpceOut` |
| 13 | 종합 여정 재생기 | `journey` | `journeyPicker` | `journeyStage` / `journeyOut` |

---

## Task 1: AWS 동작 사실 검증 (V1~V5)

spec §8의 검증 항목 5건을 AWS 공식 문서로 확인한다. **V1이 뒤집히면 7장의 척추가 바뀌므로 반드시 먼저 한다.**

**Files:**
- Create: `docs/superpowers/notes/2026-08-12-aws-facts.md`
- Modify: `docs/superpowers/specs/2026-08-12-aws-network-security-tutorial-design.md` (§8 표에 결과 열 추가)

**Interfaces:**
- Consumes: 없음
- Produces: `docs/superpowers/notes/2026-08-12-aws-facts.md` — Task 11(7장), 13(9장), 14(10장), 15(11장), 16(12장)이 서술의 근거로 읽는다. 각 항목은 `## V1 …` 형태의 헤딩과 `**결론:**` / `**근거:**` (URL 포함) / `**튜토리얼 서술에 미치는 영향:**` 세 줄을 갖는다.

- [ ] **Step 1: V1 — VPC Flow Logs와 NACL/SG 차단의 기록 비대칭**

WebSearch/WebFetch로 AWS 공식 문서 "Logging IP traffic using VPC Flow Logs" 및 "Flow log record examples"를 확인하고 다음 네 가지를 각각 판정한다.

1. 인바운드가 **NACL**에 막혔을 때 ENI Flow Log에 레코드가 남는가? 남는다면 `ACCEPT`인가 `REJECT`인가?
2. 인바운드가 **SG**에 막혔을 때는?
3. 아웃바운드가 **NACL**에 막혔을 때 `ACCEPT`로 기록되는가?
4. 아웃바운드가 **SG**에 막혔을 때는?

특히 확인할 것: AWS 문서는 "보안 그룹은 상태 저장이므로 허용된 인바운드 트래픽의 응답은 아웃바운드 규칙과 무관하게 나가며, 이 경우 Flow Log의 `ACCEPT`/`REJECT` 표기가 실제 전달 여부와 어긋날 수 있다"는 취지의 단서를 단다. 그 정확한 문구를 인용해 둔다.

- [ ] **Step 2: V2 — VPC Peering 너머의 SG 참조**

"Update your security groups to reference peer security groups" 문서에서 확인:
- 같은 리전 peering에서만 가능한지, 리전 간(inter-region) peering에서는 불가한지
- Transit Gateway를 통한 연결에서는 어떤지 (SG 참조 지원 여부)
- 필요한 설정(`Allow DNS resolution`, 계정 간 조건 등)

- [ ] **Step 3: V3 — CloudFront origin-facing managed prefix list**

정확한 prefix list 이름 문자열, 사용 리전, ALB SG에 적용하는 방법, 그리고 **prefix list가 차지하는 SG 규칙 슬롯 수**(가중치)를 확인한다. 슬롯 가중치는 실무에서 규칙 한도에 걸리는 원인이라 10장에서 언급한다.

- [ ] **Step 4: V4 — Network Firewall 삽입 라우팅 구성**

"AWS Network Firewall example architectures" 문서에서 단일 AZ 인터넷 게이트웨이 구성의 정확한 라우팅 편집 절차를 확인한다.
- 방화벽 전용 서브넷이 별도로 필요한가
- IGW의 **edge association** 라우팅 테이블에 무엇을 넣는가
- 워크로드 서브넷 라우팅 테이블의 `0.0.0.0/0` 타깃은 무엇인가 (VPC endpoint id 형식)
- 이 세 개를 순서대로 적지 않으면 9장 데모의 정답 상태를 만들 수 없다.

- [ ] **Step 5: V5 — Gateway Endpoint 지원 서비스 범위**

Gateway형 Endpoint가 현재 지원하는 서비스 목록을 확인한다(S3, DynamoDB 외 추가되었는지). Interface형과의 과금·동작 차이도 한 줄로 정리한다.

- [ ] **Step 6: 노트 파일 작성**

`docs/superpowers/notes/2026-08-12-aws-facts.md`를 만들고 V1~V5를 각각 아래 형식으로 기록한다.

```markdown
# AWS 동작 사실 검증 — 2026-08-12

이 문서는 `aws_network_security.html` 서술의 근거다. 튜토리얼에서 단정문으로
쓰는 모든 AWS 동작은 여기에 근거가 있어야 한다.

## V1 — Flow Logs와 NACL/SG 차단의 기록 비대칭

**결론:** (확인한 내용을 여기 적는다)

**근거:**
- (문서 제목) — (URL)
- 인용: "(원문 문구)"

**튜토리얼 서술에 미치는 영향:** (7장을 어떻게 쓸 것인지)
```

- [ ] **Step 7: spec의 §8 표를 갱신**

`docs/superpowers/specs/2026-08-12-aws-network-security-tutorial-design.md`의 §8 표에 "결과" 열을 추가하고 각 행에 `확인됨` / `수정 필요 — (요지)`를 적는다. V1이 예상과 다르면 §5의 7장 서술도 함께 고친다.

- [ ] **Step 8: 커밋**

```bash
git add docs/superpowers/notes/2026-08-12-aws-facts.md docs/superpowers/specs/2026-08-12-aws-network-security-tutorial-design.md
git commit -m "AWS 동작 사실 검증(V1~V5) 결과 기록"
```

---

## Task 2: 구조 검사 스크립트

빌드 도구가 없는 저장소라 테스트 러너도 없다. 4000줄짜리 단일 HTML을 17번 증분 편집하는 동안 "내가 뭘 깨뜨렸나"를 눈으로 확인하는 건 실패한다. 검사기를 먼저 만들어 이후 모든 태스크의 게이트로 쓴다.

**Files:**
- Create: `tools/check_tutorial.py`

**Interfaces:**
- Consumes: 없음
- Produces: CLI `python3 tools/check_tutorial.py [--allow-missing-anchors] <파일...>`. 위반이 없으면 stdout에 `OK <파일> (섹션 N · 퀴즈 N · 데모 N)`을 찍고 exit 0. 위반이 있으면 `FAIL <파일>:` 아래에 `  - [검사이름] 설명` 줄을 나열하고 exit 1. Task 3~20의 모든 커밋 직전 단계가 이 명령을 호출한다.
- `--allow-missing-anchors`: 내부 앵커 검사만 건너뛴다. 문서를 장별로 증분 작성하는 동안 히어로의 목차가 아직 없는 섹션을 가리키기 때문이며, **이 플래그로도 나머지 검사는 전부 적용된다.** 플래그를 쓰면 OK 줄 끝에 `[앵커 검사 유예]`가 붙어 유예 사실이 출력에 남는다.

- [ ] **Step 1: 실패하는 테스트를 먼저 만든다**

검사기가 실제로 위반을 잡는지 확인할 고정 픽스처를 만든다. 파일: `tools/testdata/bad.html`

```html
<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<script src="https://cdn.example.com/x.js"></script>
</head><body>
<section id="a">없음</section>
<section id="a" data-title="중복">
  <a href="#nowhere">깨진 앵커</a>
  <span class="term" data-t="없는용어">용어</span>
  <div class="quiz" data-qid="q1" data-answer="z">
    <button class="opt" data-opt="a">A</button>
  </div>
</section>
<script>const GLOSSARY = { "있는용어": "설명" };
// @GLOSSARY_END
fetch('/x');
</script>
</body></html>
```

이 파일은 의도적으로 7가지를 위반한다 — 외부 script, `<title>` 없음, meta description 없음, `data-title` 없는 섹션, 중복 id, 깨진 내부 앵커, GLOSSARY에 없는 `data-t`, 존재하지 않는 `data-answer`, `fetch(` 호출.

- [ ] **Step 2: 검사기를 작성한다**

파일: `tools/check_tutorial.py`

```python
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
TERM_KEY = re.compile(r'class="term"[^>]*\bdata-t\s*=\s*"([^"]+)"')
GLOSSARY_BLOCK = re.compile(r'const\s+GLOSSARY\s*=\s*\{(.*?)//\s*@GLOSSARY_END', re.S)
GLOSSARY_KEY = re.compile(r'"([^"]+)"\s*:')
QUIZ_BLOCK = re.compile(r'<div\s+class="quiz"([^>]*)>(.*?)</div>\s*</section>', re.S)
DEMO_TAG = re.compile(r'class="demo"')


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
    if not gm:
        problems.append('[glossary] GLOSSARY 블록(… // @GLOSSARY_END)을 찾을 수 없음')
    for t in sorted(set(TERM_KEY.findall(src))):
        if t not in gkeys:
            problems.append(f'[glossary] GLOSSARY에 없는 용어: {t}')

    # 7. 퀴즈 정합성
    qids = []
    for attrs, body in QUIZ_BLOCK.findall(src):
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
```

- [ ] **Step 3: 픽스처로 검사기가 실패를 잡는지 확인**

Run: `python3 tools/check_tutorial.py tools/testdata/bad.html`
Expected: exit 1. 출력에 `[external]`, `[meta]`, `[id]`, `[section]`, `[anchor]`, `[glossary]`, `[quiz]` 태그가 **각각 최소 1줄씩** 나타나야 한다. 하나라도 빠지면 해당 검사가 동작하지 않는 것이므로 정규식을 고친다.

- [ ] **Step 3-1: 플래그가 앵커 검사만 유예하는지 확인**

Run: `python3 tools/check_tutorial.py --allow-missing-anchors tools/testdata/bad.html`
Expected: 여전히 exit 1이고, `[anchor]` 줄은 **사라지되** `[external]`·`[meta]`·`[id]`·`[section]`·`[glossary]`·`[quiz]`는 **그대로 남는다.**

이 플래그가 다른 검사까지 무력화하면 15개 태스크의 커밋 게이트가 통째로 무의미해진다. 반드시 확인한다.

Run: `python3 tools/check_tutorial.py --bogus tools/testdata/bad.html`
Expected: exit 2, `알 수 없는 옵션: --bogus`. 오타 난 플래그가 조용히 무시되면 안 된다.

- [ ] **Step 4: 기존 7개 파일에 돌려 오탐이 없는지 확인**

Run: `python3 tools/check_tutorial.py index.html https_tutorial.html iam_tutorial.html network_basics.html oauth2_tutorial.html rbac_tutorial.html`
Expected: 전부 `OK`.

`index.html`은 GLOSSARY가 없고 섹션도 없으므로 `[glossary] GLOSSARY 블록을 찾을 수 없음`이 뜬다. 이건 오탐이다 — **GLOSSARY 블록이 아예 없고 `class="term"`도 하나도 없으면 그 검사를 건너뛰도록** Step 2의 코드를 고친다:

```python
    if not gm and TERM_KEY.search(src):
        problems.append('[glossary] GLOSSARY 블록(… // @GLOSSARY_END)을 찾을 수 없음')
```

(`if not gm:` 줄을 위 줄로 교체한다.)

다른 오탐이 나오면 **검사기를 완화하지 말고 먼저 그게 진짜 문제인지 확인한다.** 기존 파일의 실제 결함이면 이 계획 범위 밖이므로 노트에 적어 두고 넘어간다.

- [ ] **Step 5: 커밋**

```bash
git add tools/check_tutorial.py tools/testdata/bad.html
git commit -m "단일 HTML 튜토리얼 구조 검사 스크립트 추가"
```

---

## Task 3: 문서 뼈대

`iam_tutorial.html`을 복제해 내용을 비우고, 이 문서 고유의 디자인 토큰과 학습 엔진만 남긴다. 이 태스크가 끝나면 **빈 껍데기가 브라우저에서 완전히 동작해야 한다** — 목차가 생기고, 진행률이 움직이고, 용어사전 드로어가 열리고, 모바일 메뉴가 열린다.

**Files:**
- Create: `aws_network_security.html` (from `iam_tutorial.html`)

**Interfaces:**
- Consumes: 없음
- Produces: 이후 모든 태스크가 의존하는 전역 심볼.
  - `$(sel, root?)`, `$$(sel, root?)` — querySelector / querySelectorAll 배열
  - `LS.get(key, default)`, `LS.set(key, value)` — `netsec:` 접두어 localStorage
  - `esc(str)` — HTML 이스케이프
  - `wirePicker(rootSelector, onPick)` — `.pick` 버튼 그룹 배선. `onPick(dataKey, buttonEl)` 호출, 클릭된 버튼에만 `.on` 부여
  - `wireTogs(rootSelector, onChange)` — `.tog` 토글 그룹 배선. `onChange(stateObject)` 호출, `stateObject[dataKey] = boolean` 반환
  - `updateProgress()` — 진행률 재계산
  - `GLOSSARY` — `{ 용어: "설명" }` 객체. 각 장 태스크가 항목을 추가한다
  - `markVisited(id)`, `solved` (Set), `visited` (Set)

- [ ] **Step 1: 복제**

```bash
cp iam_tutorial.html aws_network_security.html
```

- [ ] **Step 2: 헤드 교체**

`<title>`과 `<meta name="description">`을 교체한다.

```html
<title>AWS 네트워크 보안 튜토리얼 — SG·NACL·방화벽이 엮이는 순서</title>
<meta name="description" content="SG를 다 열었는데 왜 timeout인가에서 출발하는 AWS 네트워크 보안 인터랙티브 튜토리얼. Security Group·NACL·라우팅·Network Firewall·WAF·VPC Endpoint가 하나의 패킷 앞에서 어떤 순서로 엮이는지 직접 눌러 확인합니다.">
```

- [ ] **Step 3: 디자인 토큰 교체**

`:root` 블록에서 강조색을 로즈 계열로 바꾸고, **관문별 고정 색**을 추가한다. 이 색은 13개 데모 전부에서 같은 의미로 쓰인다 — 색이 흔들리면 문서 전체의 시각적 일관성이 무너지므로 이후 태스크에서 임의의 색을 쓰지 않는다.

```css
  --accent:    #fb7185;   /* 메인(로즈) */
  --accent-2:  #f472b6;   /* 보조(핑크) */

  /* 관문 고정 색 — 모든 데모에서 동일하게 사용 */
  --g-route:   #fbbf24;   /* 라우팅 테이블 · IGW · NAT */
  --g-nacl:    #38bdf8;   /* NACL */
  --g-sg:      #34d399;   /* Security Group */
  --g-fw:      #c084fc;   /* Network Firewall */
  --g-waf:     #f97316;   /* WAF */
  --g-os:      #94a3b8;   /* OS · 앱 */
```

기존 `--client` / `--server` / `--router` / `--iam-pb` 변수는 이 문서에서 쓰지 않으므로 삭제한다. `--ok` / `--warn` / `--bad` / `--purple`은 그대로 둔다.

- [ ] **Step 4: 저장소 접두어 교체**

`iamtut:` 문자열 3곳을 전부 `netsec:`으로 바꾼다.

```bash
grep -c 'iamtut:' aws_network_security.html   # 3이 나와야 한다
```

교체 후 다시 세어 0이어야 한다.

- [ ] **Step 5: 사이드바 브랜드 교체**

```html
    <div class="brand">
      <div class="logo"><span class="dot"></span> VPC·GATE</div>
      <h1>AWS 네트워크 보안 튜토리얼</h1>
      <div class="sub">SG · NACL · 라우팅 · Firewall · WAF · Endpoint</div>
    </div>
```

- [ ] **Step 6: 본문 비우기**

`<main id="content">` 안의 모든 `<section>`을 지우고 자리표시자 하나만 남긴다.

```html
  <main id="content">
    <section id="intro" data-title="개요" class="hero">
      <h2 class="sec-title">뼈대 확인용 자리표시자</h2>
    </section>
  </main>
```

- [ ] **Step 7: GLOSSARY 비우기**

`const GLOSSARY = {` 와 `// @GLOSSARY_END` 사이의 모든 항목을 지우고, 이 문서에서 확실히 쓸 기본 항목만 남긴다. 각 장 태스크가 여기에 추가한다.

```js
const GLOSSARY = {
  "ENI":  "Elastic Network Interface. EC2·RDS·Lambda 등에 붙는 가상 랜카드입니다. Security Group이 실제로 붙는 자리는 인스턴스가 아니라 이 ENI예요.",
  "CIDR": "192.168.0.0/24 처럼 'IP 주소 + 프리픽스 길이'로 주소 범위를 나타내는 표기법. /24는 앞 24비트가 고정이라는 뜻이라 256개 주소를 가리킵니다.",
  "상태 유지": "stateful. 나간 요청을 기억해 두었다가 그 응답은 규칙 검사 없이 통과시키는 방식. Security Group이 이렇게 동작합니다.",
  "무상태": "stateless. 오가는 패킷을 각각 독립적으로 검사하는 방식. NACL이 이렇게 동작해서, 응답 트래픽을 위한 규칙을 따로 열어야 합니다.",
  // @GLOSSARY_END
};
```

**주의:** `// @GLOSSARY_END` 마커는 검사 스크립트가 찾는 표식이다. 반드시 닫는 중괄호 **앞**에 있어야 하고 지우면 안 된다.

- [ ] **Step 8: 데모 코드 제거**

`/* ============ 데모 N — ... */` 주석으로 시작하는 IIFE를 전부 삭제한다. `유틸 · 학습 엔진` 블록(목차 생성 · 스크롤스파이 · 진행률 · 툴팁 · 퀴즈 · 용어사전 드로어 · `wireTogs` · `wirePicker`)까지가 남길 경계다.

- [ ] **Step 9: IAM 전용 CSS 제거**

`<style>` 안에서 이 문서에 없는 컴포넌트의 규칙을 지운다: `.arn-seg`, `.arn-info`, `.pol-key`, `.org-node`, `.stack-row`, `#svcSteps`, `.persona-grid`, `.persona`. `:focus-visible` 셀렉터 목록에서도 해당 클래스를 뺀다.

**남길 것:** `.demo` `.demo-tag` `.picker` `.pick` `.tog` `.verdict` `.vmodel` `.vwhy` `.vres` `.callout`(`.why` `.warn` `.key` `.tip` `.std` 변종 포함) `.quiz` `.q-head` `.q` `.opt` `.mk` `.explain` `.kv` `.cmp2` `.cmp-col` `.cc-h` `.cc-t` `.myth` `.m-row` `.m-x` `.m-txt` `.oneline` `.ol-ic` `.ol-t` `.ol-b` `.chips` `.chip` `.map-grid` `.map-card` `.diag` `.d-item` `.d-txt` `.d-yes` `.diag-result` `.ckl` `.ck` `.cb` `.ct` `.ck-score` `.flow-step` `.term` `.link` `.lvl` `.sec-head` `.kicker` `.dim` `.mono` — 전부 이후 태스크에서 쓴다.

지우기 전에 확인하는 방법: 삭제 후보 클래스를 `grep -c 'CLASSNAME' aws_network_security.html`으로 세어, **CSS 규칙 1건 외에 본문 사용처가 없을 때만** 지운다.

- [ ] **Step 10: Prism에 JSON 문법 추가**

이 문서는 SG 규칙·Endpoint 정책·IAM 정책을 JSON으로 보여준다. Prism bash 정의 뒤, 즉 `Prism.languages.shell=Prism.languages.bash}(Prism);` 다음 줄에 아래를 그대로 추가한다.

```js
Prism.languages.json={property:{pattern:/(^|[^\\])"(?:\\.|[^\\"\r\n])*"(?=\s*:)/,lookbehind:!0,greedy:!0},string:{pattern:/(^|[^\\])"(?:\\.|[^\\"\r\n])*"(?!\s*:)/,lookbehind:!0,greedy:!0},comment:{pattern:/\/\/.*|\/\*[\s\S]*?(?:\*\/|$)/,greedy:!0},number:/-?\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/i,punctuation:/[{}[\],]/,operator:/:/,boolean:/\b(?:false|true)\b/,null:{pattern:/\bnull\b/,alias:"keyword"}};
```

- [ ] **Step 11: 검사 통과 확인**

Run: `python3 tools/check_tutorial.py aws_network_security.html`
Expected: `OK aws_network_security.html (섹션 1 · 퀴즈 0 · 데모 0)`

`[anchor]` 위반이 나오면 본문을 비우면서 남은 `href="#..."` 링크가 사이드바나 푸터에 있는 것이다. 지운다.

- [ ] **Step 12: 브라우저 확인**

```bash
open aws_network_security.html
```

확인할 것 — 하나라도 안 되면 다음 태스크로 넘어가지 않는다:
1. 사이드바에 "개요" 목차 항목 1개가 생긴다
2. 진행률이 0%가 아닌 값(100%)으로 표시된다 (섹션 1개 중 1개 방문)
3. `📖 용어 사전` 버튼을 누르면 드로어가 열리고 4개 항목이 보인다
4. 드로어 검색창에 "무상태"를 치면 1개만 남는다
5. `Esc`로 드로어가 닫힌다
6. `↺ 초기화` → 확인 → 새로고침 후에도 오류가 없다
7. 브라우저 개발자도구 콘솔에 오류가 0건이다
8. 개발자도구 Network 탭에 이 파일 자신 말고 요청이 0건이다

- [ ] **Step 13: 커밋**

```bash
python3 tools/check_tutorial.py aws_network_security.html && \
git add aws_network_security.html && \
git commit -m "AWS 네트워크 보안 튜토리얼: 문서 뼈대"
```

---

## Task 4: 히어로 — "다 열었는데 왜 timeout인가"

**Files:**
- Modify: `aws_network_security.html` (`<section id="intro">` 교체, GLOSSARY 항목 추가, 데모 1 IIFE 추가)

**Interfaces:**
- Consumes: Task 3의 `$`, `$$`, `wirePicker`, `GLOSSARY`
- Produces: `#diag` 자가진단 위젯(가중치 합산 → 추천 학습 경로). Task 18의 15장이 이 결과를 회수한다. `.map-grid` 안의 `href="#..."`는 Task 5~19가 만들 섹션 id를 미리 가리키므로 **Task 19가 끝날 때까지 검사기의 `[anchor]` 위반이 발생한다** — Step 5 참조.

- [ ] **Step 1: 히어로 섹션 작성**

`<section id="intro">`을 아래 구조로 채운다. 각 덩어리의 내용은 아래 지정을 따른다.

1. `.kicker`: `네트워크를 아는 개발자 → 클라우드 경계 설계자`
2. `<h2 class="sec-title">`: `다 열었는데<br>왜 timeout인가`
3. `.lead` 2문단 — 증상 서술:
   - EC2에 웹서버를 띄우고, SG 인바운드를 `0.0.0.0/0`의 80번으로 열었다. `curl`은 60초를 기다리다 죽는다. SG를 다시 봐도 분명히 열려 있다.
   - "버그가 아닙니다. **패킷이 SG 앞에 도착조차 못 한 것**일 수 있어요."
4. 일반 문단 — 이 문서의 논지: SG 하나만 보는 습관이 문제고, 필요한 건 **패킷이 통과해야 하는 관문의 목록과 순서**라는 그림. `iam_tutorial.html`이 API 호출에 대해 한 일을 이 문서가 패킷에 대해 한다고 한 줄로 잇는다.
5. `.chips` 5개: `🧱 관문의 순서`로 시작해 spec §5의 성격을 요약
6. `.callout.why` — "이 튜토리얼의 한 문장":
   > 네트워크 보안을 안다는 것은 SG 규칙을 쓸 줄 안다는 뜻이 아닙니다. **패킷 하나가 통과해야 하는 관문의 목록과 그 순서**, 그리고 **각 관문이 막았을 때 내가 보게 되는 증상**을 짝지을 수 있다는 뜻이에요.
7. `<h3>🩺 시작 전 30초 자가진단</h3>` + `.diag` 위젯 (Step 2)
8. `<h3>☁️ 우리의 무대 — 나루 클라우드 주문 서비스</h3>` — `iam_tutorial.html`의 세계관을 잇는다는 한 줄 + `<a class="link" href="iam_tutorial.html">` 링크. prod 계정의 3-tier 구성을 `.kv` 목록으로:
   - `ALB` → 퍼블릭 서브넷 2개(AZ-a/AZ-c), 인터넷에서 443을 받는다
   - `앱 EC2` → 프라이빗 서브넷, ALB에서만 8080을 받는다
   - `RDS` → 격리 서브넷, 앱에서만 5432를 받는다
   - `NAT GW` → 앱이 외부 API를 부를 때만 쓰는 나가는 문
9. `<h3>무엇을 다루나</h3>` + `.map-grid` (Step 3)
10. `.callout.tip` — "읽는 법": 🟢 필수 / 🔵 심화 표시 설명, 2장은 VPC를 아는 사람은 건너뛰어도 된다는 안내, 진행률 자동 저장 안내

- [ ] **Step 2: 자가진단 위젯 HTML**

```html
      <div class="diag" id="diag">
        <div class="d-item"><div class="d-txt">접속이 안 될 때 일단 <b>SG를 <code>0.0.0.0/0</code>으로 넓혀</b> 본 적이 있다</div><button class="pick d-yes" data-w="3">그렇다</button></div>
        <div class="d-item"><div class="d-txt"><b>timeout과 connection refused</b>가 각각 무엇을 뜻하는지 구분해 말하기 어렵다</div><button class="pick d-yes" data-w="3">그렇다</button></div>
        <div class="d-item"><div class="d-txt">NACL을 <b>직접 만들어 본 적이 없다</b> (기본값 그대로 쓴다)</div><button class="pick d-yes" data-w="2">그렇다</button></div>
        <div class="d-item"><div class="d-txt">SG 규칙의 source에 <b>다른 SG를 넣을 수 있다</b>는 걸 몰랐다</div><button class="pick d-yes" data-w="2">그렇다</button></div>
        <div class="d-item"><div class="d-txt">"<b>퍼블릭 서브넷</b>"이 무엇으로 결정되는지 한 문장으로 답하기 어렵다</div><button class="pick d-yes" data-w="2">그렇다</button></div>
        <div class="d-item"><div class="d-txt">운영 중인 VPC의 <b>아웃바운드를 제한해 본 적이 없다</b></div><button class="pick d-yes" data-w="1">그렇다</button></div>
        <div class="diag-result" id="diagResult"></div>
      </div>
```

- [ ] **Step 3: 지도 그리드 HTML**

```html
      <div class="map-grid">
        <a class="map-card" href="#outside"><div class="ic">🧱</div><div class="tt">1 · 서버 밖의 방화벽</div><div class="dd">tcpdump에 안 잡힌다</div></a>
        <a class="map-card" href="#vpc"><div class="ic">🗺️</div><div class="tt">2 · VPC 기초</div><div class="dd">발판 · 건너뛰기 가능</div></a>
        <a class="map-card" href="#route"><div class="ic">🧭</div><div class="tt">3 · 경로가 곧 통제</div><div class="dd">라우팅·IGW·NAT</div></a>
        <a class="map-card" href="#sg"><div class="ic">🛡️</div><div class="tt">4 · Security Group</div><div class="dd">상태 유지 검문소</div></a>
        <a class="map-card" href="#nacl"><div class="ic">🧊</div><div class="tt">5 · NACL</div><div class="dd">무상태 검문소</div></a>
        <a class="map-card" href="#order"><div class="ic">⚖️</div><div class="tt">6 · 관문의 순서</div><div class="dd">전체 체인</div></a>
        <a class="map-card" href="#trace"><div class="ic">🔍</div><div class="tt">7 · 어디서 막혔나</div><div class="dd">Flow Logs·증상</div></a>
        <a class="map-card" href="#ref"><div class="ic">🔗</div><div class="tt">8 · SG 참조</div><div class="dd">IP가 아니라 신원으로</div></a>
        <a class="map-card" href="#nfw"><div class="ic">🚧</div><div class="tt">9 · Network Firewall</div><div class="dd">경유시키는 통제</div></a>
        <a class="map-card" href="#waf"><div class="ic">🌊</div><div class="tt">10 · WAF</div><div class="dd">연결된 뒤에 보는 관문</div></a>
        <a class="map-card" href="#endpoint"><div class="ic">🔒</div><div class="tt">11 · VPC Endpoint</div><div class="dd">IAM과 만나는 지점</div></a>
        <a class="map-card" href="#peering"><div class="ic">🕸️</div><div class="tt">12 · VPC 잇기</div><div class="dd">Peering·TGW</div></a>
        <a class="map-card" href="#blueprint"><div class="ic">🏗️</div><div class="tt">13 · 3-tier 레퍼런스</div><div class="dd">전부 합치기</div></a>
        <a class="map-card" href="#pitfall"><div class="ic">🧨</div><div class="tt">14 · 함정과 원칙</div><div class="dd">아웃바운드·SSH</div></a>
        <a class="map-card" href="#wrap"><div class="ic">🏁</div><div class="tt">15 · 마무리</div><div class="dd">체크리스트</div></a>
        <a class="map-card" href="#appendix-cli"><div class="ic">⌨️</div><div class="tt">부록 A</div><div class="dd">진짜 명령어</div></a>
        <a class="map-card" href="#appendix-map"><div class="ic">🗺️</div><div class="tt">부록 B</div><div class="dd">GCP·Azure·온프렘</div></a>
      </div>
```

- [ ] **Step 4: 자가진단 JS 추가**

`<script>` 끝에 추가한다.

```js
/* ============================================================
   데모 1 — 히어로 자가진단
   ============================================================ */
(function(){
  const diag = $('#diag'); if(!diag) return;
  const res = $('#diagResult');
  function update(){
    const on = $$('.d-yes.on', diag);
    const score = on.reduce((s,x)=>s+(+x.dataset.w), 0);
    let msg;
    if(score===0) msg = "해당하는 항목을 눌러보세요. 하나도 없다면 이미 감각이 잡혀 있는 겁니다 — <b>6장(관문의 순서)</b>과 <b>11장(Endpoint)</b>부터 골라 읽어도 좋아요.";
    else if(score>=9) msg = "<b>🟢 처음부터 순서대로 가는 게 빠릅니다.</b> 지금은 '되게 만드는 법'만 있고 '왜 안 되는지 아는 법'이 없는 상태예요. <b>3장(경로) → 4·5장(SG·NACL) → 6장(순서)</b>이 이 문서의 심장입니다.";
    else if(score>=5) msg = "<b>🟢 구조를 잡을 때입니다.</b> 개별 규칙은 쓰지만 순서가 안 잡힌 단계예요. <b>5장(NACL의 함정)·6장(관문의 순서)·7장(진단)</b>이 특히 도움이 됩니다.";
    else msg = "<b>🔵 기초는 갖춰져 있네요.</b> <b>8장(SG 참조)·9장(Network Firewall)·11장(Endpoint)</b> 같은 연동 쪽부터 보셔도 좋습니다.";
    res.innerHTML = msg + ` <span class="dim">(체크 ${on.length}개 · 가중치 ${score})</span>`;
    res.classList.add('show');
  }
  $$('.d-yes', diag).forEach(b => b.addEventListener('click', () => { b.classList.toggle('on'); update(); }));
})();
```

- [ ] **Step 5: 검사 실행**

`.map-grid`가 아직 만들지 않은 섹션 17개를 가리키므로, 이 태스크부터 Task 18까지는 앵커 검사를 유예한다.

Run: `python3 tools/check_tutorial.py --allow-missing-anchors aws_network_security.html`
Expected: **exit 0**, `OK aws_network_security.html (섹션 1 · 퀴즈 0 · 데모 0) [앵커 검사 유예]`

플래그 없이 돌리면 FAIL이 나오는 게 정상이다 — Task 19에서 모든 섹션이 생기면 플래그 없이도 통과한다.

- [ ] **Step 6: 브라우저 확인**

1. 자가진단 항목을 3개 누르면 결과 문단이 나타나고 가중치 합계가 맞다
2. 다시 누르면 해제되고 점수가 줄어든다
3. 6개를 전부 누르면 가중치 13 → "처음부터 순서대로" 메시지가 나온다
4. 콘솔 오류 0건

- [ ] **Step 7: 커밋**

```bash
git add aws_network_security.html
git commit -m "AWS 네트워크 보안 튜토리얼: 히어로와 자가진단"
```

---

## 장 태스크 공통 절차 (Task 5~19)

Task 5부터 19까지는 전부 같은 모양이다. 각 태스크의 Step은 아래 6개이며, 태스크 본문은 **각 Step에 들어갈 내용만** 지정한다.

1. `<section>` HTML을 `<main>` 안 지정된 위치에 추가
2. 데모 IIFE를 `<script>` 끝에 추가 (데모가 있는 장만)
3. 새 용어를 `GLOSSARY`에 추가 (`// @GLOSSARY_END` 앞)
4. 검사: `python3 tools/check_tutorial.py --allow-missing-anchors aws_network_security.html` → **exit 0** (`OK … [앵커 검사 유예]`)
5. 브라우저 확인: 해당 장의 데모를 전부 눌러보고 콘솔 오류 0건
6. 커밋: `git add aws_network_security.html && git commit -m "AWS 네트워크 보안 튜토리얼: N장 <제목>"`

**섹션 껍데기는 항상 이 모양이다:**

```html
    <section id="<id>" data-title="<data-title>">
      <div class="sec-head">
        <div class="kicker"><번호> · <한 단어></div>
        <h2 class="sec-title"><이모지> <제목> <span class="lvl must">🟢 필수</span></h2>
      </div>
      …본문…
      <div class="oneline">
        <div class="ol-ic"><이모지></div>
        <div><div class="ol-t"><번호>장 한 줄 요약</div><div class="ol-b">…</div></div>
      </div>
      <div class="quiz" data-qid="<qid>" data-answer="<정답>">…</div>
    </section>
```

심화 장은 `<span class="lvl adv">🔵 심화</span>`를 쓴다.

**데모 껍데기는 항상 이 모양이다:**

```html
      <div class="demo">
        <span class="demo-tag"><데모 이름></span>
        <p style="margin:0 0 4px"><한 줄 안내></p>
        <div class="picker" id="<입력 id>">
          <button class="pick on" data-k="<키>">…</button>
        </div>
        <div id="<출력 id>"></div>
      </div>
```

---

## Task 5: 1장 — 클라우드의 방화벽은 서버 안에 없다

**Files:**
- Modify: `aws_network_security.html` (`#intro` 뒤에 `<section id="outside">` 추가)

**Interfaces:**
- Consumes: Task 3의 `wirePicker`, `esc`, `$`
- Produces: 없음. 7장이 이 장의 "관측 가능성" 논지를 회수하지만 코드 의존은 없다.

**섹션 헤더:** kicker `01 · 출발`, 제목 `🧱 클라우드의 방화벽은 <span style="color:var(--accent)">서버 안</span>에 없다`, 🟢 필수

- [ ] **Step 1: 본문 작성**

이 순서로 쓴다.

1. `.lead`: "리눅스에서 방화벽을 다뤄 본 사람이라면 `iptables -L`이 손에 붙어 있을 겁니다. 클라우드에서 그 습관이 제일 먼저 배신합니다."
2. `<h3>🔪 검문은 OS 밖에서 끝난다</h3>` — `iptables`는 커널의 netfilter 훅에서 동작하므로 패킷이 이미 랜카드를 통과해 커널에 들어온 뒤다. SG는 ENI 층, 즉 **인스턴스의 가상 랜카드 앞**에서 판정한다. `network_basics.html`의 netfilter 장으로 링크(`<a class="link" href="network_basics.html">`).
3. `.callout.key` — 결정타:
   > **SG가 버린 패킷은 `tcpdump`에 잡히지 않습니다.** 인스턴스 안에서 아무리 들여다봐도 그 패킷은 오지 않은 것과 구별할 수 없어요. "서버에 들어가서 확인해 보자"가 클라우드에서 통하지 않는 첫 번째 이유입니다.
4. 데모 (Step 2)
5. `.myth` — 오해 격파:
   - ✕ SG는 `iptables`를 클라우드가 대신 돌려주는 것이다
   - ✓ **적용 지점이 다르다.** `iptables`는 OS 안, SG는 OS 밖이다. 그래서 둘은 겹쳐서 동작하고, **양쪽 다 열려야 통과한다.** EC2 안의 `firewalld`나 `ufw`를 끄지 않았다면 SG만 열어도 막힌다.
6. `<h3>🧩 통제가 붙을 수 있는 자리</h3>` — 이후 장의 예고. `.kv`로:
   - 엣지 — CloudFront·Shield·WAF (10장)
   - VPC 경계 — IGW·NAT·Network Firewall (3·9장)
   - 서브넷 — 라우팅 테이블·NACL (3·5장)
   - ENI — Security Group (4장)
   - 서비스 진입점 — VPC Endpoint 정책 (11장)
   - OS·앱 — `iptables`·바인딩 주소 (이 장)
7. `.oneline` 요약: 클라우드의 검문소는 **내 OS 밖**에 있다. 그래서 막혔을 때 서버 안에서는 아무 증거도 나오지 않고, 진단 도구부터 달라져야 한다.

- [ ] **Step 2: 데모 — "같은 차단, 다른 흔적"**

HTML:

```html
      <div class="demo" id="fwCmp">
        <span class="demo-tag">같은 차단, 다른 흔적</span>
        <p style="margin:0 0 4px">80번 포트로 오는 요청을 네 가지 방법으로 막아봅니다. 클라이언트가 보는 것과, 서버 안에서 보이는 것이 어떻게 달라지는지 확인하세요.</p>
        <div class="picker" id="fwPicker">
          <button class="pick on" data-k="iptdrop">🐧 iptables DROP</button>
          <button class="pick" data-k="iptreject">🐧 iptables REJECT</button>
          <button class="pick" data-k="sg">🛡️ SG 미허용</button>
          <button class="pick" data-k="nacl">🧊 NACL deny</button>
        </div>
        <div id="fwOut"></div>
      </div>
```

JS:

```js
/* ============================================================
   데모 2 — 같은 차단, 다른 흔적 (1장)
   ============================================================ */
(function(){
  const out = $('#fwOut'); if(!out) return;
  const D = {
    iptdrop: {
      where: "OS 안 (커널 netfilter)", c: "var(--g-os)",
      client: "60초쯤 기다리다 <b>timeout</b>",
      dump: "<b style='color:var(--ok)'>✅ 보인다</b> — SYN이 랜카드까지 도착했고, 커널이 그걸 버린 것이다",
      log: "<code>iptables -j LOG</code>를 걸어두면 서버 로그에 남는다",
      note: "패킷은 <b>서버까지 왔다</b>. 인스턴스에 들어가면 <code>tcpdump -i any port 80</code>으로 SYN이 계속 재전송되는 걸 볼 수 있고, <code>iptables -L -n -v</code>의 카운터도 올라갑니다. 증거가 서버 안에 있어요."
    },
    iptreject: {
      where: "OS 안 (커널 netfilter)", c: "var(--g-os)",
      client: "즉시 <b>connection refused</b>",
      dump: "<b style='color:var(--ok)'>✅ 보인다</b> — SYN이 들어오고 RST가 나가는 게 함께 찍힌다",
      log: "위와 동일",
      note: "DROP과 REJECT의 차이가 <b>클라이언트가 기다리는 시간</b>을 가릅니다. REJECT는 RST를 돌려주니 즉시 끝나고, DROP은 침묵하니 재전송을 반복하다 타임아웃합니다. 이 구분이 <a class='link' href='#trace'>7장 진단</a>의 첫 갈래가 돼요."
    },
    sg: {
      where: "OS 밖 (ENI 층)", c: "var(--g-sg)",
      client: "60초쯤 기다리다 <b>timeout</b>",
      dump: "<b style='color:var(--bad)'>❌ 안 보인다</b> — 패킷이 인스턴스에 도달하지 않았다",
      log: "서버에는 아무 기록도 없다. <b>VPC Flow Logs</b>에 <code>REJECT</code>로 남는다",
      note: "여기가 리눅스 감각과 갈라지는 지점입니다. 인스턴스 안에서는 <b>아무 일도 일어나지 않은 것과 구별할 수 없어요</b>. 방화벽이 막았는지, 애초에 요청이 오지 않았는지, 라우팅이 없었는지 — 서버 안의 증거로는 셋을 못 가릅니다. 증거를 <b>VPC 쪽</b>에서 찾아야 합니다."
    },
    nacl: {
      where: "서브넷 경계 (ENI보다 바깥)", c: "var(--g-nacl)",
      client: "60초쯤 기다리다 <b>timeout</b>",
      dump: "<b style='color:var(--bad)'>❌ 안 보인다</b>",
      log: "서버에는 없고, <b>VPC Flow Logs에 <code>REJECT</code></b> — SG가 막았을 때와 <b>똑같이</b> 보인다",
      note: "여기가 함정입니다. SG가 막든 NACL이 막든 <b>Flow Log에는 똑같이 <code>REJECT</code> 한 줄</b>만 남아요. 로그만 보고 둘을 가릴 수 없습니다. <br><br>구별되는 경우는 따로 있는데, <b>응답이 막힐 때</b>입니다 — 그때만 <code>ACCEPT</code> 다음에 <code>REJECT</code>가 짝으로 남고, <b>SG는 상태 저장이라 그 조합을 원리상 만들 수 없어요.</b> <a class='link' href='#trace'>7장</a>에서 이 신호를 진단 도구로 씁니다."
    }
  };
  function render(k){
    const d = D[k];
    out.innerHTML =
      `<div class="kv" style="margin-top:12px">
         <dt>적용 지점</dt><dd><b style="color:${d.where && d.c}">${esc(d.where)}</b></dd>
         <dt>클라이언트가 보는 것</dt><dd>${d.client}</dd>
         <dt>서버에서 tcpdump</dt><dd>${d.dump}</dd>
         <dt>어디에 기록되나</dt><dd>${d.log}</dd>
       </div>
       <div class="callout why" style="margin-bottom:0"><p style="margin:0">${d.note}</p></div>`;
  }
  wirePicker('#fwPicker', render);
  render('iptdrop');
})();
```

- [ ] **Step 3: 용어 추가**

```js
  "netfilter": "리눅스 커널 안에서 패킷을 검사·변환하는 프레임워크. iptables·nftables는 여기에 규칙을 등록하는 도구입니다. 커널 안이라는 점이 클라우드의 SG와 결정적으로 다릅니다.",
  "Flow Logs": "VPC Flow Logs. ENI를 오간 트래픽의 요약을 5분(또는 1분) 단위로 남기는 로그. 패킷 내용은 없고 5-tuple과 ACCEPT/REJECT만 남습니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-outside"`, `data-answer="c"`

> 질문: EC2에 접속이 안 되어 인스턴스에 들어가 `tcpdump -i any port 80`을 걸었더니 아무것도 찍히지 않았다. 이때 **배제할 수 있는** 원인은?
>
> - A. SG 인바운드에 80이 없다
> - B. 서브넷 라우팅 테이블에 IGW가 없다
> - C. **인스턴스 안의 `iptables`가 DROP하고 있다**
> - D. NACL이 80을 거부하고 있다
>
> 해설: **정답 C.** `iptables`는 OS 안에서 동작하므로, 그게 막았다면 패킷은 이미 랜카드를 통과해 `tcpdump`에 **찍힌 뒤** 버려집니다. 아무것도 안 찍혔다는 건 패킷이 인스턴스 밖에서 사라졌다는 뜻이라 A·B·D가 전부 살아 있어요.

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

버튼 4개를 눌러 `.kv` 4행과 `.callout`이 매번 바뀌는지 확인한다.

---

## Task 6: 2장 — VPC 기초 (발판)

**Files:**
- Modify: `aws_network_security.html` (`#outside` 뒤에 `<section id="vpc">` 추가)

**Interfaces:**
- Consumes: Task 3의 `wirePicker`, `esc`
- Produces: 없음

**섹션 헤더:** kicker `02 · 발판`, 제목 `🗺️ VPC 기초 — <span style="color:var(--accent)">발판만</span> 깔고 간다`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.callout.tip` 을 **맨 앞에** 둔다: "이 장은 본론이 아니라 발판입니다. VPC를 만들어 본 적이 있다면 마지막 오해 격파만 읽고 <a class='link' href='#route'>3장</a>으로 넘어가세요."
2. `<h3>📦 VPC는 내가 빌린 주소 공간이다</h3>` — VPC = CIDR 블록 하나를 받아 쓰는 격리된 네트워크. 계정·리전에 종속. `network_basics.html`의 사설 IP 이야기와 잇는다.
3. `<h3>🧱 서브넷은 AZ에 갇힌다</h3>` — 서브넷 하나는 정확히 하나의 AZ 안에 있다. 그래서 다중 AZ 구성은 **서브넷을 AZ 수만큼 만드는 것**에서 시작한다. 라우팅 테이블과 NACL이 붙는 자리가 바로 이 서브넷이다.
4. `<h3>🔌 진짜 주체는 인스턴스가 아니라 ENI다</h3>` — EC2에 SG를 붙인다고 말하지만 실제로 붙는 건 ENI다. 인스턴스에 ENI가 둘이면 SG도 각각 다르게 붙는다. RDS·Lambda(VPC 연결)·Interface Endpoint 전부 ENI를 만들고, 그래서 전부 SG를 받는다. → 11장 예고.
5. 데모 2개 (Step 2, 3)
6. `.myth` — **이 장의 핵심**:
   - ✕ 서브넷에는 "퍼블릭"과 "프라이빗"이라는 **속성**이 있다
   - ✓ 그런 속성은 없다. **연결된 라우팅 테이블에 `0.0.0.0/0 → IGW` 항목이 있으면 관례상 퍼블릭이라 부를 뿐**이다. 콘솔 어디에도 그 체크박스는 없다. 라우팅 테이블 하나만 바꾸면 프라이빗 서브넷이 퍼블릭이 되고, 그 반대도 된다. → 3장으로 이어진다.
7. `.oneline` 요약: VPC는 주소 공간, 서브넷은 **AZ에 갇힌 조각**, 통제가 실제로 붙는 자리는 **서브넷과 ENI** 둘이다.

- [ ] **Step 2: 데모 — VPC 지도**

```html
      <div class="demo" id="vpcMap">
        <span class="demo-tag">VPC 지도</span>
        <p style="margin:0 0 4px">VPC를 이루는 조각들입니다. 눌러서 각각이 <b>무엇에 소속되고 무엇이 붙는지</b> 확인하세요.</p>
        <div class="picker" id="vpcPicker">
          <button class="pick on" data-k="vpc">📦 VPC</button>
          <button class="pick" data-k="subnet">🧱 서브넷</button>
          <button class="pick" data-k="rt">🧭 라우팅 테이블</button>
          <button class="pick" data-k="eni">🔌 ENI</button>
          <button class="pick" data-k="nacl">🧊 NACL</button>
          <button class="pick" data-k="sg">🛡️ SG</button>
        </div>
        <div id="vpcOut"></div>
      </div>
```

```js
/* ============================================================
   데모 3 — VPC 지도 (2장)
   ============================================================ */
(function(){
  const out = $('#vpcOut'); if(!out) return;
  const D = {
    vpc:    { t:"📦 VPC", c:"var(--text-dim)", scope:"리전 하나 · 계정 하나",
      ex:"10.0.0.0/16 (65,536개 주소)",
      d:"빌린 주소 공간 그 자체. 만들 때 정한 CIDR은 <b>줄일 수 없고</b>, 나중에 보조 CIDR을 덧붙이는 것만 됩니다. 다른 VPC와는 기본적으로 완전히 격리돼요 — 잇는 방법은 <a class='link' href='#peering'>12장</a>에서 다룹니다." },
    subnet: { t:"🧱 서브넷", c:"var(--g-nacl)", scope:"AZ 하나에 갇힘",
      ex:"10.0.1.0/24 (ap-northeast-2a)",
      d:"VPC의 CIDR을 쪼갠 조각이고 <b>정확히 한 AZ 안에</b> 있습니다. AZ를 넘는 서브넷은 만들 수 없어요. 그래서 다중 AZ는 서브넷을 AZ 수만큼 만드는 데서 시작합니다. <b>라우팅 테이블과 NACL이 붙는 자리</b>가 여기예요." },
    rt:     { t:"🧭 라우팅 테이블", c:"var(--g-route)", scope:"서브넷에 연결",
      ex:"10.0.0.0/16 → local · 0.0.0.0/0 → igw-abc",
      d:"패킷을 어디로 보낼지 정하는 표. 서브넷마다 정확히 하나가 연결됩니다(지정 안 하면 VPC 기본 것). <b>\"퍼블릭 서브넷\"의 정체가 바로 이 표의 한 줄</b>이에요. 통제 이전에 <b>경로</b>라는 걸 <a class='link' href='#route'>3장</a>에서 다룹니다." },
    eni:    { t:"🔌 ENI", c:"var(--g-sg)", scope:"서브넷 하나에 소속",
      ex:"eni-0a1b · 사설 IP 10.0.1.42",
      d:"가상 랜카드. EC2·RDS·Lambda(VPC 연결)·Interface Endpoint·ALB 노드가 전부 이걸 만듭니다. <b>Security Group이 실제로 붙는 자리</b>가 인스턴스가 아니라 여기예요. 인스턴스에 ENI가 둘이면 SG도 따로 붙습니다." },
    nacl:   { t:"🧊 NACL", c:"var(--g-nacl)", scope:"서브넷에 연결",
      ex:"100 ALLOW tcp 443 · * DENY",
      d:"서브넷 경계의 무상태 검문소. 번호 순서대로 평가하고 <b>deny를 쓸 수 있습니다</b>. 서브넷 하나에 하나만 연결되고, 지정 안 하면 기본 NACL(전부 허용)이 붙어요. 함정은 <a class='link' href='#nacl'>5장</a>에서." },
    sg:     { t:"🛡️ Security Group", c:"var(--g-sg)", scope:"ENI에 붙음 (여러 개 가능)",
      ex:"inbound tcp 443 from 0.0.0.0/0",
      d:"상태 유지 검문소. <b>allow만 있고 deny가 없습니다.</b> ENI 하나에 여러 개를 붙일 수 있고 그때는 합집합이에요. VPC 안에서 움직이므로 리전을 넘지 못합니다. <a class='link' href='#sg'>4장</a>에서 해부합니다." }
  };
  function render(k){
    const d = D[k];
    out.innerHTML =
      `<div class="verdict" style="margin-top:12px">
         <span class="vmodel" style="color:${d.c}">${esc(d.t)}</span>
         <span class="vwhy">${esc(d.scope)} · <span class="mono">${esc(d.ex)}</span></span>
       </div>
       <div class="callout why" style="margin-bottom:0"><p style="margin:0">${d.d}</p></div>`;
  }
  wirePicker('#vpcPicker', render);
  render('vpc');
})();
```

- [ ] **Step 3: 데모 — CIDR 분할기**

```html
      <div class="demo" id="cidrCalc">
        <span class="demo-tag">CIDR 분할기</span>
        <p style="margin:0 0 4px">서브넷 크기를 골라 보세요. <b>AWS가 가져가는 5개</b>가 작은 서브넷에서 얼마나 아픈지 드러납니다.</p>
        <div class="picker" id="cidrPicker">
          <button class="pick" data-k="16">/16</button>
          <button class="pick" data-k="20">/20</button>
          <button class="pick on" data-k="24">/24</button>
          <button class="pick" data-k="26">/26</button>
          <button class="pick" data-k="28">/28</button>
        </div>
        <div id="cidrOut"></div>
      </div>
```

```js
/* ============================================================
   데모 4 — CIDR 분할기 (2장)
   ============================================================ */
(function(){
  const out = $('#cidrOut'); if(!out) return;
  // AWS는 서브넷마다 5개 주소를 예약한다: 네트워크 주소, VPC 라우터,
  // DNS(+2), 미래 예약(+3), 브로드캐스트 주소.
  const RESERVED = 5;
  function render(k){
    const p = +k;
    const total = Math.pow(2, 32 - p);
    const usable = Math.max(0, total - RESERVED);
    const perVpc = Math.pow(2, p - 16); // 10.0.0.0/16 을 이 크기로 쪼갤 때의 개수
    out.innerHTML =
      `<div class="kv" style="margin-top:12px">
         <dt>예시</dt><dd><span class="mono">10.0.0.0/${p}</span></dd>
         <dt>전체 주소</dt><dd>${total.toLocaleString()}개</dd>
         <dt>실제 쓸 수 있는 주소</dt><dd><b>${usable.toLocaleString()}개</b> <span class="dim">(AWS가 서브넷마다 5개를 예약합니다)</span></dd>
         <dt>10.0.0.0/16 하나를 이 크기로 쪼개면</dt><dd>${perVpc.toLocaleString()}개의 서브넷</dd>
       </div>
       <div class="callout why" style="margin-bottom:0"><p style="margin:0">
         AWS가 가져가는 5개는 <b>네트워크 주소 · VPC 라우터(.1) · DNS(.2) · 미래 예약(.3) · 브로드캐스트 주소</b>입니다.
         그래서 <code>/28</code>은 16개 중 <b>11개만</b> 쓸 수 있어요 — 실무에서 서브넷을 <code>/28</code>보다 작게 만들지 않는 이유입니다.
         Interface Endpoint나 ALB 노드도 여기서 IP를 하나씩 가져간다는 걸 잊으면 <b>확장할 때 주소가 모자랍니다.</b>
       </p></div>`;
  }
  wirePicker('#cidrPicker', render);
  render('24');
})();
```

- [ ] **Step 4: 용어 추가**

```js
  "AZ": "Availability Zone. 리전 안에서 물리적으로 분리된 데이터센터 묶음. 서브넷 하나는 정확히 하나의 AZ 안에만 존재합니다.",
  "라우팅 테이블": "패킷의 목적지 대역별로 다음에 어디로 보낼지 적어 둔 표. 서브넷마다 하나가 연결되며, 여기에 IGW 항목이 있느냐가 '퍼블릭 서브넷'의 실체입니다.",
```

- [ ] **Step 5: 퀴즈**

`data-qid="q-vpc"`, `data-answer="b"`

> 질문: 프라이빗 서브넷에 있던 EC2를 인터넷에서 접근 가능하게 만들려고 한다. 반드시 필요한 것은?
>
> - A. 서브넷의 "퍼블릭" 속성을 켠다
> - B. **라우팅 테이블에 `0.0.0.0/0 → IGW`를 넣고, 인스턴스에 퍼블릭 IP를 준다**
> - C. SG 인바운드를 `0.0.0.0/0`으로 연다
> - D. NACL을 기본값으로 되돌린다
>
> 해설: **정답 B.** "퍼블릭 서브넷"이라는 속성은 존재하지 않습니다(A 오답). 라우팅 테이블의 한 줄이 그 정체예요. 그리고 경로가 있어도 **인스턴스에 퍼블릭 IP가 없으면** IGW가 변환해 줄 대상이 없어 여전히 안 됩니다. C와 D는 통제를 여는 것이지 **경로를 만드는 것이 아닙니다** — 경로가 없으면 통제를 아무리 열어도 소용없다는 게 <a class="link" href="#route">3장</a>의 주제입니다.

- [ ] **Step 6: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

CIDR 분할기에서 `/28`을 눌렀을 때 "11개"가 나오는지 반드시 확인한다 (16 − 5 = 11).

---

## Task 7: 3장 — 경로가 곧 통제다

**Files:**
- Modify: `aws_network_security.html` (`#vpc` 뒤에 `<section id="route">` 추가)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 라우팅 테이블의 개념 모델(`local` 항목은 지울 수 없고 항상 이긴다 / longest prefix match). **Task 13(9장)의 삽입 라우팅 데모가 이 모델을 그대로 확장한다** — 9장 데모의 라우팅 표 렌더링은 이 장의 `renderTable()` 스타일을 따른다.

**섹션 헤더:** kicker `03 · 경로`, 제목 `🧭 통제 이전에 <span style="color:var(--accent)">경로</span>가 있다`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.lead`: "SG도 열었고 NACL도 기본값입니다. 그런데도 안 됩니다. 이 경우 십중팔구 막힌 게 아니라 — **갈 길이 없는** 겁니다."
2. `<h3>📏 가장 긴 프리픽스가 이긴다</h3>` — 라우팅 테이블은 목적지 대역별 표이고, 여러 줄이 매치하면 **가장 구체적인(프리픽스가 긴) 줄**이 이긴다. `local` 항목(VPC CIDR)은 자동으로 들어가고 **지울 수도, 덮어쓸 수도 없다**.
3. 데모 (Step 2)
4. `<h3>🚪 IGW는 NAT이 아니다</h3>` — 흔한 오해. IGW는 **퍼블릭 IP를 가진 인스턴스에 대해 1:1로** 주소를 바꿔 준다. 퍼블릭 IP가 없으면 IGW는 해줄 일이 없어 그냥 버린다. 그래서 "라우팅은 넣었는데 안 된다"의 절반이 **퍼블릭 IP 없음**이다.
5. `<h3>🌗 NAT 게이트웨이가 단방향인 이유</h3>` — NAT은 **나간 연결을 기억**했다가 그 응답만 돌려보낸다. 밖에서 먼저 들어오는 연결은 매핑이 없어 갈 곳을 모른다. `network_basics.html`의 NAT 장으로 링크. 여기서 "상태를 기억한다"는 개념이 처음 나오고, **4장 SG의 상태 유지가 같은 아이디어**임을 예고한다.
6. `.myth`:
   - ✕ 프라이빗 서브넷의 인스턴스는 인터넷에 **나갈 수 없다**
   - ✓ 나갈 수 있다. `0.0.0.0/0 → NAT GW` 경로만 있으면 된다. 못 하는 건 **밖에서 먼저 들어오는 것**이다. 이 비대칭이 프라이빗 서브넷의 정의다.
7. `.callout.warn` — 9장 예고: "라우팅 테이블은 통제 도구이기도 합니다. **경로를 바꿔서 트래픽을 검사 장비로 우회**시키는 게 <a class='link' href='#nfw'>9장 Network Firewall</a>의 작동 원리예요. 지금 이 표를 이해해 두면 그 장이 쉬워집니다."
8. `.oneline` 요약: 통제를 열기 전에 **경로가 있는지** 먼저 본다. 경로 없음의 증상은 차단과 똑같은 timeout이라 헷갈리지만, 고치는 곳이 전혀 다르다.

- [ ] **Step 2: 데모 — 라우팅 시뮬레이터**

HTML:

```html
      <div class="demo" id="routeSim">
        <span class="demo-tag">라우팅 시뮬레이터</span>
        <p style="margin:0 0 4px">앱 서버가 있는 <b>프라이빗 서브넷</b>의 라우팅 테이블입니다. 목적지를 골라 어느 줄이 이기는지 보세요.</p>
        <div class="picker" id="routePicker">
          <button class="pick on" data-k="same">🏠 10.0.1.42 (같은 VPC)</button>
          <button class="pick" data-k="peer">🕸️ 10.1.5.7 (피어 VPC)</button>
          <button class="pick" data-k="s3">🪣 52.219.x.x (S3)</button>
          <button class="pick" data-k="net">🌐 8.8.8.8 (인터넷)</button>
          <button class="pick" data-k="trap">🪤 10.0.9.9 (VPC 안, 없는 서브넷)</button>
        </div>
        <div id="routeOut"></div>
      </div>
```

JS:

```js
/* ============================================================
   데모 5 — 라우팅 시뮬레이터 (3장)
   ============================================================ */
(function(){
  const out = $('#routeOut'); if(!out) return;
  // 프리픽스가 긴 순서로 평가한다 = longest prefix match
  const TABLE = [
    { dest:"10.0.0.0/16",  target:"local",           len:16, fixed:true,
      note:"VPC를 만들 때 자동으로 들어가고 <b>지울 수 없습니다</b>. VPC 안 통신은 무조건 여기로 갑니다." },
    { dest:"10.1.0.0/16",  target:"pcx-1a2b (peering)", len:16, fixed:false,
      note:"피어 VPC로 가는 경로. 양쪽 라우팅 테이블에 <b>모두</b> 넣어야 왕복이 됩니다." },
    { dest:"pl-s3 (prefix list)", target:"vpce-s3 (gateway endpoint)", len:99, fixed:false,
      note:"Gateway Endpoint는 <b>라우팅 테이블의 한 줄</b>로 나타납니다. S3 대역이 담긴 prefix list를 목적지로 씁니다." },
    { dest:"0.0.0.0/0",    target:"nat-0c3d",        len:0,  fixed:false,
      note:"위 어디에도 안 걸리면 여기로. 프라이빗 서브넷이니 IGW가 아니라 <b>NAT GW</b>입니다." }
  ];
  const CASE = {
    same: { ip:"10.0.1.42", hit:0,
      v:"<b style='color:var(--ok)'>같은 VPC 안</b>이라 local로 갑니다. 서브넷이 달라도, AZ가 달라도 마찬가지예요.",
      x:"이 경로는 <b>지울 수 없으므로</b>, VPC 안 통신을 라우팅으로 막는 건 불가능합니다. 그래서 VPC 내부 격리는 <b>SG와 NACL의 일</b>이 됩니다 — 라우팅으로는 못 해요." },
    peer: { ip:"10.1.5.7", hit:1,
      v:"peering 연결로 나갑니다.",
      x:"<code>10.0.0.0/16</code>과 <code>10.1.0.0/16</code>은 겹치지 않으니 깔끔합니다. 만약 두 VPC가 <b>같은 CIDR을 썼다면</b> 이 줄을 아예 만들 수 없어요 — <a class='link' href='#peering'>12장</a>의 주제입니다." },
    s3:   { ip:"52.219.x.x", hit:2,
      v:"Gateway Endpoint로 빠집니다. <b>인터넷으로 나가지 않아요.</b>",
      x:"prefix list가 <code>0.0.0.0/0</code>보다 구체적이라 이깁니다. 이 한 줄 덕분에 S3 트래픽이 NAT GW를 타지 않고, <b>NAT 데이터 처리 요금도 발생하지 않습니다</b>. 자세한 건 <a class='link' href='#endpoint'>11장</a>." },
    net:  { ip:"8.8.8.8", hit:3,
      v:"기본 경로를 타고 NAT GW로 갑니다.",
      x:"NAT GW가 자기 퍼블릭 IP로 바꿔서 내보내고, 응답이 오면 기억해 둔 매핑으로 되돌려 줍니다. <b>밖에서 먼저 들어오는 연결은 매핑이 없어 갈 곳을 모릅니다</b> — 이게 프라이빗 서브넷의 정의예요." },
    trap: { ip:"10.0.9.9", hit:0,
      v:"<b style='color:var(--warn)'>local로 갑니다</b> — 그 서브넷이 존재하지 않아도.",
      x:"함정입니다. VPC CIDR 안이기만 하면 라우팅은 <b>성공</b>하고, 패킷은 VPC 라우터까지 갔다가 <b>받는 쪽이 없어 조용히 사라집니다</b>. 인터넷으로 나가지 않아요. \"오타 난 IP로 보냈는데 왜 timeout이지\"의 정체가 대개 이겁니다." }
  };
  function render(k){
    const c = CASE[k];
    const rows = TABLE.map((r,i) => {
      const on = i === c.hit;
      return `<div class="flow-step" style="opacity:${on?1:.42}; border-left:3px solid ${on?'var(--g-route)':'var(--border)'}; padding-left:12px; margin:6px 0">
                <div><span class="mono" style="color:${on?'var(--g-route)':'var(--text-mut)'}">${esc(r.dest)}</span>
                     <span class="dim"> → </span><span class="mono">${esc(r.target)}</span>
                     ${on?' <b style="color:var(--ok)">← 매치</b>':''}${r.fixed?' <span class="dim">(고정)</span>':''}</div>
                ${on?`<div class="dim" style="font-size:13px; margin-top:3px">${r.note}</div>`:''}
              </div>`;
    }).join('');
    out.innerHTML =
      `<div style="margin-top:12px"><span class="dim" style="font-size:13px">목적지 </span><span class="mono" style="color:var(--accent)">${esc(c.ip)}</span></div>
       <div style="margin:8px 0">${rows}</div>
       <div class="verdict"><span class="vres allow">${c.v}</span></div>
       <div class="callout why" style="margin-bottom:0"><p style="margin:0">${c.x}</p></div>`;
  }
  wirePicker('#routePicker', render);
  render('same');
})();
```

- [ ] **Step 3: 용어 추가**

```js
  "IGW": "Internet Gateway. VPC와 인터넷을 잇는 문. 퍼블릭 IP를 가진 리소스에 대해 1:1로 주소를 변환합니다. 퍼블릭 IP가 없으면 해 줄 일이 없어 패킷을 버립니다.",
  "NAT GW": "NAT Gateway. 프라이빗 서브넷의 리소스가 밖으로 나갈 때만 쓰는 단방향 문. 나간 연결을 기억했다가 그 응답만 돌려보냅니다.",
  "prefix list": "여러 CIDR을 묶어 이름 하나로 참조하는 목록. AWS가 관리하는 것(S3·CloudFront 대역 등)과 직접 만드는 것이 있고, 라우팅 테이블과 SG 규칙에서 쓸 수 있습니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-route"`, `data-answer="a"`

> 질문: 프라이빗 서브넷의 앱 서버에서 `curl https://10.0.9.9`을 실행했다. `10.0.9.9`는 VPC CIDR(`10.0.0.0/16`) 안이지만 그런 서브넷은 만든 적이 없다. 무슨 일이 벌어지나?
>
> - A. **`local` 경로에 매치되어 VPC 안에서 사라진다. NAT을 타고 인터넷으로 나가지 않는다**
> - B. 매치되는 서브넷이 없으므로 `0.0.0.0/0`을 타고 NAT GW로 나간다
> - C. 라우팅 테이블에 없는 주소라 즉시 `no route to host` 오류가 난다
> - D. NACL이 거부하고 Flow Log에 `REJECT`가 남는다
>
> 해설: **정답 A.** `local` 경로는 VPC CIDR **전체**를 덮고 지울 수 없습니다. `10.0.9.9`는 그 안이므로 라우팅은 성공하고, 패킷은 VPC 라우터까지 갔다가 받는 쪽이 없어 조용히 사라져요. `0.0.0.0/0`보다 `10.0.0.0/16`이 더 구체적이라 B는 아닙니다. 라우팅은 실패하지 않았으므로 C도 아니고, 통제까지 가지도 못했으니 D도 아닙니다.

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

`🪤` 케이스를 눌렀을 때 매치되는 줄이 **첫 번째(local)** 인지 확인한다. 여기가 이 데모의 핵심이다.

---

## Task 8: 4장 — Security Group

**Files:**
- Modify: `aws_network_security.html` (`#route` 뒤에 `<section id="sg">` 추가)

**Interfaces:**
- Consumes: `wirePicker`, `wireTogs`, `esc`
- Produces: SG 평가 모델 — 규칙 집합을 OR로 평가하고 상태 유지로 응답을 자동 허용하는 순수 함수 `sgAllows(rules, probe)`. **Task 9(5장)와 Task 10(6장)이 같은 모델을 재구현하지 않고 이 장의 평가 규칙 서술을 따른다.** 함수 자체는 IIFE 안에 갇히므로 전역으로 노출하지 않는다 — 각 데모는 자기 IIFE 안에 필요한 만큼만 다시 쓴다.

**섹션 헤더:** kicker `04 · ENI`, 제목 `🛡️ Security Group — <span style="color:var(--accent)">상태를 기억하는</span> 검문소`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.lead`: "SG는 규칙이 몇 줄 안 되는데도 오해가 많습니다. 대부분은 **`iptables`처럼 생각해서** 생깁니다."
2. `<h3>🔌 인스턴스가 아니라 ENI에 붙는다</h3>` — 2장 회수. ENI가 둘이면 SG도 각각.
3. `<h3>✅ allow만 있다</h3>` — **deny 규칙이라는 게 존재하지 않는다.** 기본이 전부 차단이고, 규칙은 구멍을 뚫는 것뿐. 그래서 "특정 IP만 막기"를 SG로는 할 수 없다 → NACL이 필요한 거의 유일한 이유(5장 예고).
4. `<h3>🔀 규칙 사이에 순서가 없다</h3>` — `iptables`는 위에서부터 첫 매치가 이기지만, SG는 **전부 OR**다. 규칙을 어느 자리에 넣든 결과가 같다. SG를 여러 개 붙이면 모든 규칙의 합집합.
5. `<h3>🧠 상태를 기억한다</h3>` — 인바운드로 허용된 연결의 응답은 **아웃바운드 규칙을 보지 않고** 나간다. 3장 NAT에서 본 "기억한다"와 같은 아이디어. 그래서 아웃바운드를 전부 잠가도 웹서버는 정상 응답한다.
6. 데모 (Step 2)
7. `.callout.warn` — 기본 SG(default)의 함정: 자기 자신을 source로 참조하는 규칙이 들어 있어 **같은 기본 SG를 쓰는 리소스끼리는 전부 통한다.** 편해서 그냥 쓰다가 격리가 사라진다. → 14장 회수.
8. `.oneline` 요약: SG는 **ENI에 붙는 allow-only·순서없음·상태유지** 검문소다. 이 네 단어가 SG의 전부다.

- [ ] **Step 2: 데모 — SG 규칙 편집기**

규칙을 토글로 켜고 끄면서 다섯 가지 패킷을 던져 본다.

```html
      <div class="demo" id="sgEditor">
        <span class="demo-tag">SG 규칙 편집기</span>
        <p style="margin:0 0 4px">앱 서버 ENI에 붙은 <span class="mono">app-sg</span>입니다. 규칙을 켜고 끈 다음, 아래에서 패킷을 던져 보세요.</p>
        <div class="picker" id="sgRules">
          <button class="tog on" data-k="in443">IN tcp 443 ← 0.0.0.0/0</button>
          <button class="tog" data-k="in8080">IN tcp 8080 ← sg-alb</button>
          <button class="tog" data-k="in22">IN tcp 22 ← 0.0.0.0/0</button>
          <button class="tog on" data-k="outall">OUT 전체 허용</button>
        </div>
        <div class="picker" id="sgProbe" style="margin-top:10px">
          <button class="pick on" data-k="p443">🌐 인터넷 → 443</button>
          <button class="pick" data-k="p8080">⚖️ ALB → 8080</button>
          <button class="pick" data-k="p22">🔑 인터넷 → 22</button>
          <button class="pick" data-k="presp">↩️ 443 요청의 응답 나가기</button>
          <button class="pick" data-k="pout">📤 앱 → 외부 API 443</button>
        </div>
        <div id="sgOut"></div>
      </div>
```

```js
/* ============================================================
   데모 6 — SG 규칙 편집기 (4장)
   ============================================================ */
(function(){
  const out = $('#sgOut'); if(!out) return;
  let rules = null, probe = 'p443';

  const PROBE = {
    p443:  { dir:'in',  label:'인터넷(203.0.113.9) → app:443', need:'in443',
             deny:"인바운드에 443을 여는 규칙이 없습니다. SG는 <b>기본이 전부 차단</b>이라, 명시적으로 열지 않으면 막힙니다.",
             allow:"인바운드 443 규칙에 매치. 이 연결은 <b>상태로 기억</b>되므로 응답은 아웃바운드 규칙과 무관하게 나갑니다." },
    p8080: { dir:'in',  label:'ALB(sg-alb) → app:8080', need:'in8080',
             deny:"8080 규칙이 꺼져 있습니다. ALB가 정상이어도 <b>대상 쪽 SG</b>가 닫혀 있으면 헬스체크부터 실패해요.",
             allow:"source가 IP가 아니라 <b>sg-alb</b>라는 점을 보세요. ALB 노드의 IP가 바뀌어도 이 규칙은 그대로 유효합니다 — <a class='link' href='#ref'>8장</a>의 주제입니다." },
    p22:   { dir:'in',  label:'인터넷(203.0.113.9) → app:22', need:'in22',
             deny:"22가 닫혀 있습니다. <b>이게 정상입니다.</b>",
             allow:"<b style='color:var(--bad)'>열렸습니다. 그리고 이건 사고입니다.</b> 전 세계에서 SSH 무차별 대입이 들어옵니다. 필요하다면 SSM Session Manager를 쓰세요 — <a class='link' href='#pitfall'>14장</a>." },
    presp: { dir:'resp', label:'app:443 → 인터넷(203.0.113.9) [응답]', need:null,
             deny:"", allow:"" },
    pout:  { dir:'out', label:'app → api.example.com:443 [새 연결]', need:'outall',
             deny:"아웃바운드가 잠겨 있어 <b>앱이 먼저 거는 연결</b>이 막힙니다. 외부 API 호출·패키지 설치·SDK 호출이 전부 실패해요. 응답 트래픽과는 완전히 다른 이야기입니다.",
             allow:"아웃바운드 전체 허용은 <b>기본값이자 대부분의 계정이 그대로 두는 설정</b>입니다. 편하지만, 침해당했을 때 데이터가 나가는 문이기도 해요 — <a class='link' href='#pitfall'>14장</a>." }
  };

  function render(){
    if(!rules) return;
    const p = PROBE[probe];
    let ok, why;
    if(p.dir === 'resp'){
      ok = !!rules.in443;
      why = ok
        ? "<b>아웃바운드 규칙을 보지 않았습니다.</b> 인바운드로 허용된 연결의 응답이라 SG가 상태로 기억해 두었다가 그냥 통과시킵니다. <code>OUT 전체 허용</code>을 꺼도 결과가 같은지 직접 눌러 확인해 보세요."
        : "애초에 인바운드 443이 닫혀 있어 <b>기억할 연결 자체가 없습니다</b>. 응답할 요청이 없으니 이 패킷은 존재하지 않아요.";
    } else {
      ok = !!rules[p.need];
      why = ok ? p.allow : p.deny;
    }
    const on = Object.entries(rules).filter(([,v])=>v).map(([k])=>k);
    out.innerHTML =
      `<div class="verdict" style="margin-top:12px">
         <span class="vmodel">${esc(p.label)}</span>
         <span class="vres ${ok?'allow':'deny'}">${ok?'✅ 통과':'⛔ 차단'}</span>
       </div>
       <div class="callout ${ok?'why':'warn'}" style="margin-bottom:0"><p style="margin:0">${why}</p></div>
       <div class="dim" style="font-size:12.5px; margin-top:8px">켜진 규칙 ${on.length}개 · SG는 이 규칙들을 <b>순서 없이 OR</b>로 평가합니다.</div>`;
  }

  rules = wireTogs('#sgRules', s => { rules = s; render(); });
  wirePicker('#sgProbe', k => { probe = k; render(); });
  render();
})();
```

- [ ] **Step 3: 용어 추가**

```js
  "Security Group": "ENI에 붙는 상태 유지 방화벽. allow 규칙만 가질 수 있고 규칙 사이에 순서가 없으며, 허용된 연결의 응답은 반대 방향 규칙 없이 통과합니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-sg"`, `data-answer="b"`

> 질문: 웹서버 SG의 **아웃바운드 규칙을 전부 삭제**했다. 인바운드에는 443이 열려 있다. 무슨 일이 벌어지나?
>
> - A. 웹서버가 응답을 보내지 못해 모든 요청이 timeout된다
> - B. **웹 응답은 정상이지만, 서버가 먼저 거는 연결(외부 API 호출·패키지 설치)은 전부 막힌다**
> - C. 아무 변화도 없다. 아웃바운드 규칙은 무시된다
> - D. SG는 아웃바운드 규칙을 삭제할 수 없다
>
> 해설: **정답 B.** SG는 상태 유지라, 인바운드로 허용된 연결의 **응답**은 아웃바운드 규칙을 보지 않고 나갑니다(A 오답). 하지만 서버가 **먼저 거는 새 연결**은 명백한 아웃바운드라 규칙이 필요해요. 이 구분이 "아웃바운드를 잠가도 서비스는 멀쩡한데 배포만 깨지는" 현상의 정체입니다.

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

반드시 확인할 것: `↩️ 443 요청의 응답 나가기`를 고른 상태에서 `OUT 전체 허용`을 꺼도 **여전히 ✅ 통과**여야 한다. 이게 이 장 전체의 논지다.

---

## Task 9: 5장 — NACL과 ephemeral 포트의 함정

**Files:**
- Modify: `aws_network_security.html` (`#sg` 뒤에 `<section id="nacl">` 추가)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 4단 파이프라인 렌더 패턴(`요청 NACL → 요청 SG → 응답 SG → 응답 NACL`). Task 10의 관문 체인 시뮬레이터가 이 패턴을 확장한다.

**섹션 헤더:** kicker `05 · 서브넷`, 제목 `🧊 NACL — <span style="color:var(--accent)">기억하지 않는</span> 검문소`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.lead`: "NACL은 기본값이 전부 허용이라 평소엔 없는 셈 칩니다. 그런데 누군가 '보안 강화'를 하겠다고 커스텀 NACL을 만드는 순간, 아무도 이유를 모르는 장애가 시작됩니다."
2. `<h3>🔢 번호 순서대로, 첫 매치가 이긴다</h3>` — SG와 정반대. 규칙에 번호가 있고 작은 번호부터 평가하며 **처음 매치된 규칙이 최종 판정**이다. 마지막에는 지울 수 없는 `* DENY`가 있다.
3. `<h3>🚫 deny를 쓸 수 있다</h3>` — SG가 못 하는 유일한 일. 특정 IP만 차단하려면 NACL이 필요하다. 다만 규칙 수가 제한적이라 **차단 목록 관리 도구로는 부적합**하고, 그 용도는 WAF나 Network Firewall이 맡는다(9·10장 예고).
4. `<h3>🧠 기억하지 않는다 — 함정의 원천</h3>` — **핵심.** SG는 연결을 기억하지만 NACL은 패킷마다 독립 판정한다. 그래서 **응답 트래픽도 규칙 검사를 받는다.**
   - 클라이언트가 `203.0.113.9:51514 → 서버:443`으로 요청한다
   - 서버 응답은 `서버:443 → 203.0.113.9:51514`이다
   - NACL 아웃바운드 규칙은 **목적지 포트**로 매치하므로, 여기서 필요한 건 `443`이 아니라 **`1024–65535`(ephemeral 범위)** 다
   - `아웃바운드 443만 허용`이라고 써 두면 요청은 들어오고 **응답이 못 나간다**
5. 데모 (Step 2)
6. `.cmp2` — SG vs NACL 나란히 비교:
   - 🛡️ Security Group: ENI에 붙음 / allow만 / 순서 없음(OR) / **상태 유지** / 여러 개 = 합집합
   - 🧊 NACL: 서브넷에 붙음 / allow + **deny** / 번호 순서, 첫 매치 승 / **무상태** / 서브넷당 1개
7. `.callout.std` — 업계 표준: **NACL은 기본값 그대로 두고, 통제는 SG로 한다.** NACL은 "SG로 불가능한 일"이 있을 때만 꺼낸다 — 특정 IP 대역 전면 차단, 서브넷 단위의 광범위한 가드레일. 커스텀 NACL을 만들 거라면 ephemeral 범위를 먼저 열어 둔다.
8. `.oneline` 요약: NACL의 모든 함정은 **무상태**라는 한 단어에서 나온다. 응답도 검사받는다는 걸 잊는 순간, 열어 둔 포트로 요청은 들어오고 답이 못 나간다.

- [ ] **Step 2: 데모 — SG vs NACL 왕복 검사**

```html
      <div class="demo" id="naclCmp">
        <span class="demo-tag">SG vs NACL — 왕복 검사</span>
        <p style="margin:0 0 4px">클라이언트가 <span class="mono">203.0.113.9:51514 → 웹서버:443</span>으로 요청합니다. 네 관문을 왕복으로 통과해야 화면이 뜹니다.</p>
        <div class="picker" id="naclPicker">
          <button class="pick on" data-k="default">🟢 기본 NACL (전부 허용)</button>
          <button class="pick" data-k="naive">🪤 커스텀 NACL · 443만 허용</button>
          <button class="pick" data-k="fixed">✅ 커스텀 NACL · ephemeral 개방</button>
          <button class="pick" data-k="denyip">🚫 특정 IP만 차단</button>
        </div>
        <div id="naclOut"></div>
      </div>
```

```js
/* ============================================================
   데모 7 — SG vs NACL 왕복 검사 (5장)
   ============================================================ */
(function(){
  const out = $('#naclOut'); if(!out) return;
  // 4단계: 요청이 NACL 인바운드 → SG 인바운드 → (서버) → 응답이 SG 아웃바운드 → NACL 아웃바운드
  const CASE = {
    default: {
      rules: "인바운드 <span class='mono'>100 ALLOW all</span> · 아웃바운드 <span class='mono'>100 ALLOW all</span>",
      steps: [true, true, true, true],
      v: "<b style='color:var(--ok)'>화면이 뜹니다.</b>",
      x: "기본 NACL은 양방향 전부 허용이라 <b>사실상 없는 것과 같습니다</b>. 대부분의 계정이 이 상태고, 그래서 NACL의 존재를 모른 채로도 아무 문제가 없어요." },
    naive: {
      rules: "인바운드 <span class='mono'>100 ALLOW tcp 443</span> · 아웃바운드 <span class='mono'>100 ALLOW tcp 443</span>",
      steps: [true, true, true, false],
      v: "<b style='color:var(--bad)'>timeout.</b> 요청은 도착했고 서버는 응답까지 만들었는데, 그 응답이 서브넷 밖으로 못 나갑니다.",
      x: "\"443 서비스니까 443만 열면 되지\"가 정확히 이 함정입니다. <b>응답 패킷의 목적지 포트는 443이 아니라 클라이언트의 ephemeral 포트(51514)</b>예요. NACL 아웃바운드는 목적지 포트로 매치하므로 <code>ALLOW tcp 443</code>에 걸리지 않습니다. <b>서버 로그에는 200 OK가 찍혀 있는데 클라이언트는 timeout</b>인, 가장 헷갈리는 증상이 나옵니다." },
    fixed: {
      rules: "인바운드 <span class='mono'>100 ALLOW tcp 443</span> · 아웃바운드 <span class='mono'>100 ALLOW tcp 1024-65535</span>",
      steps: [true, true, true, true],
      v: "<b style='color:var(--ok)'>화면이 뜹니다.</b>",
      x: "아웃바운드에 <b>ephemeral 범위</b>를 열어야 응답이 나갑니다. 그런데 보세요 — 결국 <code>1024-65535</code>를 통째로 연 셈이라, <b>NACL로 아웃바운드를 정교하게 통제하려는 시도는 대개 이렇게 무의미해집니다.</b> 이게 \"통제는 SG로, NACL은 기본값\"이 표준인 이유예요." },
    denyip: {
      rules: "인바운드 <span class='mono'>90 DENY 203.0.113.9/32</span> · <span class='mono'>100 ALLOW all</span>",
      steps: [false, false, false, false],
      v: "<b style='color:var(--warn)'>이 클라이언트만 차단됩니다.</b> 다른 IP는 그대로 통과해요.",
      x: "번호가 작은 <code>90 DENY</code>가 먼저 평가되어 <b>첫 매치로 확정</b>됩니다. 뒤의 <code>100 ALLOW all</code>은 보지도 않아요. <b>SG로는 이걸 할 수 없습니다</b> — deny 규칙이 없으니까요. NACL을 꺼내는 거의 유일하게 정당한 이유가 이겁니다." }
  };
  const STAGE = [
    { t:"① NACL 인바운드", d:"요청 <span class='mono'>→ :443</span>", c:"var(--g-nacl)" },
    { t:"② SG 인바운드",   d:"요청 <span class='mono'>→ :443</span>", c:"var(--g-sg)" },
    { t:"③ SG 아웃바운드", d:"응답 <span class='mono'>:443 →</span> <b>상태로 자동 통과</b>", c:"var(--g-sg)" },
    { t:"④ NACL 아웃바운드", d:"응답 <span class='mono'>→ :51514</span> <b>다시 검사받는다</b>", c:"var(--g-nacl)" }
  ];
  function render(k){
    const c = CASE[k];
    let dead = -1;
    const rows = STAGE.map((s,i) => {
      const ok = c.steps[i];
      const skipped = dead >= 0;
      if(!ok && dead < 0) dead = i;
      const mark = skipped ? '<span class="dim">—</span>'
                 : ok ? '<b style="color:var(--ok)">통과</b>'
                      : '<b style="color:var(--bad)">차단</b>';
      return `<div class="flow-step" style="opacity:${skipped?.35:1}; border-left:3px solid ${skipped?'var(--border)':s.c}; padding-left:12px; margin:6px 0">
                <div><b style="color:${skipped?'var(--text-mut)':s.c}">${s.t}</b> &nbsp; ${mark}</div>
                <div class="dim" style="font-size:13px">${s.d}</div>
              </div>`;
    }).join('');
    out.innerHTML =
      `<div class="dim" style="font-size:13px; margin-top:12px">NACL 규칙 — ${c.rules}</div>
       <div style="margin:8px 0">${rows}</div>
       <div class="verdict"><span class="vres ${c.steps.every(Boolean)?'allow':'deny'}">${c.v}</span></div>
       <div class="callout ${c.steps.every(Boolean)?'why':'warn'}" style="margin-bottom:0"><p style="margin:0">${c.x}</p></div>`;
  }
  wirePicker('#naclPicker', render);
  render('default');
})();
```

**주의:** `denyip` 케이스는 `steps`가 전부 `false`인데, 이건 "①에서 죽고 나머지는 평가되지 않음"을 표현한 것이다. 렌더 함수의 `dead` 로직이 첫 `false` 이후를 `—`로 흐리게 처리하므로 의도대로 나온다.

- [ ] **Step 3: 용어 추가**

```js
  "NACL": "Network ACL. 서브넷 경계에 붙는 무상태 방화벽. 번호 순서로 평가하고 첫 매치가 이기며, deny 규칙을 쓸 수 있습니다. 무상태라 응답 트래픽도 검사받습니다.",
  "ephemeral 포트": "클라이언트가 연결을 걸 때 OS가 임시로 골라 쓰는 출발지 포트. 보통 1024~65535 범위입니다. 응답 패킷의 목적지 포트가 되므로, 무상태 방화벽에서는 이 범위를 열어야 응답이 돌아갑니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-nacl"`, `data-answer="d"`

> 질문: 웹서버 서브넷에 커스텀 NACL을 만들어 **인바운드 443 허용 / 아웃바운드 443 허용**만 넣었다. SG는 443이 열려 있다. 결과는?
>
> - A. 정상 동작한다. 443 서비스니까 443만 열면 된다
> - B. 요청이 서버에 도달하지 못해 서버 로그에 아무것도 남지 않는다
> - C. SG가 상태를 유지하므로 NACL 설정과 무관하게 정상이다
> - D. **서버 로그에는 200 OK가 남지만 클라이언트는 timeout된다**
>
> 해설: **정답 D.** 요청은 인바운드 443 규칙을 통과해 서버까지 갑니다(B 오답). 서버는 응답을 만들어 내보내고 SG는 상태 유지라 그냥 통과시켜요. 하지만 **NACL 아웃바운드는 무상태라 다시 검사**하는데, 응답 패킷의 목적지 포트는 클라이언트의 ephemeral 포트(예: 51514)라서 `ALLOW tcp 443`에 매치되지 않습니다. SG의 상태 유지는 SG에만 적용되지 NACL을 면제해 주지 않아요(C 오답).

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

`🪤 커스텀 NACL · 443만 허용`에서 ①②③이 초록 통과, ④만 빨강 차단으로 나오는지 확인한다. 이 그림이 5장의 전부다.

---

## Task 10: 6장 — 관문의 순서 (클라이맥스)

문서 전체에서 가장 중요한 데모다. 시나리오 4종 × 고장 6종을 조합해 **어느 관문에서 죽는지**와 **그때 내가 보게 되는 증상**을 짝지어 준다. 앞의 다섯 장이 전부 여기로 모인다.

**Files:**
- Modify: `aws_network_security.html` (`#nacl` 뒤에 `<section id="order">` 추가)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: `SCEN` / `FAULTS` 데이터 구조와 단계 애니메이션 렌더. **Task 17(13장 종합 여정 재생기)이 같은 구조를 3-tier 전체 경로로 확장한다.** 두 데모는 별개 IIFE이고 코드를 공유하지 않지만, 시각 언어(관문 색·통과/차단/생략 3상태·증상 3줄)는 동일해야 한다.

**섹션 헤더:** kicker `06 · 순서`, 제목 `⚖️ 하나의 패킷이 통과하는 <span style="color:var(--accent)">관문의 순서</span>`, 🟢 핵심

- [ ] **Step 1: 본문 작성**

1. `.lead`: "여기까지 관문을 하나씩 봤습니다. 이제 순서를 세울 차례예요. **순서를 모르면 증상을 못 읽습니다.**"
2. `<h3>➡️ 들어올 때</h3>` — 순서를 글로 한 번 못박는다:
   `인터넷 → IGW → 라우팅 테이블 → NACL 인바운드 → SG 인바운드 → ENI → OS(iptables) → 앱의 바인딩 주소`
3. `<h3>⬅️ 나갈 때 (응답)</h3>` —
   `앱 → SG(상태로 자동 통과) → NACL 아웃바운드 → 라우팅 테이블 → IGW/NAT → 인터넷`
   **비대칭에 주목:** 가는 길에는 SG가 검사하고 오는 길에는 검사하지 않는다. 반대로 NACL은 양쪽 다 검사한다. 5장의 함정이 여기서 구조적으로 설명된다.
4. `.callout.key`:
   > 관문마다 **막았을 때의 증상이 다릅니다.** 경로가 없으면 조용히 사라지고, SG가 막으면 Flow Log에 `REJECT`가 남고, OS가 REJECT하면 즉시 `connection refused`가 돌아옵니다. **증상 → 관문**을 역으로 읽을 수 있게 되는 것이 이 장의 목표예요.
5. 데모 (Step 2)
6. `.oneline` 요약: 관문은 여덟 개고 순서가 있다. 그리고 **증상은 관문마다 다르다** — 이 둘을 짝지으면 진단이 검색이 아니라 추론이 된다.

- [ ] **Step 2: 데모 — 관문 체인 시뮬레이터**

```html
      <div class="demo" id="chain">
        <span class="demo-tag">관문 체인 시뮬레이터</span>
        <p style="margin:0 0 4px">시나리오를 고르고, 고장을 하나 주입해 보세요. 어느 관문에서 죽는지와 그때 <b>내가 실제로 보게 되는 것</b>이 함께 나옵니다.</p>
        <div class="picker" id="chainScenario">
          <button class="pick on" data-k="in">🌐 인터넷 → 웹서버:443</button>
          <button class="pick" data-k="db">🗄️ 앱 → RDS:5432</button>
          <button class="pick" data-k="out">📤 앱 → 외부 API:443</button>
          <button class="pick" data-k="s3">🪣 앱 → S3</button>
        </div>
        <div class="picker" id="chainFault" style="margin-top:10px">
          <button class="pick on" data-k="none">✅ 고장 없음</button>
          <button class="pick" data-k="nortigw">🧭 라우팅에 IGW 없음</button>
          <button class="pick" data-k="nopubip">🏷️ 퍼블릭 IP 없음</button>
          <button class="pick" data-k="sgdir">🛡️ SG 방향 착각</button>
          <button class="pick" data-k="naclout">🧊 NACL이 ephemeral 차단</button>
          <button class="pick" data-k="nonat">🚧 NAT 경로 없음</button>
        </div>
        <div id="chainStage"></div>
        <div id="chainOut"></div>
      </div>
```

```js
/* ============================================================
   데모 8 — 관문 체인 시뮬레이터 (6장) · 이 문서의 핵심
   ============================================================ */
(function(){
  const stage = $('#chainStage'), out = $('#chainOut'); if(!stage || !out) return;

  // kill 값: { why, client, log, fix }
  const G = {
    rtIgw:  { t:"라우팅 테이블 (0.0.0.0/0 → IGW)", c:"var(--g-route)", kill:{
      nortigw:{ why:"이 서브넷의 라우팅 테이블에 IGW로 가는 줄이 없습니다.",
        client:"<b>timeout</b> — 60초쯤 기다리다 죽는다",
        log:"<b>아무 데도 남지 않는다.</b> 패킷이 ENI에 닿지도 못했다",
        fix:"라우팅 테이블에 <code>0.0.0.0/0 → igw-xxx</code> 추가. 이게 '퍼블릭 서브넷'의 실체다 (<a class='link' href='#vpc'>2장</a>)" } } },
    igw:    { t:"IGW (퍼블릭 IP 변환)", c:"var(--g-route)", kill:{
      nopubip:{ why:"인스턴스에 퍼블릭 IP가 없어 IGW가 변환해 줄 대상이 없습니다.",
        client:"<b>timeout</b>",
        log:"남지 않는다",
        fix:"퍼블릭 IP를 할당하거나 Elastic IP를 붙인다. 경로가 있어도 <b>주소가 없으면 소용없다</b> (<a class='link' href='#route'>3장</a>)" } } },
    naclIn: { t:"NACL 인바운드", c:"var(--g-nacl)", kill:{} },
    sgIn:   { t:"SG 인바운드", c:"var(--g-sg)", kill:{
      sgdir:{ why:"열어야 할 방향을 반대로 걸었습니다. 아웃바운드에 443을 넣고 인바운드는 비어 있어요.",
        client:"<b>timeout</b>",
        log:"<b>Flow Log에 단독 <code>REJECT</code> 한 줄.</b> ENI까지는 왔다는 뜻이라 라우팅 문제와는 갈리지만, <b>NACL이 막았을 때와는 구별되지 않는다</b>",
        fix:"인바운드 규칙을 추가한다. SG는 <b>방향별로 완전히 별개</b>다 (<a class='link' href='#sg'>4장</a>)" } } },
    os:     { t:"OS · 앱 바인딩", c:"var(--g-os)", kill:{} },
    sgResp: { t:"응답 — SG (상태로 자동 통과)", c:"var(--g-sg)", kill:{} },
    naclOut:{ t:"응답 — NACL 아웃바운드 (목적지 = ephemeral)", c:"var(--g-nacl)", kill:{
      naclout:{ why:"NACL 아웃바운드가 <code>1024-65535</code>를 열지 않았습니다. 응답의 목적지 포트가 거기입니다.",
        client:"<b>timeout</b>",
        log:"<b>서버 로그에는 200 OK.</b> Flow Log에는 <code>ACCEPT</code> 뒤에 <code>REJECT</code>가 <b>짝으로</b> 남는다 — SG는 상태 저장이라 이 조합을 만들 수 없으므로 <b>NACL 확정 신호</b>다",
        fix:"NACL 아웃바운드에 ephemeral 범위를 연다. 또는 커스텀 NACL을 걷어낸다 (<a class='link' href='#nacl'>5장</a>)" } } },
    rtLocal:{ t:"라우팅 테이블 (local — 지울 수 없음)", c:"var(--g-route)", kill:{} },
    naclOutReq:{ t:"NACL 아웃바운드 (요청)", c:"var(--g-nacl)", kill:{} },
    sgOut:  { t:"SG 아웃바운드", c:"var(--g-sg)", kill:{
      sgdir:{ why:"아웃바운드 규칙을 지워 둔 상태에서 <b>앱이 먼저 거는 연결</b>을 시도했습니다.",
        client:"<b>timeout</b> (또는 SDK의 연결 오류)",
        log:"Flow Log에 <code>REJECT</code>",
        fix:"아웃바운드 규칙을 추가한다. 응답 트래픽과 <b>새 연결</b>은 다르다 (<a class='link' href='#sg'>4장</a>)" } } },
    naclInPeer:{ t:"상대 서브넷 NACL 인바운드", c:"var(--g-nacl)", kill:{} },
    sgInPeer:{ t:"상대 SG 인바운드 (source = app-sg)", c:"var(--g-sg)", kill:{} },
    rtNat:  { t:"라우팅 테이블 (0.0.0.0/0 → NAT GW)", c:"var(--g-route)", kill:{
      nonat:{ why:"프라이빗 서브넷에 NAT로 가는 경로가 없습니다.",
        client:"<b>timeout</b>",
        log:"남지 않는다",
        fix:"NAT GW를 만들고 <code>0.0.0.0/0 → nat-xxx</code>를 넣는다. 또는 나갈 필요가 없는 트래픽이라면 <b>VPC Endpoint</b>를 쓴다 (<a class='link' href='#endpoint'>11장</a>)" } } },
    nat:    { t:"NAT GW (매핑 기록)", c:"var(--g-route)", kill:{} },
    naclInResp:{ t:"응답 — NACL 인바운드 (목적지 = ephemeral)", c:"var(--g-nacl)", kill:{
      naclout:{ why:"나가는 건 됐는데 <b>돌아오는 응답</b>이 NACL 인바운드에 막혔습니다. 응답의 목적지 포트는 앱의 ephemeral 포트예요.",
        client:"<b>timeout</b>",
        log:"나가는 방향만 Flow Log에 남아 <b>편도만 성공한 것처럼</b> 보인다",
        fix:"NACL 인바운드에 ephemeral 범위를 연다 (<a class='link' href='#nacl'>5장</a>)" } } },
    rtVpce: { t:"라우팅 테이블 (S3 prefix list → Gateway Endpoint)", c:"var(--g-route)", kill:{
      nonat:{ why:"Gateway Endpoint도 없고 NAT 경로도 없습니다. S3로 갈 길이 아예 없어요.",
        client:"<b>timeout</b> 또는 SDK의 연결 오류",
        log:"남지 않는다",
        fix:"Gateway Endpoint를 만들어 라우팅 테이블에 연결한다. 인터넷을 거치지 않고 <b>요금도 들지 않는다</b> (<a class='link' href='#endpoint'>11장</a>)" } } },
    vpcePol:{ t:"Endpoint 정책", c:"var(--accent-2)", kill:{} },
    iam:    { t:"IAM 판정 (s3:GetObject)", c:"var(--accent-2)", kill:{} }
  };

  const SCEN = {
    in:  { title:"인터넷 → 퍼블릭 서브넷의 웹서버:443",
           gates:["rtIgw","igw","naclIn","sgIn","os","sgResp","naclOut"],
           okMsg:"화면이 뜹니다. 여덟 관문을 왕복으로 다 통과했어요." },
    db:  { title:"앱(프라이빗) → RDS(격리 서브넷):5432",
           gates:["rtLocal","naclOutReq","sgOut","naclInPeer","sgInPeer"],
           okMsg:"쿼리가 나갑니다. <b>인터넷 게이트웨이도 NAT도 등장하지 않았다</b>는 점을 보세요 — VPC 안 통신은 local 경로로 끝납니다." },
    out: { title:"앱(프라이빗) → 외부 API:443",
           gates:["rtNat","naclOutReq","sgOut","nat","naclInResp"],
           okMsg:"외부 호출이 성공합니다. NAT GW가 매핑을 기억해 뒀다가 응답을 되돌려 줬어요." },
    s3:  { title:"앱(프라이빗) → S3 (Gateway Endpoint 경유)",
           gates:["rtVpce","sgOut","vpcePol","iam"],
           okMsg:"객체를 읽습니다. <b>관문이 둘 더 있다는 데 주목하세요</b> — 네트워크를 다 통과해도 Endpoint 정책과 IAM이 남아 있습니다 (<a class='link' href='#endpoint'>11장</a>)." }
  };

  const FAULT_LABEL = {
    none:"고장 없음", nortigw:"라우팅에 IGW 없음", nopubip:"퍼블릭 IP 없음",
    sgdir:"SG 방향 착각", naclout:"NACL이 ephemeral 차단", nonat:"NAT 경로 없음"
  };

  let scen = 'in', fault = 'none';
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function render(){
    const s = SCEN[scen];
    const ids = s.gates;
    let deadAt = -1, killInfo = null;
    for(let i = 0; i < ids.length; i++){
      const k = G[ids[i]].kill[fault];
      if(k){ deadAt = i; killInfo = k; break; }
    }

    stage.innerHTML =
      `<div class="dim" style="font-size:13px; margin-top:12px">${s.title} &nbsp;·&nbsp; 고장: <b>${esc(FAULT_LABEL[fault])}</b></div>` +
      `<div id="chainRows" style="margin:8px 0"></div>`;
    const rows = $('#chainRows');

    ids.forEach((id, i) => {
      const g = G[id];
      const state = deadAt < 0 ? 'ok' : (i < deadAt ? 'ok' : i === deadAt ? 'dead' : 'skip');
      const mark = state === 'ok' ? '<b style="color:var(--ok)">통과</b>'
                 : state === 'dead' ? '<b style="color:var(--bad)">여기서 죽는다</b>'
                 : '<span class="dim">평가되지 않음</span>';
      const el = document.createElement('div');
      el.className = 'flow-step';
      el.style.cssText = `border-left:3px solid ${state==='skip'?'var(--border)':g.c}; padding-left:12px; margin:6px 0; opacity:0; transition:opacity .18s`;
      el.innerHTML = `<div><span style="color:${state==='skip'?'var(--text-mut)':g.c}">${esc(g.t)}</span> &nbsp; ${mark}</div>`;
      rows.appendChild(el);
      if(reduce) el.style.opacity = state === 'skip' ? '.35' : '1';
      else setTimeout(() => { el.style.opacity = state === 'skip' ? '.35' : '1'; }, i * 130);
    });

    if(killInfo){
      out.innerHTML =
        `<div class="verdict"><span class="vres deny">⛔ ${killInfo.why}</span></div>
         <div class="kv" style="margin-top:10px">
           <dt>내가 보는 것</dt><dd>${killInfo.client}</dd>
           <dt>로그에는</dt><dd>${killInfo.log}</dd>
           <dt>고칠 곳</dt><dd>${killInfo.fix}</dd>
         </div>`;
    } else {
      const na = fault !== 'none';
      out.innerHTML =
        `<div class="verdict"><span class="vres allow">✅ ${s.okMsg}</span></div>` +
        (na ? `<div class="callout why" style="margin-bottom:0"><p style="margin:0">
                 <b>이 고장은 이 경로에 해당하지 않습니다.</b> “${esc(FAULT_LABEL[fault])}”는 다른 시나리오에서만 문제가 돼요.
                 같은 고장이 경로에 따라 <b>치명적이거나 무해하다</b>는 게 이 데모의 두 번째 교훈입니다.
               </p></div>` : '');
    }
  }

  wirePicker('#chainScenario', k => { scen = k; render(); });
  wirePicker('#chainFault',    k => { fault = k; render(); });
  render();
})();
```

- [ ] **Step 3: 퀴즈**

`data-qid="q-order"`, `data-answer="c"`

> 질문: 서버의 애플리케이션 로그에는 `200 OK`가 정상적으로 찍히는데, 클라이언트는 계속 timeout된다. 가장 유력한 원인은?
>
> - A. SG 인바운드에 해당 포트가 없다
> - B. 라우팅 테이블에 IGW가 없다
> - C. **NACL 아웃바운드가 ephemeral 포트 범위를 열지 않았다**
> - D. 인스턴스에 퍼블릭 IP가 없다
>
> 해설: **정답 C.** 서버가 `200 OK`를 만들었다는 건 **요청이 앱까지 도달했다**는 뜻입니다. 그러면 들어오는 길의 관문(A·B·D)은 전부 통과한 거예요. 남은 건 **나가는 길**이고, 거기서 SG는 상태 유지라 통과시키므로 유일하게 남는 용의자가 NACL 아웃바운드입니다. **"어디까지 갔는지"를 먼저 확정하면 용의자가 절반으로 줄어듭니다** — 이게 관문의 순서를 아는 이유예요.

- [ ] **Step 4: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

반드시 확인할 조합:
1. `인터넷 → 웹서버` × `라우팅에 IGW 없음` → 첫 관문에서 죽고, 나머지가 흐려진다
2. `인터넷 → 웹서버` × `NACL이 ephemeral 차단` → **마지막 관문**에서 죽는다
3. `앱 → RDS` × `라우팅에 IGW 없음` → **해당 없음** 안내가 나오고 전부 통과한다
4. `앱 → S3` × `고장 없음` → 관문 4개 중 뒤 2개가 Endpoint 정책·IAM이다
5. `앱 → RDS` × `SG 방향 착각` → `sgOut`(앱의 아웃바운드)에서 죽는다
6. 시스템 설정에서 "동작 줄이기"를 켜면 애니메이션 없이 즉시 렌더된다

**설계 메모:** `sgInPeer`의 `kill` 맵은 의도적으로 비어 있다. "RDS SG가 앱의 IP를 박아 두었다가 인스턴스 교체로 깨진다"는 이야기는 `sgdir`(방향 착각)과 **다른 종류의 고장**이라 여기에 섞으면 안 되고, <a href="#task-12">Task 12(8장)</a>의 SG 참조 데모가 그 이야기를 온전히 다룬다. 고장 목록에 억지로 끼워 넣지 말 것.

---

## Task 11: 7장 — 어디서 막혔는지 알아내는 법

**이 태스크는 Task 1의 결과에 직접 의존한다.** 시작하기 전에 `docs/superpowers/notes/2026-08-12-aws-facts.md`의 V1 항목을 읽고, 아래 서술이 검증 결과와 어긋나면 **검증 결과를 따른다.**

**Files:**
- Modify: `aws_network_security.html` (`#order` 뒤에 `<section id="trace">` 추가)
- Read: `docs/superpowers/notes/2026-08-12-aws-facts.md`

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 없음

**섹션 헤더:** kicker `07 · 진단`, 제목 `🔍 <span style="color:var(--accent)">증상</span>에서 관문을 역추적하기`, 🟢 필수

- [ ] **Step 1: V1 검증 결과 반영 확인**

`docs/superpowers/notes/2026-08-12-aws-facts.md`의 V1을 읽는다. 아래 Step 3의 `flowLog` 데모 데이터에서 **`nacl` 케이스의 서술**과 **`outdeny` 케이스의 `action` 값**이 검증 결과와 일치하는지 확인하고, 다르면 데이터와 본문 서술을 고친다. 확신이 없으면 **단정하지 말고** "AWS 문서는 이 경우 …라고 설명한다"처럼 출처를 밝히는 문장으로 쓴다.

- [ ] **Step 2: 본문 작성**

1. `.lead`: "지금까지는 '어디서 막히는가'를 봤습니다. 실무에서는 반대 방향이 필요해요 — **증상만 보고 관문을 좁히는 것.**"
2. `<h3>⏱️ timeout과 refused는 다른 이야기다</h3>` — 진단의 첫 갈래이자 가장 큰 갈래.
   - `connection refused` = **RST가 돌아왔다** = 패킷이 목적지까지 **도달했다**. 방화벽은 전부 통과했고, 그 포트에 듣는 프로세스가 없거나 OS가 명시적으로 거절한 것. **네트워크 문제가 아니다.**
   - `timeout` = **아무 답도 없다** = 어딘가에서 조용히 버려졌다. 관문 전체가 용의선상에 남는다.
   - `network_basics.html`의 RST 이야기로 링크한다.
3. `.callout.key`:
   > `connection refused`를 보고 SG를 뒤지는 건 시간 낭비입니다. 그 메시지는 이미 **"관문을 다 통과했다"는 증거**예요. 앱이 안 떠 있거나, `127.0.0.1`에만 바인딩했거나, 포트를 잘못 안 겁니다.
4. `<h3>📋 Flow Logs — ENI가 남기는 영수증</h3>` + 데모 (Step 3)
5. `<h3>🧩 REJECT 앞에 ACCEPT가 있는가</h3>` — **V1 검증 결과로 재작성된 절.** 반드시 이 논지로 쓴다:

   - **흔한 오해부터 깬다** — "NACL이 막으면 로그가 안 남는다"는 **틀렸다.** `action` 필드의 공식 정의가 `REJECT`의 원인으로 **보안 그룹과 네트워크 ACL을 함께** 열거한다. 둘 다 똑같이 `REJECT`로 남는다.
   - 따라서 **단독 `REJECT` 한 줄만 보고는 SG와 NACL을 가릴 수 없다.** 인바운드가 어느 쪽에 막히든 패킷은 인스턴스에 닿지 못하고, 응답도 없으니 로그는 한 줄뿐이다.
   - **진짜 신호는 짝이다.** `ACCEPT` 다음에 `REJECT`가 따라붙으면 — 요청은 인스턴스까지 갔고 **응답이 막혔다**는 뜻이다. **SG는 상태 저장이라 이 조합을 원리상 만들 수 없다.** 허용된 인바운드의 응답을 아웃바운드 규칙과 무관하게 무조건 통과시키니까. 그러므로 `ACCEPT`+`REJECT` 짝은 **NACL 확정 신호**다.
   - **로그가 아예 없을 때**는 또 다른 이야기다 — 패킷이 ENI 근처에도 오지 못한 것이라 **라우팅·퍼블릭 IP·서브넷**을 본다.

   세 갈래를 `.kv`로 정리한다: `기록 없음 → 경로 문제` / `단독 REJECT → SG 또는 NACL(구별 불가)` / `ACCEPT+REJECT 짝 → NACL이 응답을 막음`.

   근거 문서와 인용은 `docs/superpowers/notes/2026-08-12-aws-facts.md`의 V1에 있다. 그 인용을 넘어서는 단정을 새로 만들지 말 것.
6. `<h3>🧪 Reachability Analyzer — 패킷을 안 보내고 경로를 검사한다</h3>` — 출발 ENI와 목적지를 지정하면 라우팅·SG·NACL을 **정적으로 분석**해 어디서 막히는지 알려준다. 실제 트래픽을 보내지 않으므로 앱이 안 떠 있어도 쓸 수 있고, 반대로 **OS 방화벽이나 앱 바인딩 문제는 못 잡는다.** 이 한계를 명시한다.
7. 판별 트리 데모 (Step 4)
8. `.oneline` 요약: 증상은 관문을 가리킨다. `refused`면 네트워크를 그만 보고, `timeout`이면 **어디까지 갔는지**부터 확정한다.

- [ ] **Step 3: 데모 — Flow Log 한 줄 해부기**

```html
      <div class="demo" id="flowLog">
        <span class="demo-tag">Flow Log 한 줄 해부기</span>
        <p style="margin:0 0 4px">기본 형식(version 2)의 로그 한 줄입니다. 상황을 골라 무엇이 남고 무엇이 안 남는지 보세요.</p>
        <div class="picker" id="flowPicker">
          <button class="pick on" data-k="ok">✅ 정상 요청</button>
          <button class="pick" data-k="sgreject">🛡️ SG가 인바운드 차단</button>
          <button class="pick" data-k="nacl">🧊 NACL이 인바운드 차단</button>
          <button class="pick" data-k="naclresp">🧊 NACL이 <b>응답</b> 차단</button>
          <button class="pick" data-k="outdeny">📤 아웃바운드 차단</button>
          <button class="pick" data-k="none">🚫 기록이 아예 없음</button>
        </div>
        <div id="flowOut"></div>
      </div>
```

```js
/* ============================================================
   데모 9 — Flow Log 한 줄 해부기 (7장)
   ============================================================ */
(function(){
  const out = $('#flowOut'); if(!out) return;
  const FIELDS = ["version","account-id","interface-id","srcaddr","dstaddr","srcport","dstport",
                  "protocol","packets","bytes","start","end","action","log-status"];
  const D = {
    ok: { line:["2","111122223333","eni-0a1b2c3d","203.0.113.9","10.0.1.42","51514","443","6","12","1842","1690000000","1690000060","ACCEPT","OK"],
      n:"평범한 성공입니다. <code>protocol 6</code>은 TCP고, <code>srcport</code>가 <b>51514</b>인 데 주목하세요 — 클라이언트의 ephemeral 포트입니다. <a class='link' href='#nacl'>5장</a>에서 NACL 아웃바운드가 열어야 했던 그 번호예요." },
    sgreject: { line:["2","111122223333","eni-0a1b2c3d","203.0.113.9","10.0.1.42","51514","22","6","1","44","1690000000","1690000060","REJECT","OK"],
      n:"<b><code>REJECT</code>가 남았다는 건 패킷이 ENI까지 도달했다는 뜻입니다.</b> 즉 라우팅은 정상이고, SG(또는 ENI 층의 판정)에서 걸린 거예요. <code>packets 1</code>·<code>bytes 44</code>는 SYN 하나만 왔다는 뜻이라 연결이 성립조차 안 했음을 보여줍니다. 여기서는 22번 포트 스캔이 들어온 흔적이네요." },
    nacl: { line:["2","111122223333","eni-0a1b2c3d","203.0.113.9","10.0.1.42","51514","443","6","1","44","1690000000","1690000060","REJECT","OK"],
      n:"<b>SG가 막았을 때와 글자 하나 다르지 않습니다.</b> <code>action</code> 필드의 공식 정의는 <code>REJECT</code>의 원인으로 <b>보안 그룹과 네트워크 ACL을 함께</b> 열거해요. 로그만 보고는 둘을 가릴 수 없습니다. <br><br>\"NACL이 막으면 로그가 안 남는다\"는 널리 퍼진 오해입니다. <b>로그가 정말 한 줄도 없다면</b> 그건 SG도 NACL도 아니라 <b>패킷이 ENI 근처에도 못 왔다</b>는 뜻 — 라우팅·퍼블릭 IP·서브넷을 보세요." },
    naclresp: { lines:[
        ["2","111122223333","eni-0a1b2c3d","203.0.113.9","10.0.1.42","51514","443","6","10","1420","1690000000","1690000060","ACCEPT","OK"],
        ["2","111122223333","eni-0a1b2c3d","10.0.1.42","203.0.113.9","443","51514","6","8","1180","1690000000","1690000060","REJECT","OK"]
      ],
      n:"<b>여기가 진짜 단서입니다.</b> 같은 5-tuple에 대해 <code>ACCEPT</code> 한 줄과 <code>REJECT</code> 한 줄이 <b>짝으로</b> 남았습니다. 요청은 인스턴스까지 갔고(<code>ACCEPT</code>), <b>응답이 막혔다</b>(<code>REJECT</code>)는 뜻이에요. <br><br><b>SG는 이 조합을 원리상 만들 수 없습니다.</b> 상태 저장이라 허용된 인바운드의 응답을 아웃바운드 규칙과 무관하게 무조건 통과시키니까요. 그러니 이 짝이 보이면 <b>NACL이 응답을 막은 것으로 확정</b>입니다." },
    outdeny: { line:["2","111122223333","eni-0a1b2c3d","10.0.1.42","198.51.100.7","44210","443","6","1","44","1690000000","1690000060","REJECT","OK"],
      n:"방향이 뒤집혀 있죠 — <code>srcaddr</code>가 우리 인스턴스입니다. 앱이 <b>먼저 건 연결</b>이 아웃바운드 규칙에 막힌 경우예요. <a class='link' href='#sg'>4장</a>에서 본 \"응답은 되는데 새 연결은 안 되는\" 상황이 로그로는 이렇게 보입니다." },
    none: { lines:[],
      n:"<b>한 줄도 없습니다.</b> 이건 SG도 NACL도 아니에요 — 둘 다 막으면 최소한 <code>REJECT</code>는 남기니까요. <br><br>기록이 아예 없다는 건 <b>패킷이 ENI 근처에도 오지 못했다</b>는 뜻입니다. 라우팅 테이블에 경로가 없거나, 퍼블릭 IP가 없거나, 엉뚱한 서브넷을 보고 있거나, 애초에 요청이 오지 않은 거예요. <b>여기서부터는 Flow Log가 아니라 Reachability Analyzer의 영역</b>입니다." }
  };
  function render(k){
    const d = D[k];
    const rows = d.lines !== undefined ? d.lines : [d.line];
    if(rows.length === 0){
      out.innerHTML =
        `<div class="verdict" style="margin-top:12px"><span class="vres deny">기록 없음</span></div>
         <div class="callout warn" style="margin-bottom:0"><p style="margin:0">${d.n}</p></div>`;
      return;
    }
    const blocks = rows.map(line => {
      const cells = line.map((v,i) => {
        const hot = ["srcport","dstport","action","srcaddr"].includes(FIELDS[i]);
        const isAction = FIELDS[i] === 'action';
        const col = isAction ? (v === 'ACCEPT' ? 'var(--ok)' : 'var(--bad)')
                             : (hot ? 'var(--accent)' : 'var(--text)');
        return `<div style="display:inline-block; margin:0 10px 8px 0">
                  <div class="dim" style="font-size:11px">${esc(FIELDS[i])}</div>
                  <div class="mono" style="font-size:13.5px; color:${col}"><b>${esc(v)}</b></div>
                </div>`;
      }).join('');
      return `<div style="margin-top:10px; padding:12px; background:var(--bg); border:1px solid var(--border); border-radius:9px">${cells}</div>`;
    }).join('');
    out.innerHTML = blocks +
      `<div class="callout ${rows.length > 1 ? 'key' : 'why'}" style="margin-bottom:0"><p style="margin:0">${d.n}</p></div>`;
  }
  wirePicker('#flowPicker', render);
  render('ok');
})();
```

- [ ] **Step 4: 데모 — 증상 판별 트리**

```html
      <div class="demo" id="triage">
        <span class="demo-tag">증상 → 용의자</span>
        <p style="margin:0 0 4px">지금 보고 있는 증상을 고르세요. 용의자와 다음에 확인할 것이 나옵니다.</p>
        <div class="picker" id="triagePicker">
          <button class="pick on" data-k="timeout">⏱️ timeout</button>
          <button class="pick" data-k="refused">🚪 connection refused</button>
          <button class="pick" data-k="oneway">↔️ 편도만 된다</button>
          <button class="pick" data-k="wasok">📅 어제까지는 됐다</button>
          <button class="pick" data-k="flaky">🎲 될 때도 있고 안 될 때도 있다</button>
        </div>
        <div id="triageOut"></div>
      </div>
```

```js
/* ============================================================
   데모 10 — 증상 판별 트리 (7장)
   ============================================================ */
(function(){
  const out = $('#triageOut'); if(!out) return;
  const D = {
    timeout: { s:["라우팅 테이블에 경로가 없다","퍼블릭 IP가 없다","SG 인바운드가 닫혀 있다","NACL이 막았다","OS 방화벽이 DROP했다","보안그룹은 맞는데 서브넷을 잘못 골랐다"],
      next:"<b>① Flow Log에 줄이 있는지</b> 먼저 본다. <b>한 줄도 없으면</b> 패킷이 ENI 근처에도 못 온 것 — <b>라우팅·퍼블릭 IP·서브넷</b>으로 좁혀진다. <b>단독 <code>REJECT</code>가 있으면</b> ENI까지는 왔다는 뜻이지만, 여기서 <b>SG와 NACL은 구별되지 않는다</b>(둘 다 <code>REJECT</code>로 남는다). <br><b>② Reachability Analyzer</b>를 돌리면 라우팅·SG·NACL을 한 번에 판정해 준다. 그래도 통과라고 나오면 남은 건 <b>OS와 앱</b>이다." },
    refused: { s:["앱이 떠 있지 않다","앱이 127.0.0.1에만 바인딩했다","포트를 잘못 알고 있다","OS 방화벽이 REJECT했다"],
      next:"<b>네트워크 관문은 전부 통과했습니다.</b> RST가 돌아왔다는 건 목적지에 도달했다는 증거예요. SG·NACL·라우팅을 뒤지지 말고 <b>인스턴스 안</b>을 보세요 — <code>ss -tlnp</code>로 그 포트를 듣는 프로세스가 있는지, 바인딩 주소가 <code>0.0.0.0</code>인지 <code>127.0.0.1</code>인지." },
    oneway: { s:["NACL 아웃바운드가 ephemeral을 막았다","NACL 인바운드가 ephemeral을 막았다","비대칭 라우팅"],
      next:"거의 항상 <b>무상태 검문소</b>가 범인입니다. SG는 상태를 유지하므로 편도만 되는 상황을 만들지 못해요. <b>Flow Log에서 같은 5-tuple의 <code>ACCEPT</code> 뒤에 <code>REJECT</code>가 붙어 있으면 NACL 확정</b>입니다 — SG는 그 조합을 원리상 만들 수 없으니까요. 그다음 <b>NACL 양방향에 <code>1024-65535</code>가 열려 있는지</b> 확인하세요." },
    wasok: { s:["SG가 IP를 source로 참조하는데 그 IP가 바뀌었다","오토스케일링으로 인스턴스가 교체됐다","NAT GW의 EIP가 바뀌었다","상대 쪽 IP 허용 목록에서 빠졌다"],
      next:"<b>구성은 안 바뀌었는데 IP가 바뀐 경우</b>가 압도적으로 많습니다. SG 규칙에 <code>10.0.1.42/32</code> 같은 개별 IP가 박혀 있는지 보세요. 있다면 그게 원인이고, 답은 <b>SG 참조</b>입니다 (<a class='link' href='#ref'>8장</a>)." },
    flaky: { s:["다중 AZ 중 한쪽 서브넷만 설정이 다르다","대상 그룹의 일부 인스턴스만 SG가 다르다","NACL 규칙 수 한도","연결 추적 한도"],
      next:"<b>\"어떤 요청은 되고 어떤 요청은 안 된다\"는 대개 대상이 여러 개</b>라는 뜻입니다. AZ별 서브넷의 라우팅 테이블과 NACL이 <b>정말 같은지</b> 하나씩 대조하세요. 다중 AZ 구성에서 한쪽 서브넷만 라우팅 테이블 연결을 빠뜨리는 게 전형적입니다." }
  };
  function render(k){
    const d = D[k];
    out.innerHTML =
      `<div style="margin-top:12px"><div class="dim" style="font-size:12.5px; margin-bottom:6px">용의자</div>` +
      d.s.map(x => `<span class="chip" style="margin:0 6px 6px 0; display:inline-block">${esc(x)}</span>`).join('') +
      `</div><div class="callout why" style="margin-bottom:0"><h4>다음에 확인할 것</h4><p style="margin:0">${d.next}</p></div>`;
  }
  wirePicker('#triagePicker', render);
  render('timeout');
})();
```

- [ ] **Step 5: 용어 추가**

```js
  "Reachability Analyzer": "출발지와 목적지를 지정하면 실제 패킷을 보내지 않고 라우팅·SG·NACL을 정적으로 분석해 도달 가능 여부를 알려주는 VPC 기능. OS 방화벽이나 앱 바인딩 문제는 볼 수 없습니다.",
```

- [ ] **Step 6: 퀴즈**

`data-qid="q-trace"`, `data-answer="a"`

> 질문: `curl`이 즉시 `connection refused`를 반환한다. 가장 먼저 확인할 것은?
>
> - A. **인스턴스 안에서 그 포트를 듣는 프로세스가 있는지, 바인딩 주소가 `127.0.0.1`은 아닌지**
> - B. SG 인바운드 규칙
> - C. 서브넷의 라우팅 테이블
> - D. NACL 아웃바운드의 ephemeral 범위
>
> 해설: **정답 A.** `refused`는 **RST가 돌아왔다**는 뜻이고, RST가 왔다는 건 패킷이 목적지까지 도달했다는 증거입니다. 네트워크 관문(B·C·D)은 이미 전부 통과한 거예요. 이 한 가지 구분만으로 용의자 절반이 사라집니다.

- [ ] **Step 7: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

반드시 확인할 것:
1. `🧊 NACL이 인바운드 차단`이 `🛡️ SG가 인바운드 차단`과 **거의 같은 한 줄**을 보여준다 (구별되지 않는다는 게 요점이다)
2. `🧊 NACL이 응답 차단`이 **두 줄**을 보여주고, 첫 줄 `action`이 초록 `ACCEPT`, 둘째 줄이 빨강 `REJECT`다
3. `🚫 기록이 아예 없음`만 "기록 없음" 판정을 낸다

---

## Task 12: 8장 — SG 참조, IP가 아니라 신원으로

**Files:**
- Modify: `aws_network_security.html` (`#trace` 뒤에 `<section id="ref">` 추가)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 3-tier SG 체인 모델(`alb-sg` → `app-sg` → `rds-sg`). **Task 14(10장)가 CloudFront prefix list 이야기에서, Task 17(13장)이 종합 레퍼런스에서 이 이름들을 그대로 재사용한다.** 이름을 바꾸지 말 것.

**섹션 헤더:** kicker `08 · 연동`, 제목 `🔗 IP가 아니라 <span style="color:var(--accent)">신원</span>으로`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.lead`: "여기서부터 2부입니다. 관문을 하나씩 아는 것과, 그것들을 **엮어서 구성하는 것**은 다른 기술이에요. 첫 번째 도구가 이겁니다."
2. `<h3>🏷️ SG 규칙의 source에 SG를 넣을 수 있다</h3>` — CIDR 대신 다른 SG의 id를 쓴다. 의미는 "**그 SG가 붙은 ENI에서 오는 트래픽**"이다. IP를 한 글자도 쓰지 않는다.
3. `<h3>💥 CIDR 기반 규칙이 무너지는 지점</h3>` — 오토스케일링으로 인스턴스가 교체되면 IP가 바뀐다. Fargate 태스크는 뜰 때마다 새 IP를 받는다. ALB 노드의 IP는 AWS가 예고 없이 바꾼다. **"어제까지 됐는데"의 대부분이 여기서 나온다** (7장 회수).
4. `.callout.key` — 프레이밍:
   > **SG를 방화벽 규칙이 아니라 라벨로 보세요.** `app-sg`는 "8080을 여는 규칙 뭉치"가 아니라 **"이 워크로드는 앱이다"라는 이름표**입니다. 규칙은 그 이름표들 사이의 관계를 적은 것이고요. 이렇게 보면 <a class="link" href="iam_tutorial.html">IAM에서 신원으로 권한을 준 것</a>과 정확히 같은 발상이라는 게 보입니다 — 축만 패킷으로 옮겼을 뿐이에요.
5. 데모 (Step 2)
6. `<h3>⛓️ 3-tier를 잠그는 표준형</h3>` — `.kv`로:
   - `alb-sg` — 인바운드 443 ← `0.0.0.0/0` · 아웃바운드 8080 → `app-sg`
   - `app-sg` — 인바운드 8080 ← `alb-sg` · 아웃바운드 5432 → `rds-sg`
   - `rds-sg` — 인바운드 5432 ← `app-sg` · 아웃바운드 없음
   IP가 한 번도 등장하지 않는다는 점을 짚는다.
7. `.callout.warn` — 순환 참조 주의: A가 B를 참조하고 B가 A를 참조하는 구성은 만들 수 있지만, **Terraform으로 관리하면 생성 순서가 꼬인다.** 규칙을 SG 리소스와 분리해 `aws_vpc_security_group_ingress_rule`로 따로 선언하는 게 관례다.
8. `.oneline` 요약: source에 SG를 쓰면 규칙이 **IP 변화에 면역**이 된다. 3-tier 잠그기는 IP 없이 SG 세 개의 관계만으로 끝난다.

- [ ] **Step 2: 데모 — SG 참조 체인 빌더**

```html
      <div class="demo" id="sgRef">
        <span class="demo-tag">SG 참조 체인</span>
        <p style="margin:0 0 4px">같은 3-tier를 네 가지 방식으로 잠가봅니다. 오토스케일링으로 앱 인스턴스가 교체되는 순간 무슨 일이 벌어지는지 보세요.</p>
        <div class="picker" id="sgRefPicker">
          <button class="pick on" data-k="cidr">📍 IP(CIDR)로 지정</button>
          <button class="pick" data-k="wide">🕳️ VPC 대역 전체 허용</button>
          <button class="pick" data-k="ref">🔗 SG 참조</button>
          <button class="pick" data-k="default">⚠️ 전부 기본 SG 공유</button>
        </div>
        <div id="sgRefOut"></div>
      </div>
```

```js
/* ============================================================
   데모 11 — SG 참조 체인 (8장)
   ============================================================ */
(function(){
  const out = $('#sgRefOut'); if(!out) return;
  const D = {
    cidr: { rule:"rds-sg 인바운드 5432 ← <span class='mono'>10.0.1.42/32</span>",
      scale:{ ok:false, t:"앱이 교체되면 <b>끊긴다</b>" },
      lateral:{ ok:true, t:"횡이동은 막힌다" },
      n:"의도는 맞았는데 <b>수명이 짧습니다</b>. 인스턴스가 교체되면 IP가 바뀌고 규칙은 그대로 남아요. 새 인스턴스는 거부되고, 게다가 <b>그 IP를 나중에 받은 다른 워크로드가 DB에 접근</b>하게 됩니다 — 조용히 생기는 구멍이에요." },
    wide: { rule:"rds-sg 인바운드 5432 ← <span class='mono'>10.0.0.0/16</span>",
      scale:{ ok:true, t:"교체돼도 유지된다" },
      lateral:{ ok:false, t:"<b>VPC 안 아무나 DB에 붙는다</b>" },
      n:"\"IP가 자꾸 바뀌니 대역을 열자\"는 가장 흔한 후퇴입니다. 안정적이긴 한데 <b>격리가 사라집니다</b>. 침해당한 배치 서버 하나가 곧바로 DB에 붙을 수 있어요. 편의를 위해 <b>횡이동 방어를 통째로 포기</b>한 겁니다." },
    ref: { rule:"rds-sg 인바운드 5432 ← <span class='mono'>app-sg</span>",
      scale:{ ok:true, t:"교체돼도 유지된다" },
      lateral:{ ok:true, t:"app-sg가 붙은 것만 통과" },
      n:"<b>둘 다 얻습니다.</b> IP를 안 쓰니 교체에 면역이고, 범위는 <code>app-sg</code>가 붙은 ENI로 정확히 한정됩니다. 새 인스턴스는 <b>SG를 달고 뜨는 순간</b> 자동으로 통과해요 — 규칙을 고칠 일이 없습니다. 이게 표준형입니다." },
    default: { rule:"세 계층이 모두 <span class='mono'>default</span> SG 하나를 공유",
      scale:{ ok:true, t:"교체돼도 유지된다" },
      lateral:{ ok:false, t:"<b>세 계층이 서로 완전히 열려 있다</b>" },
      n:"기본 SG에는 <b>자기 자신을 source로 하는 인바운드 규칙</b>이 들어 있습니다. 그래서 같은 기본 SG를 쓰는 리소스끼리는 <b>모든 포트가 열립니다</b>. 아무것도 설정하지 않았는데 통신이 되길래 그냥 두는 경우가 많은데, 계층 분리가 처음부터 없었던 셈이에요 — <a class='link' href='#pitfall'>14장</a>에서 다시 봅니다." }
  };
  function badge(o){
    return `<span class="vres ${o.ok?'allow':'deny'}" style="display:inline-block">${o.ok?'✅':'⛔'} ${o.t}</span>`;
  }
  function render(k){
    const d = D[k];
    out.innerHTML =
      `<div style="margin-top:12px" class="mono" style="font-size:13px">${d.rule}</div>
       <div class="kv" style="margin-top:10px">
         <dt>인스턴스 교체 후</dt><dd>${badge(d.scale)}</dd>
         <dt>횡이동(lateral) 방어</dt><dd>${badge(d.lateral)}</dd>
       </div>
       <div class="callout ${d.scale.ok && d.lateral.ok ? 'why' : 'warn'}" style="margin-bottom:0"><p style="margin:0">${d.n}</p></div>`;
  }
  wirePicker('#sgRefPicker', render);
  render('cidr');
})();
```

- [ ] **Step 3: 용어 추가**

```js
  "횡이동": "lateral movement. 공격자가 침해한 한 대를 발판 삼아 내부의 다른 시스템으로 옮겨 다니는 것. 계층 간 통신을 좁게 제한하면 이 이동이 어려워집니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-ref"`, `data-answer="c"`

> 질문: 오토스케일링 그룹의 앱 서버들이 RDS에 접속해야 한다. 가장 적절한 `rds-sg` 인바운드 규칙은?
>
> - A. `5432 ← 10.0.0.0/16` (VPC 대역 전체)
> - B. `5432 ← 10.0.1.42/32` (현재 앱 서버 IP)
> - C. **`5432 ← app-sg`**
> - D. `5432 ← 0.0.0.0/0` (SG는 VPC 밖에서 오는 트래픽을 어차피 못 받으므로)
>
> 해설: **정답 C.** B는 인스턴스가 교체되는 순간 깨지고, 심지어 그 IP를 나중에 받은 다른 워크로드가 DB에 접근하게 됩니다. A는 안정적이지만 VPC 안 아무나 DB에 붙을 수 있어 횡이동 방어가 사라져요. D는 위험하기도 하고 전제도 틀렸습니다 — 프라이빗 서브넷이라 실제로 인터넷에서 못 오는 것뿐이지, 라우팅이 바뀌면 그대로 노출됩니다. **경로에 의존한 보안은 보안이 아닙니다.**

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

---

## Task 13: 9장 — AWS Network Firewall

**Task 1의 V4 결과를 먼저 읽는다.** 삽입 라우팅의 정확한 구성이 검증 결과와 다르면 데모 데이터를 그에 맞춘다.

**Files:**
- Modify: `aws_network_security.html` (`#ref` 뒤에 `<section id="nfw">` 추가)
- Read: `docs/superpowers/notes/2026-08-12-aws-facts.md` (V4)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 없음

**섹션 헤더:** kicker `09 · 인라인`, 제목 `🚧 붙이는 게 아니라 <span style="color:var(--accent)">경유시키는</span> 통제`, 🔵 심화

- [ ] **Step 1: 본문 작성**

1. `.lead`: "SG와 NACL은 리소스에 **붙습니다**. Network Firewall은 다릅니다 — 트래픽이 **지나가게 만들어야** 해요. 그래서 이 장은 방화벽 규칙 이야기가 아니라 <a class='link' href='#route'>3장 라우팅</a> 이야기로 시작합니다."
2. `<h3>🔀 규칙을 아무리 써도 트래픽이 안 옵니다</h3>` — 가장 흔한 첫 좌절. 방화벽을 만들고 규칙을 넣어도 **라우팅을 안 바꾸면 아무 일도 일어나지 않는다.** 방화벽은 자기 서브넷에 **엔드포인트(ENI)** 를 만들고, 라우팅 테이블이 그걸 next hop으로 가리켜야 비로소 경로에 들어온다.
3. 데모 (Step 2)
4. `<h3>🔍 SG가 못 보는 것을 본다</h3>` — SG·NACL은 5-tuple(IP·포트·프로토콜)만 본다. Network Firewall은 **패킷 내용**을 본다:
   - **TLS SNI 기반 도메인 필터링** — `*.github.com`만 허용 같은 규칙. SG로는 불가능하다(깃허브 IP를 다 알 수도 없고 바뀐다)
   - **Suricata 규칙** — 알려진 악성 패턴, 프로토콜 이상 탐지
   - **세션 단위 상태 추적**
   그리고 **아웃바운드 통제**가 실질적 주용도임을 짚는다. "나가는 걸 도메인 단위로 막는다"가 데이터 유출 방어의 현실적인 수단이다 → 14장 연결.
5. `<h3>🏢 중앙 인스펙션 VPC</h3>` — VPC마다 방화벽을 두면 비싸다. TGW 허브에 인스펙션 VPC 하나를 두고 모든 VPC 간·외부 트래픽을 거기로 몰아 검사하는 게 표준 구성이다. → 12장 예고.
6. `.callout.warn` — **비대칭 라우팅 주의**: 가는 길만 방화벽을 지나고 오는 길은 안 지나면, 상태 추적이 깨져 정상 트래픽이 끊긴다. 양방향 모두 같은 방화벽 엔드포인트를 지나게 해야 한다.
7. `.oneline` 요약: Network Firewall의 절반은 **라우팅 설계**다. 규칙은 그 다음 문제고, 라우팅이 틀리면 규칙은 실행조차 되지 않는다.

- [ ] **Step 2: 데모 — 삽입 라우팅**

```html
      <div class="demo" id="nfwRoute">
        <span class="demo-tag">삽입 라우팅</span>
        <p style="margin:0 0 4px">방화벽은 이미 만들었고 규칙도 넣었습니다. 라우팅을 어떻게 바꾸느냐에 따라 결과가 완전히 달라져요.</p>
        <div class="picker" id="nfwPicker">
          <button class="pick on" data-k="none">1️⃣ 방화벽만 만듦 (라우팅 그대로)</button>
          <button class="pick" data-k="out">2️⃣ 나가는 길만 방화벽으로</button>
          <button class="pick" data-k="both">3️⃣ 양방향 모두 방화벽으로</button>
        </div>
        <div id="nfwOut"></div>
      </div>
```

```js
/* ============================================================
   데모 12 — Network Firewall 삽입 라우팅 (9장)
   ============================================================ */
(function(){
  const out = $('#nfwOut'); if(!out) return;
  const D = {
    none: {
      rt:[["워크로드 서브넷 RT","0.0.0.0/0 → <b>igw-abc</b>",false],
          ["IGW 엣지 연결 RT","(설정 없음)",false]],
      path:"인터넷 ↔ IGW ↔ 워크로드",
      ok:false,
      v:"방화벽을 <b>한 번도 지나지 않습니다.</b>",
      n:"규칙을 아무리 정교하게 써도 실행되지 않아요. 콘솔에는 방화벽이 <b>정상(Ready)</b>으로 보이고 요금도 나가는데, 검사한 트래픽은 0바이트입니다. \"방화벽을 켰는데 아무것도 안 잡힌다\"의 정체가 대개 이겁니다." },
    out: {
      rt:[["워크로드 서브넷 RT","0.0.0.0/0 → <b>vpce-fw</b> (방화벽 엔드포인트)",true],
          ["IGW 엣지 연결 RT","(설정 없음)",false]],
      path:"워크로드 → 방화벽 → IGW → 인터넷 &nbsp;/&nbsp; 인터넷 → IGW → <b>워크로드(방화벽 우회)</b>",
      ok:false,
      v:"<b style='color:var(--warn)'>비대칭 라우팅.</b> 나갈 때만 검사하고 들어올 때는 그냥 통과합니다.",
      n:"더 나쁜 건 <b>연결이 아예 깨질 수 있다</b>는 점이에요. 방화벽은 상태를 추적하는데 응답 패킷을 못 보니 세션이 성립하지 않습니다. 정상 트래픽이 끊기는데 규칙에는 아무 문제가 없어서 원인을 찾기 어려워요. <b>양방향을 반드시 같이 걸어야 합니다.</b>" },
    both: {
      rt:[["워크로드 서브넷 RT","0.0.0.0/0 → <b>vpce-fw</b>",true],
          ["IGW 엣지 연결 RT","10.0.1.0/24 → <b>vpce-fw</b>",true]],
      path:"인터넷 ↔ IGW ↔ <b>방화벽</b> ↔ 워크로드",
      ok:true,
      v:"<b style='color:var(--ok)'>양방향 모두 검사됩니다.</b>",
      n:"핵심은 <b>IGW에 라우팅 테이블을 연결(edge association)</b>한다는 발상입니다. \"게이트웨이도 라우팅 테이블을 가질 수 있다\"는 걸 모르면 떠올리기 어려운 구성이에요. 이제 도메인 필터링·Suricata 규칙이 실제로 동작합니다." }
  };
  function render(k){
    const d = D[k];
    const rows = d.rt.map(([n,v,on]) =>
      `<div class="flow-step" style="border-left:3px solid ${on?'var(--g-fw)':'var(--border)'}; padding-left:12px; margin:6px 0">
         <div><b style="color:${on?'var(--g-fw)':'var(--text-mut)'}">${esc(n)}</b></div>
         <div class="mono" style="font-size:13px">${v}</div>
       </div>`).join('');
    out.innerHTML =
      `<div style="margin-top:12px">${rows}</div>
       <div class="dim" style="font-size:13px; margin:10px 0 6px">실제 경로 — ${d.path}</div>
       <div class="verdict"><span class="vres ${d.ok?'allow':'deny'}">${d.v}</span></div>
       <div class="callout ${d.ok?'why':'warn'}" style="margin-bottom:0"><p style="margin:0">${d.n}</p></div>`;
  }
  wirePicker('#nfwPicker', render);
  render('none');
})();
```

- [ ] **Step 3: 용어 추가**

```js
  "Suricata": "오픈소스 침입 탐지 규칙 문법. AWS Network Firewall이 이 문법을 그대로 받아들여, 패킷 내용에 기반한 탐지·차단 규칙을 쓸 수 있습니다.",
  "SNI": "Server Name Indication. TLS 핸드셰이크 초반에 평문으로 오가는 접속 대상 도메인 이름. 암호화 전이라 중간 장비가 읽을 수 있어서 도메인 단위 필터링의 근거가 됩니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-nfw"`, `data-answer="b"`

> 질문: Network Firewall을 만들고 도메인 필터링 규칙까지 넣었는데, 아무 트래픽도 검사되지 않는다(로그가 비어 있다). 방화벽 상태는 `Ready`다. 가장 유력한 원인은?
>
> - A. 규칙 문법이 틀렸다
> - B. **라우팅 테이블이 방화벽 엔드포인트를 가리키지 않는다**
> - C. SG가 방화벽 엔드포인트를 차단하고 있다
> - D. NACL이 방화벽 서브넷을 막고 있다
>
> 해설: **정답 B.** Network Firewall은 SG·NACL처럼 리소스에 **붙는** 통제가 아니라, 라우팅으로 **경로에 끼워 넣는** 장비입니다. 라우팅을 바꾸지 않으면 트래픽이 근처에도 가지 않아요. 방화벽이 `Ready`이고 요금이 나가는데 검사량이 0이라면 거의 확실히 이겁니다.

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

---

## Task 14: 10장 — WAF

**Task 1의 V3 결과를 먼저 읽는다.** CloudFront managed prefix list의 정확한 이름을 확인하고 데모·본문에 반영한다.

**Files:**
- Modify: `aws_network_security.html` (`#nfw` 뒤에 `<section id="waf">` 추가)
- Read: `docs/superpowers/notes/2026-08-12-aws-facts.md` (V3)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 없음. Task 12(8장)의 `alb-sg` 이름을 그대로 재사용한다.

**섹션 헤더:** kicker `10 · L7`, 제목 `🌊 WAF — <span style="color:var(--accent)">연결된 뒤에</span> 보는 관문`, 🔵 심화

- [ ] **Step 1: 본문 작성**

1. `.lead`: "\"WAF를 붙였으니 SG는 좀 느슨해도 되겠지\" — 아닙니다. 둘은 **경쟁 관계가 아니라 축이 다른** 통제예요."
2. `<h3>📐 축이 다르다</h3>` — `.cmp2`:
   - 🛡️ SG: **연결 자체**를 막는다 / IP·포트로 판단 / TCP 핸드셰이크 전 / 요청 내용을 볼 수 없다
   - 🌊 WAF: **이미 맺어진 연결 위의 HTTP**를 본다 / URL·헤더·본문·쿠키로 판단 / 포트를 볼 수 없다(이미 443으로 들어온 뒤)

   결론: **SG가 못 보는 것을 WAF가 보고, WAF가 못 하는 것을 SG가 한다.** 하나로 다른 하나를 대신할 수 없다.
3. 데모 (Step 2)
4. `<h3>📦 어디에 붙는가</h3>` — WAF는 독립 장비가 아니라 **CloudFront · ALB · API Gateway · AppSync에 붙는 부착물**이다. 붙는 대상이 없으면 존재할 수 없고, 그래서 NLB(L4)에는 붙일 수 없다.
5. `<h3>🕳️ 가장 흔한 구멍 — 우회</h3>` — **이 장의 핵심.**
   - CloudFront에 WAF를 붙였다. 훌륭하다.
   - 그런데 공격자가 ALB의 DNS 이름을 알아내 **직접** 때리면? WAF는 CloudFront에 붙어 있으므로 아무 일도 하지 않는다.
   - 답: **`alb-sg`의 인바운드 source를 CloudFront origin-facing prefix list로 좁힌다.** (V3에서 확인한 정확한 이름을 여기 적는다. 이 prefix list가 SG 규칙 슬롯을 여러 개 차지한다는 점도 함께 적는다)
   - **8장이 회수되는 지점이다** — L7 통제의 구멍을 L3/L4 통제로 막는다.
6. `.callout.std` — 업계 표준: Managed rule group(공통 취약점·봇·평판 IP)을 먼저 켜되 처음에는 **Count 모드**로 두어 오탐을 관찰한 뒤 Block으로 바꾼다. 곧바로 Block으로 켜면 정상 트래픽을 막아 놓고 원인을 못 찾는다.
7. `.oneline` 요약: WAF는 SG를 대체하지 않는다. **L7 통제는 L3/L4로 경로를 하나로 좁혀 둘 때만 의미가 있다** — 우회로가 열려 있으면 규칙은 장식이다.

- [ ] **Step 2: 데모 — 누가 무엇을 막나**

```html
      <div class="demo" id="wafTest">
        <span class="demo-tag">누가 무엇을 막나</span>
        <p style="margin:0 0 4px">다섯 가지 요청을 던져 SG와 WAF가 각각 어떻게 반응하는지 봅니다. 한쪽만으로는 안 되는 이유가 드러납니다.</p>
        <div class="picker" id="wafPicker">
          <button class="pick on" data-k="normal">🙂 정상 GET /products</button>
          <button class="pick" data-k="sqli">💉 본문에 SQL 인젝션</button>
          <button class="pick" data-k="flood">🌊 초당 5,000회 요청</button>
          <button class="pick" data-k="ssh">🔑 22번 포트 스캔</button>
          <button class="pick" data-k="bypass">🕳️ ALB 직접 접근 (CloudFront 우회)</button>
        </div>
        <div id="wafOut"></div>
      </div>
```

```js
/* ============================================================
   데모 13 — 누가 무엇을 막나 (10장)
   ============================================================ */
(function(){
  const out = $('#wafOut'); if(!out) return;
  const D = {
    normal: { sg:[true,"443이 열려 있으니 통과"], waf:[true,"규칙에 걸리지 않음"],
      n:"둘 다 통과합니다. 정상 요청이 이렇게 흘러요." },
    sqli: { sg:[true,"443으로 온 정상 TCP 연결. <b>본문을 볼 수 없다</b>"],
      waf:[false,"<code>SQLi_BODY</code> 관리형 규칙에 매치"],
      n:"<b>SG는 이걸 절대 막을 수 없습니다.</b> 포트도 IP도 정상이고, 페이로드는 SG의 관측 범위 밖이에요. L7을 보는 통제가 없으면 이 요청은 그대로 앱까지 갑니다." },
    flood: { sg:[true,"각 연결이 개별적으로는 정상"],
      waf:[false,"Rate-based 규칙이 해당 IP를 일시 차단"],
      n:"SG에는 <b>\"초당 몇 번\"이라는 개념이 없습니다.</b> 규칙은 매칭이지 계수가 아니에요. 빈도 기반 통제는 WAF(또는 Shield)의 몫입니다." },
    ssh: { sg:[false,"22가 열려 있지 않아 <b>연결 자체가 성립 안 됨</b>"],
      waf:[null,"평가되지 않음 — HTTP 요청이 아니다"],
      n:"방향이 반대입니다. <b>WAF는 이걸 볼 수조차 없어요.</b> WAF는 ALB·CloudFront에 붙어 <b>HTTP 요청</b>을 검사하는데, 22번 포트 스캔은 애초에 그 앞까지 오지 않습니다. 이게 \"WAF가 있으니 SG는 느슨해도 된다\"가 틀린 이유예요." },
    bypass: { sg:[true,"<b><code>alb-sg</code>가 <code>0.0.0.0/0</code>이면 통과</b>"],
      waf:[null,"평가되지 않음 — WAF는 CloudFront에 붙어 있다"],
      n:"<b>이 장의 핵심입니다.</b> CloudFront에 아무리 정교한 WAF를 걸어도, 공격자가 ALB 주소로 직접 오면 그 규칙들은 <b>실행되지 않습니다</b>. <br><br>답은 L7이 아니라 <b>L3/L4</b>에 있어요 — <code>alb-sg</code>의 인바운드 source를 <b>CloudFront origin-facing prefix list</b>로 좁혀서, ALB가 CloudFront 외의 어디서도 연결을 받지 않게 만듭니다. <a class='link' href='#ref'>8장의 SG 참조</a>가 여기서 회수됩니다." }
  };
  function cell(v){
    if(v[0] === null) return `<span class="dim">— ${v[1]}</span>`;
    return `${v[0] ? '<b style="color:var(--ok)">통과</b>' : '<b style="color:var(--bad)">차단</b>'} <span class="dim">— ${v[1]}</span>`;
  }
  function render(k){
    const d = D[k];
    out.innerHTML =
      `<div class="kv" style="margin-top:12px">
         <dt>🛡️ Security Group</dt><dd>${cell(d.sg)}</dd>
         <dt>🌊 WAF</dt><dd>${cell(d.waf)}</dd>
       </div>
       <div class="callout ${k==='normal'?'why':'warn'}" style="margin-bottom:0"><p style="margin:0">${d.n}</p></div>`;
  }
  wirePicker('#wafPicker', render);
  render('normal');
})();
```

- [ ] **Step 3: 용어 추가**

```js
  "WAF": "Web Application Firewall. HTTP 요청의 URL·헤더·본문·쿠키를 검사해 차단하는 L7 통제. CloudFront·ALB·API Gateway 등에 붙여서 씁니다.",
  "Count 모드": "WAF 규칙을 차단하지 않고 매치 횟수만 세는 모드. 새 규칙을 켤 때 오탐을 먼저 관찰하려고 씁니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-waf"`, `data-answer="d"`

> 질문: CloudFront 앞단에 WAF를 붙여 SQL 인젝션과 봇을 차단하고 있다. 그런데 공격이 계속 앱에 도달한다. 확인해야 할 것은?
>
> - A. WAF 규칙을 Count 모드에서 Block 모드로 바꿨는지
> - B. ALB에도 별도의 WAF를 붙였는지
> - C. NACL이 공격자 IP를 차단하는지
> - D. **ALB의 SG가 CloudFront에서 오는 트래픽만 받도록 좁혀져 있는지**
>
> 해설: **정답 D.** WAF는 자기가 붙은 리소스로 오는 요청만 검사합니다. `alb-sg`가 `0.0.0.0/0`이면 공격자는 **CloudFront를 건너뛰고 ALB를 직접** 때릴 수 있고, 그 경로에는 WAF가 없어요. A도 실무에서 흔한 실수지만 이 상황(우회)의 답은 아니고, B는 비용이 두 배가 될 뿐 우회로 자체는 남습니다. **L7 통제는 경로가 하나로 좁혀져 있을 때만 유효합니다.**

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

`🔑 22번 포트 스캔`과 `🕳️ ALB 직접 접근`에서 WAF 칸이 **"평가되지 않음"** 으로 흐리게 나오는지 확인한다. 두 방향의 비대칭이 이 데모의 요점이다.

---

## Task 15: 11장 — VPC Endpoint, 네트워크와 신원이 만나는 곳

시리즈의 두 문서가 여기서 교차한다. `iam_tutorial.html`을 읽은 독자에게만 열리는 문이라 문서 전체에서 가장 보람 있는 장이다.

**Task 1의 V5 결과를 먼저 읽는다.**

**Files:**
- Modify: `aws_network_security.html` (`#waf` 뒤에 `<section id="endpoint">` 추가)
- Read: `docs/superpowers/notes/2026-08-12-aws-facts.md` (V5)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 없음

**섹션 헤더:** kicker `11 · 교차`, 제목 `🔒 인터넷을 거치지 않고 만나기 — <span style="color:var(--accent)">VPC Endpoint</span>`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.lead`: "프라이빗 서브넷의 앱이 S3에 파일을 올립니다. 이 트래픽은 어디로 갈까요? 기본 구성에서는 **NAT 게이트웨이를 타고 인터넷으로 나갔다가 돌아옵니다.** 같은 리전의 AWS 서비스인데도요."
2. `<h3>🚪 두 가지 Endpoint</h3>` — `.cmp2`:
   - **Gateway형** — 라우팅 테이블에 한 줄이 추가되는 방식. 지원 서비스가 제한적이다(V5 결과를 적는다). **요금이 없다.** SG를 붙일 수 없다(ENI가 아니니까).
   - **Interface형 (PrivateLink)** — 서브넷에 **ENI가 생긴다.** 그래서 **SG가 붙는다**(4장 회수). 거의 모든 AWS 서비스와 서드파티 SaaS를 지원한다. 시간당 요금과 데이터 처리 요금이 있다.
3. `<h3>💰 왜 쓰나 — 세 가지 이유</h3>`:
   - **보안** — 트래픽이 AWS 네트워크를 벗어나지 않는다. IGW·NAT 없이도 S3를 쓸 수 있으니 아웃바운드를 훨씬 좁게 잠글 수 있다
   - **비용** — NAT GW의 데이터 처리 요금이 사라진다. S3 트래픽이 많은 계정에서는 이것만으로 절감액이 크다
   - **통제** — 아래 항목
4. `<h3>⚖️ 관문이 둘 더 있다</h3>` — 네트워크를 다 통과해도 끝이 아니다.
   - **Endpoint 정책** — 이 엔드포인트를 통과하는 요청에만 적용되는 리소스 정책. "이 VPC에서는 우리 회사 버킷에만 접근 가능"을 강제할 수 있다
   - **IAM 정책** — 늘 있던 그것
   둘 다 통과해야 한다. 6장 데모의 `앱 → S3` 시나리오에서 관문 두 개가 더 있었던 이유가 이거다.
5. 데모 (Step 2)
6. `.callout.key` — **이 장의 정점**:
   > 지금까지 네트워크 통제는 "**어디서** 왔는가"만 물었고, IAM은 "**누가** 요청했는가"만 물었습니다. VPC Endpoint에서 두 축이 곱해집니다.
   > `aws:SourceVpce` · `aws:SourceVpc` 조건 키를 버킷 정책에 걸면 — **"이 역할이, 이 VPC 안에서 요청할 때만 허용"** 이 됩니다.
   > 자격 증명이 유출돼도 **공격자의 노트북에서는 쓸 수 없습니다.** <a class="link" href="iam_tutorial.html">IAM 튜토리얼</a>의 `Condition` 자리가 여기서 네트워크와 만납니다.
7. `.callout.warn` — 조심할 점: `aws:SourceVpce` 조건을 버킷 정책에 `Deny`로 걸 때, **콘솔에서의 접근도 함께 막힌다.** 관리자가 자기 발등을 찍는 전형적인 사고라 예외를 함께 설계해야 한다.
8. `.oneline` 요약: Endpoint는 경로를 짧게 만드는 도구이면서, **네트워크 경계를 IAM 조건으로 끌어올리는 유일한 다리**다.

- [ ] **Step 2: 데모 — Endpoint 정책 × IAM 정책**

```html
      <div class="demo" id="vpceEval">
        <span class="demo-tag">두 관문의 결합 판정</span>
        <p style="margin:0 0 4px">앱이 <span class="mono">s3:GetObject</span>로 <span class="mono">naru-prod-data</span> 버킷의 객체를 읽으려 합니다. 두 정책을 각각 골라 최종 판정을 보세요.</p>
        <div class="picker" id="vpcePicker">
          <button class="pick on" data-k="open">Endpoint 정책 · 전체 허용(기본)</button>
          <button class="pick" data-k="ours">Endpoint 정책 · 우리 계정 버킷만</button>
          <button class="pick" data-k="prefix">Endpoint 정책 · <span class="mono">logs/*</span> 접두어만</button>
        </div>
        <div class="picker" id="iamPicker" style="margin-top:10px">
          <button class="pick on" data-k="full">IAM · s3:* 허용</button>
          <button class="pick" data-k="get">IAM · GetObject만 허용</button>
          <button class="pick" data-k="none">IAM · S3 권한 없음</button>
        </div>
        <div id="vpceOut"></div>
      </div>
```

```js
/* ============================================================
   데모 14 — Endpoint 정책 × IAM 정책 (11장)
   ============================================================ */
(function(){
  const out = $('#vpceOut'); if(!out) return;
  const EP = {
    open: { ok:true,  t:"전체 허용 (기본값)",
      n:"Endpoint를 만들면 정책이 <b>전체 허용</b>으로 시작합니다. 그래서 대부분의 계정에서 이 관문은 사실상 없는 셈이에요." },
    ours: { ok:true,  t:"우리 계정 버킷만",
      n:"<code>aws:PrincipalAccount</code>나 리소스 ARN으로 범위를 좁힌 경우. <b>이 엔드포인트를 통해서는 남의 버킷에 접근할 수 없습니다</b> — 사내 데이터를 외부 버킷으로 빼내는 경로를 네트워크 층에서 막는 방법이에요." },
    prefix:{ ok:false, t:"<span class='mono'>logs/*</span> 접두어만 허용",
      n:"Endpoint 정책이 리소스를 <code>arn:aws:s3:::naru-prod-data/logs/*</code>로 한정한 경우입니다. 지금 요청은 <code>data/report.csv</code>라 <b>범위 밖</b>이에요. <br><br>주목할 점 — <b>IAM은 이 요청을 허용했습니다.</b> 권한은 충분한데 <b>이 통로로는 못 지나갑니다</b>. 같은 역할이라도 다른 경로(예: 인터넷 경유)로 오면 결과가 달라질 수 있어요. 이게 Endpoint 정책이 IAM과 별개로 존재하는 이유입니다." }
  };
  const IAM = {
    full: { ok:true,  t:"s3:* 허용" },
    get:  { ok:true,  t:"GetObject만 허용" },
    none: { ok:false, t:"S3 권한 없음" }
  };
  let ep = 'open', iam = 'full';
  function render(){
    const e = EP[ep], i = IAM[iam];
    const ok = e.ok && i.ok;
    let verdict, why;
    if(ok){
      verdict = "✅ 객체를 읽습니다";
      why = `${e.n} <br><br>두 관문이 <b>모두</b> 허용해야 통과합니다 — 하나라도 거부하면 끝이에요. <a class='link' href='iam_tutorial.html'>IAM 튜토리얼</a>에서 본 <b>명시적 거부 우선</b> 원칙이 여기서도 그대로 적용됩니다.`;
    } else if(!i.ok){
      verdict = "⛔ AccessDenied — IAM에서 거부";
      why = "네트워크는 완벽합니다. Endpoint까지 문제없이 도달했고 Endpoint 정책도 통과했어요. 그런데 <b>이 주체에게 권한이 없습니다.</b> <br><br>여기가 두 세계의 경계입니다 — <b>네트워크를 다 열어도 IAM이 막으면 못 합니다.</b> 반대도 마찬가지고요. 두 축은 서로를 대신하지 못합니다.";
    } else {
      verdict = "⛔ AccessDenied — Endpoint 정책에서 거부";
      why = e.n;
    }
    out.innerHTML =
      `<div class="kv" style="margin-top:12px">
         <dt>🔒 Endpoint 정책</dt><dd>${esc(e.t)} — ${e.ok?'<b style="color:var(--ok)">허용</b>':'<b style="color:var(--bad)">거부</b>'}</dd>
         <dt>👤 IAM 정책</dt><dd>${esc(i.t)} — ${i.ok?'<b style="color:var(--ok)">허용</b>':'<b style="color:var(--bad)">거부</b>'}</dd>
       </div>
       <div class="verdict"><span class="vres ${ok?'allow':'deny'}">${verdict}</span></div>
       <div class="callout ${ok?'why':'warn'}" style="margin-bottom:0"><p style="margin:0">${why}</p></div>`;
  }
  wirePicker('#vpcePicker', k => { ep = k; render(); });
  wirePicker('#iamPicker',  k => { iam = k; render(); });
  render();
})();
```

**요청 시나리오를 고정한다:** 이 데모의 요청은 항상 `s3:GetObject` on `naru-prod-data/data/report.csv`다. 그래야 `prefix` 정책이 **왜** 거부하는지가 분명해진다. 본문 안내 문구의 객체 경로를 이와 일치시킬 것.

- [ ] **Step 2-1: 3×3 조합을 전부 눌러 확인**

9개 조합 중 판정이 이렇게 나와야 한다.

| Endpoint 정책 \ IAM | s3:* | GetObject만 | 권한 없음 |
|---|---|---|---|
| 전체 허용 | ✅ | ✅ | ⛔ IAM |
| 우리 계정 버킷만 | ✅ | ✅ | ⛔ IAM |
| `logs/*`만 | ⛔ Endpoint | ⛔ Endpoint | ⛔ IAM |

IAM 거부가 Endpoint 거부보다 **우선 표시**된다(코드의 `else if(!i.ok)`가 먼저다). 이건 의도한 것이다 — 실무에서 IAM 거부가 훨씬 흔하고 먼저 확인할 것이기 때문이다.

- [ ] **Step 3: 용어 추가**

```js
  "VPC Endpoint": "VPC 안에서 AWS 서비스에 접근할 때 인터넷을 거치지 않게 해 주는 진입점. 라우팅 테이블 항목으로 동작하는 Gateway형과, ENI를 만드는 Interface형(PrivateLink)이 있습니다.",
  "PrivateLink": "Interface형 VPC Endpoint의 기반 기술. 내 VPC 안에 ENI를 만들어 상대 서비스로 연결하므로, 그 ENI에 Security Group을 붙일 수 있습니다.",
  "Endpoint 정책": "VPC Endpoint를 통과하는 요청에만 적용되는 리소스 정책. IAM 정책과 별개이며, 둘 다 통과해야 요청이 성공합니다.",
```

- [ ] **Step 4: 퀴즈**

`data-qid="q-endpoint"`, `data-answer="b"`

> 질문: S3 버킷 정책에 `aws:SourceVpce` 조건을 걸어 특정 VPC Endpoint를 통한 요청만 허용했다. 개발자의 노트북에서 유출된 액세스 키로 공격자가 `aws s3 cp`를 시도하면?
>
> - A. IAM 권한이 있으므로 성공한다
> - B. **거부된다. 공격자의 요청은 그 Endpoint를 통과하지 않았으므로 조건이 맞지 않는다**
> - C. SG가 막으므로 거부된다
> - D. NACL이 막으므로 거부된다
>
> 해설: **정답 B.** 이게 네트워크 경계와 신원 경계를 곱했을 때 생기는 힘입니다. 공격자는 유효한 자격 증명을 가졌지만 **요청이 우리 VPC Endpoint를 거치지 않았으므로** 조건이 불일치해 거부돼요. C·D는 방향이 틀렸습니다 — 공격자는 우리 VPC 안에 있지 않으니 SG도 NACL도 그 요청을 볼 기회가 없고, 판정은 전적으로 **S3 쪽에서** 일어납니다.

- [ ] **Step 5: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

`IAM · S3 권한 없음`을 골랐을 때, Endpoint 정책이 무엇이든 **IAM 거부 메시지**가 나오는지 확인한다.

---

## Task 16: 12장 — VPC끼리 잇기

데모가 없는 짧은 장이다. 12장의 역할은 9장의 "중앙 인스펙션 VPC"를 성립시키는 배경 지식을 주는 것이다.

**Files:**
- Modify: `aws_network_security.html` (`#endpoint` 뒤에 `<section id="peering">` 추가)
- Read: `docs/superpowers/notes/2026-08-12-aws-facts.md` (V2)

**Interfaces:**
- Consumes: 없음 (데모 없음)
- Produces: 없음

**섹션 헤더:** kicker `12 · 연결`, 제목 `🕸️ VPC끼리 <span style="color:var(--accent)">잇는</span> 방법과 그 한계`, 🔵 심화

- [ ] **Step 1: 본문 작성**

1. `.lead`: "VPC는 기본적으로 완전히 격리돼 있습니다. 잇는 방법이 몇 가지 있는데, 각각 **못 하는 일**이 뚜렷해서 그걸 먼저 아는 게 빠릅니다."
2. `<h3>🔗 Peering — 두 VPC를 직접 잇는다</h3>`
   - 양쪽 라우팅 테이블에 **모두** 상대 대역을 넣어야 한다. 한쪽만 넣으면 편도가 되고, 편도는 곧 timeout이다
   - **전이되지 않는다.** A–B와 B–C가 있어도 A–C는 통신할 수 없다. B를 경유하는 라우팅을 넣어도 안 된다 — AWS가 명시적으로 금지한다
   - **CIDR이 겹치면 아예 만들 수 없다.** 이게 "VPC를 만들 때 CIDR을 계획적으로 배정해야 하는" 이유다
   - SG 참조가 경계를 넘을 수 있다 (V2 결과를 여기 반영한다 — 같은 리전 한정인지 등)
3. `<h3>🚇 Transit Gateway — 허브를 둔다</h3>`
   - VPC가 늘어나면 Peering은 N×(N−1)/2개가 필요하다. 10개면 45개다. 관리가 불가능해진다
   - TGW는 허브 하나에 각 VPC를 한 번씩 붙인다. 라우팅 테이블도 TGW가 갖는다
   - **9장의 중앙 인스펙션 VPC가 여기서 성립한다** — TGW 라우팅으로 모든 VPC 간 트래픽을 검사 VPC로 몰 수 있다
4. `.callout.warn` — CIDR 겹침은 되돌리기 어렵다: VPC의 기본 CIDR은 **변경할 수 없다**. 겹친 걸 나중에 발견하면 한쪽을 새로 만들어 마이그레이션하는 것 외에 방법이 없다. **조직 차원의 CIDR 할당 계획**이 첫날에 필요한 이유다.
5. `.kv` — 언제 무엇을:
   - `Peering` — VPC 두세 개, 단순한 연결, 비용 최소
   - `Transit Gateway` — VPC가 여럿, 중앙 통제·인스펙션이 필요할 때
   - `PrivateLink` — **네트워크를 잇지 않고 서비스 하나만 노출**할 때. CIDR이 겹쳐도 되고, 상대 VPC 전체가 보이지 않아 가장 좁다
6. `.oneline` 요약: Peering은 전이되지 않고 CIDR이 겹치면 불가능하다. 규모가 커지면 TGW로 가고, **연결이 아니라 서비스 하나만 필요하면 PrivateLink가 가장 좁은 답**이다.

- [ ] **Step 2: 퀴즈**

`data-qid="q-peering"`, `data-answer="a"`

> 질문: VPC A–B, B–C 두 개의 Peering이 설정되어 있다. A에서 C로 통신하려면?
>
> - A. **A–C Peering을 새로 만들어야 한다. B를 경유하는 라우팅은 동작하지 않는다**
> - B. A의 라우팅 테이블에 C의 대역을 B의 Peering으로 보내는 줄을 추가하면 된다
> - C. B에서 IP 포워딩을 켜면 된다
> - D. 자동으로 통신된다. Peering은 전이적이다
>
> 해설: **정답 A.** VPC Peering은 **전이되지 않습니다.** B를 경유하는 라우팅을 넣어도 AWS가 그 패킷을 전달하지 않아요(B 오답). B 안에 NAT 인스턴스 같은 걸 직접 세워 포워딩하는 우회는 이론상 가능하지만 Peering 자체가 해 주는 일은 아니고 권장되지도 않습니다(C). VPC가 셋 이상으로 늘어나기 시작하면 이 지점이 **Transit Gateway로 넘어갈 신호**입니다.

- [ ] **Step 3: 용어 추가**

```js
  "Transit Gateway": "여러 VPC와 온프레미스 연결을 한 허브에 모아 잇는 라우터. VPC마다 한 번씩만 붙이면 되어, VPC가 늘어날 때 Peering의 조합 폭발을 피할 수 있습니다.",
```

- [ ] **Step 4: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

---

## Task 17: 13장 — 3-tier 레퍼런스

**Files:**
- Modify: `aws_network_security.html` (`#peering` 뒤에 `<section id="blueprint">` 추가)

**Interfaces:**
- Consumes: `wirePicker`, `esc`
- Produces: 없음. Task 12의 SG 이름(`alb-sg` · `app-sg` · `rds-sg`)을 그대로 쓴다.

**섹션 헤더:** kicker `13 · 종합`, 제목 `🏗️ 전부 합친 <span style="color:var(--accent)">3-tier</span> 레퍼런스`, 🟢 필수

- [ ] **Step 1: 본문 작성**

1. `.lead`: "열두 장에 걸쳐 통제를 하나씩 봤습니다. 이제 하나의 그림에 전부 얹고, 요청 하나가 겪는 일을 처음부터 끝까지 따라가 봅니다."
2. `<h3>📐 구성</h3>` — `.kv`로 전체 구성을 한 번에 나열한다:
   - **서브넷** — 퍼블릭 ×2(ALB) · 프라이빗 ×2(앱) · 격리 ×2(RDS), 각 AZ에 하나씩
   - **라우팅** — 퍼블릭은 `0.0.0.0/0 → IGW`, 프라이빗은 `→ NAT GW`, 격리는 `local`만
   - **NACL** — 전부 기본값 (5장의 결론)
   - **SG** — `alb-sg` → `app-sg` → `rds-sg` 참조 체인 (8장)
   - **엣지** — CloudFront + WAF, `alb-sg`는 CloudFront prefix list만 허용 (10장)
   - **Endpoint** — S3 Gateway Endpoint, 프라이빗·격리 서브넷 라우팅 테이블에 연결 (11장)
   - **아웃바운드** — 앱은 NAT을 통해 필요한 도메인만. Network Firewall이 SNI로 필터링 (9장)
3. 데모 (Step 2)
4. `.callout.key` — 설계 원칙 한 줄: **각 계층은 자기 바로 위 계층에서만 트래픽을 받는다.** 이 한 문장이 위 구성 전체를 설명한다. 인터넷은 CloudFront만, CloudFront는 ALB만, ALB는 앱만, 앱은 DB만.
5. `.oneline` 요약: 열세 장의 통제가 실제로는 **여섯 줄의 SG 규칙과 세 개의 라우팅 테이블**로 압축된다. 복잡해 보이는 건 개념이지 구성이 아니다.

- [ ] **Step 2: 데모 — 종합 여정 재생기**

```html
      <div class="demo" id="journey">
        <span class="demo-tag">요청 하나의 전체 여정</span>
        <p style="margin:0 0 4px">사용자가 <span class="mono">https://shop.naru.example/products</span>를 열었습니다. 구간을 골라 그 안에서 무슨 일이 일어나는지 보세요.</p>
        <div class="picker" id="journeyPicker">
          <button class="pick on" data-k="edge">① 엣지</button>
          <button class="pick" data-k="in">② VPC 진입</button>
          <button class="pick" data-k="app">③ 앱 → DB</button>
          <button class="pick" data-k="s3">④ 앱 → S3</button>
          <button class="pick" data-k="back">⑤ 응답</button>
        </div>
        <div id="journeyStage"></div>
        <div id="journeyOut"></div>
      </div>
```

```js
/* ============================================================
   데모 15 — 종합 여정 재생기 (13장)
   ============================================================ */
(function(){
  const stage = $('#journeyStage'), out = $('#journeyOut'); if(!stage || !out) return;
  const LEG = {
    edge: { steps:[
        ["Route 53", "var(--g-route)", "<code>shop.naru.example</code> → CloudFront 배포의 도메인"],
        ["CloudFront", "var(--accent-2)", "가장 가까운 엣지에서 캐시 확인. 히트면 여기서 끝난다"],
        ["AWS Shield", "var(--g-waf)", "L3/L4 DDoS 흡수 — 기본으로 켜져 있다"],
        ["WAF", "var(--g-waf)", "관리형 규칙 + rate limit. SQLi·봇·과도한 빈도를 여기서 끊는다 (<a class='link' href='#waf'>10장</a>)"]
      ],
      n:"운이 좋으면 <b>여정이 여기서 끝납니다.</b> 캐시 히트면 VPC까지 오지도 않아요. 그리고 WAF가 여기 있다는 건, 뒤의 ALB가 <b>이 경로로만</b> 트래픽을 받아야 의미가 있다는 뜻입니다." },
    in: { steps:[
        ["IGW", "var(--g-route)", "퍼블릭 서브넷 라우팅 테이블에 <code>0.0.0.0/0 → igw</code>가 있어서 들어온다 (<a class='link' href='#route'>3장</a>)"],
        ["NACL 인바운드", "var(--g-nacl)", "기본값이라 전부 허용 — 사실상 통과 (<a class='link' href='#nacl'>5장</a>)"],
        ["alb-sg 인바운드", "var(--g-sg)", "443 ← <b>CloudFront prefix list</b>. 직접 접근은 여기서 죽는다 (<a class='link' href='#waf'>10장</a>)"],
        ["ALB", "var(--accent)", "대상 그룹의 앱 인스턴스로 8080 전달"],
        ["app-sg 인바운드", "var(--g-sg)", "8080 ← <b>alb-sg</b>. IP가 아니라 신원으로 (<a class='link' href='#ref'>8장</a>)"]
      ],
      n:"ALB가 <b>연결을 한 번 끊고 새로 맺는다</b>는 점에 주목하세요. 앱이 보는 출발지 IP는 사용자가 아니라 ALB 노드입니다. 그래서 <code>app-sg</code>의 source가 <code>alb-sg</code>인 거고, 실제 사용자 IP는 <code>X-Forwarded-For</code> 헤더로 따로 전달됩니다." },
    app: { steps:[
        ["라우팅 (local)", "var(--g-route)", "격리 서브넷도 VPC 안이라 local로 간다. IGW·NAT 등장 안 함"],
        ["app-sg 아웃바운드", "var(--g-sg)", "5432 → rds-sg"],
        ["NACL", "var(--g-nacl)", "기본값 통과"],
        ["rds-sg 인바운드", "var(--g-sg)", "5432 ← <b>app-sg</b>. 오토스케일링으로 앱이 교체돼도 유효하다"]
      ],
      n:"격리 서브넷의 라우팅 테이블에는 <b><code>0.0.0.0/0</code> 항목이 아예 없습니다.</b> NAT도 IGW도 없어요. DB가 인터넷으로 나갈 이유가 없으니 <b>경로 자체를 만들지 않는</b> 겁니다 — 통제보다 강력한 건 경로의 부재입니다." },
    s3: { steps:[
        ["라우팅 (prefix list → vpce)", "var(--g-route)", "S3 대역은 Gateway Endpoint로. NAT을 타지 않는다 (<a class='link' href='#endpoint'>11장</a>)"],
        ["app-sg 아웃바운드", "var(--g-sg)", "443 허용"],
        ["Endpoint 정책", "var(--accent-2)", "우리 계정 버킷으로 범위 제한"],
        ["IAM 판정", "var(--accent-2)", "인스턴스 프로파일의 역할이 <code>s3:PutObject</code>를 갖는가"]
      ],
      n:"<b>네트워크를 다 통과하고도 관문이 둘 남아 있습니다.</b> 여기가 이 문서와 <a class='link' href='iam_tutorial.html'>IAM 튜토리얼</a>이 만나는 지점이에요. 버킷 정책에 <code>aws:SourceVpce</code>를 걸어 두면 <b>이 VPC 밖에서는 같은 역할로도 못 읽습니다.</b>" },
    back: { steps:[
        ["app-sg", "var(--g-sg)", "<b>검사하지 않는다</b> — 상태 유지라 응답은 자동 통과 (<a class='link' href='#sg'>4장</a>)"],
        ["NACL 아웃바운드", "var(--g-nacl)", "<b>다시 검사한다</b> — 목적지는 ALB의 ephemeral 포트 (<a class='link' href='#nacl'>5장</a>)"],
        ["ALB → CloudFront", "var(--accent)", "ALB가 자기 쪽 연결로 응답을 실어 보낸다"],
        ["CloudFront", "var(--accent-2)", "<code>Cache-Control</code>이 붙어 있으면 캐시에 저장 — 다음 요청은 ①에서 끝난다"]
      ],
      n:"가는 길과 오는 길의 <b>비대칭</b>이 마지막으로 한 번 더 나옵니다. SG는 응답을 검사하지 않고 NACL은 검사해요. 이 문서에서 다룬 가장 흔한 장애가 바로 여기, 이 한 칸에서 생깁니다." }
  };
  function render(k){
    const l = LEG[k];
    stage.innerHTML = '<div style="margin:12px 0">' + l.steps.map(([t,c,d]) =>
      `<div class="flow-step" style="border-left:3px solid ${c}; padding-left:12px; margin:6px 0">
         <div><b style="color:${c}">${esc(t)}</b></div>
         <div class="dim" style="font-size:13px">${d}</div>
       </div>`).join('') + '</div>';
    out.innerHTML = `<div class="callout why" style="margin-bottom:0"><p style="margin:0">${l.n}</p></div>`;
  }
  wirePicker('#journeyPicker', render);
  render('edge');
})();
```

- [ ] **Step 3: 퀴즈**

`data-qid="q-blueprint"`, `data-answer="c"`

> 질문: 이 레퍼런스 구성에서 RDS가 있는 격리 서브넷의 라우팅 테이블에는 무엇이 있어야 하나?
>
> - A. `0.0.0.0/0 → NAT GW` — DB도 패치를 받아야 하니까
> - B. `0.0.0.0/0 → IGW` — 관리 접속을 위해
> - C. **`local` 하나뿐. `0.0.0.0/0` 항목을 아예 만들지 않는다**
> - D. `0.0.0.0/0 → Network Firewall`
>
> 해설: **정답 C.** RDS는 관리형 서비스라 패치를 AWS가 처리하므로 인터넷으로 나갈 이유가 없습니다. 그러면 **경로 자체를 만들지 않는 것**이 가장 강한 통제예요 — SG를 잘못 열어도, NACL을 실수해도, 갈 길이 없으면 나가지 못합니다. **통제를 거는 것보다 경로를 없애는 게 낫다**는 게 이 구성의 설계 원칙입니다.

- [ ] **Step 4: 검사 · 브라우저 확인 · 커밋** (공통 절차 4~6)

---

## Task 18: 14장 함정과 원칙 + 15장 마무리

정적 콘텐츠 두 장을 한 태스크로 묶는다. 15장의 체크리스트는 `netsec:ckl` 키에 상태를 저장한다.

**Files:**
- Modify: `aws_network_security.html` (`#blueprint` 뒤에 `<section id="pitfall">`, `<section id="wrap">` 추가)

**Interfaces:**
- Consumes: `$`, `$$`, `LS`
- Produces: `#ckl` 체크리스트 위젯. Task 3에서 이미 배선된 `↺ 초기화` 버튼이 `netsec:ckl`을 함께 지운다.

- [ ] **Step 1: 14장 작성**

섹션 헤더: kicker `14 · 실무`, 제목 `🧨 실제로 사고가 나는 <span style="color:var(--accent)">여섯 자리</span>`, 🟢 필수

각 항목을 `.myth` 또는 `.callout.warn`으로 쓴다.

1. **`0.0.0.0/0`으로 열린 22번** — 계정을 만들자마자 전 세계에서 스캔이 들어온다. 답은 SG를 좁히는 게 아니라 **SSH를 아예 열지 않는 것**이다. SSM Session Manager를 쓰면 인바운드 포트 없이 셸에 붙을 수 있고 접속 기록이 CloudTrail에 남는다.
2. **기본 SG를 그냥 쓰기** — 자기 자신을 source로 하는 규칙 때문에 같은 기본 SG를 쓰는 리소스끼리 전부 열린다. 계층 분리가 처음부터 없다. (8장 회수)
3. **아웃바운드 무제한** — 기본값이고 대부분 그대로 둔다. 침해당했을 때 데이터가 나가는 문이자 공격자가 툴을 내려받는 문이다. 최소한 **DB 계층만이라도** 잠근다. 도메인 단위 통제가 필요하면 Network Firewall (9장).
4. **NACL을 보안 도구로 쓰기** — 규칙 수 한도가 낮고 무상태라 관리 비용이 크다. 목록 기반 차단은 WAF나 Network Firewall의 일이다. (5장 회수)
5. **다중 AZ 중 한쪽만 다른 설정** — "될 때도 있고 안 될 때도 있다"의 최다 원인. 서브넷은 AZ마다 별개 리소스이고 라우팅 테이블 연결도 별개다. (7장 회수)
6. **SG 규칙을 콘솔에서 손으로 고치기** — 누가 왜 열었는지가 남지 않는다. Terraform으로 관리하되 규칙을 SG 리소스와 분리해 선언하고, 규칙마다 `description`에 **티켓 번호와 이유**를 적는다.

`.callout.std` — 업계 표준 요약: 인바운드는 좁게 시작해 필요할 때 연다. 아웃바운드는 **DB 계층부터** 잠근다. SSH는 열지 않는다. NACL은 기본값으로 둔다. 모든 규칙은 코드로 관리한다.

`.oneline` 요약: 사고는 정교한 공격보다 **기본값을 그대로 둔 자리**에서 난다.

`data-qid="q-pitfall"`, `data-answer="b"`

> 질문: 운영 계정의 보안을 점검한다. 하나만 고칠 수 있다면?
>
> - A. NACL에 알려진 악성 IP 목록을 넣는다
> - B. **`0.0.0.0/0`에서 22번이 열린 SG를 찾아 닫고 SSM Session Manager로 전환한다**
> - C. 모든 서브넷에 커스텀 NACL을 만든다
> - D. VPC Flow Logs를 켠다
>
> 해설: **정답 B.** 인터넷에 열린 SSH는 지금 이 순간에도 무차별 대입을 받고 있는 **현재진행형 노출**입니다. A는 목록 관리 비용에 비해 효과가 적고 NACL의 규칙 수 한도에 금방 걸려요. C는 오히려 ephemeral 함정으로 장애를 만들 가능성이 큽니다. D는 좋은 일이지만 **탐지**이지 **차단**이 아닙니다 — 열린 문을 닫는 게 먼저예요.

- [ ] **Step 2: 15장 작성**

섹션 헤더: kicker `15 · 마무리`, 제목 `🏁 내 VPC에는 <span style="color:var(--accent)">몇 개가 열려</span> 있나`, 🟢 필수

1. `.lead` — 히어로의 자가진단을 회수한다: "처음에 물었던 여섯 가지를 다시 떠올려 보세요. 이제 각각이 어느 장의 이야기였는지 말할 수 있을 겁니다."
2. `<h3>🧭 한 장으로 줄이면</h3>` — `.kv`로 문서 전체 요약:
   - **경로** — 통제 이전에 경로가 있는지 본다. 경로 없음과 차단은 증상이 같다
   - **SG** — ENI에 붙고, allow만 있고, 순서가 없고, 상태를 기억한다
   - **NACL** — 서브넷에 붙고, deny를 쓸 수 있고, 번호 순이고, **기억하지 않는다**
   - **순서** — 인바운드는 라우팅 → NACL → SG → OS, 응답은 SG를 건너뛰고 NACL만 다시 본다
   - **진단** — `refused`면 네트워크를 그만 본다. `timeout`이면 어디까지 갔는지부터 확정한다
   - **연동** — IP가 아니라 SG를 참조한다. 경로를 없앨 수 있으면 통제보다 낫다
3. 체크리스트 (Step 3)
4. `<h3>📚 다음에 읽을 것</h3>` — `.kv`로 시리즈 내 링크:
   - `iam_tutorial.html` — 같은 계정의 **API 층** 통제. 11장에서 만난 그 축
   - `rbac_tutorial.html` — 애플리케이션 안의 인가
   - `network_basics.html` — 이 문서가 전제한 네트워크 원리
   - `https_tutorial.html` — 9장의 SNI가 왜 평문인지
5. `.oneline` 요약: 관문의 순서를 알면 "왜 안 되지"가 검색이 아니라 **추론**이 된다.

`data-qid="q-wrap"`, `data-answer="a"`

> 질문: 이 문서 전체를 한 문장으로 줄이면?
>
> - A. **패킷 하나가 통과하는 관문의 목록과 순서를 알면, 증상에서 원인을 역추적할 수 있다**
> - B. SG를 좁게 쓰고 NACL로 이중 방어를 하면 안전하다
> - C. WAF와 Network Firewall을 도입하면 대부분의 공격을 막을 수 있다
> - D. 모든 서브넷을 프라이빗으로 만들고 NAT을 쓰면 된다
>
> 해설: **정답 A.** B의 "NACL 이중 방어"는 이 문서가 계속 반박한 것이고(5장), C는 도구를 늘리는 게 구조를 대신하지 못한다는 10장의 논지와 어긋나며, D는 구성 하나를 정답처럼 외우는 태도라 이 문서가 피하려던 바로 그것입니다. **순서를 아는 것**이 도구를 아는 것보다 오래 갑니다.

- [ ] **Step 3: 체크리스트 위젯**

```html
      <h3>✅ 내 계정에 적용해 볼 것</h3>
      <div class="ckl" id="ckl">
        <div class="ck" data-k="ssh"><span class="cb">✓</span><span class="ct"><code>0.0.0.0/0</code>에서 <b>22·3389</b>가 열린 SG가 있는지 찾아본다</span></div>
        <div class="ck" data-k="default"><span class="cb">✓</span><span class="ct"><b>기본 SG</b>를 그대로 쓰는 리소스가 있는지 확인한다</span></div>
        <div class="ck" data-k="egress"><span class="cb">✓</span><span class="ct"><b>DB 계층</b>의 아웃바운드를 잠근다</span></div>
        <div class="ck" data-k="ref"><span class="cb">✓</span><span class="ct">SG 규칙에 박힌 <b>개별 IP</b>를 SG 참조로 바꾼다</span></div>
        <div class="ck" data-k="nacl"><span class="cb">✓</span><span class="ct">커스텀 NACL이 있다면 <b>ephemeral 범위</b>가 열려 있는지 확인한다</span></div>
        <div class="ck" data-k="rt"><span class="cb">✓</span><span class="ct">AZ별 서브넷의 <b>라우팅 테이블 연결</b>이 정말 같은지 대조한다</span></div>
        <div class="ck" data-k="vpce"><span class="cb">✓</span><span class="ct">S3·DynamoDB 트래픽이 NAT을 타고 있다면 <b>Gateway Endpoint</b>를 만든다</span></div>
        <div class="ck" data-k="flow"><span class="cb">✓</span><span class="ct"><b>VPC Flow Logs</b>를 켜고 한 줄을 직접 읽어 본다</span></div>
        <div class="ck-score" id="cklScore"></div>
      </div>
```

```js
/* ============================================================
   데모 16 — 마무리 체크리스트 (15장)
   ============================================================ */
(function(){
  const ckl = $('#ckl'); if(!ckl) return;
  const done = new Set(LS.get('ckl', []));
  const items = $$('.ck', ckl);
  const score = $('#cklScore');
  function upd(){
    score.textContent = `${done.size} / ${items.length} 확인함`;
    LS.set('ckl', [...done]);
  }
  items.forEach(el => {
    const k = el.dataset.k;
    if(done.has(k)) el.classList.add('on');
    el.setAttribute('tabindex', '0');
    el.setAttribute('role', 'checkbox');
    el.setAttribute('aria-checked', done.has(k) ? 'true' : 'false');
    const toggle = () => {
      el.classList.toggle('on');
      const on = el.classList.contains('on');
      el.setAttribute('aria-checked', on ? 'true' : 'false');
      if(on) done.add(k); else done.delete(k);
      upd();
    };
    el.addEventListener('click', toggle);
    el.addEventListener('keydown', e => {
      if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); toggle(); }
    });
  });
  upd();
})();
```

**주의:** 점수 표시 엘리먼트의 클래스는 `ck-score`다(`ckl-score`가 아니다). Task 3에서 남긴 CSS의 클래스명과 일치해야 한다.

- [ ] **Step 4: 검사 · 브라우저 확인 · 커밋**

체크리스트를 3개 켜고 새로고침해 **상태가 유지되는지**, `↺ 초기화` 후 전부 꺼지는지 확인한다.

```bash
python3 tools/check_tutorial.py --allow-missing-anchors aws_network_security.html
git add aws_network_security.html
git commit -m "AWS 네트워크 보안 튜토리얼: 14장 함정과 원칙, 15장 마무리"
```

---

## Task 19: 부록 A · B

이 태스크가 끝나면 **`[anchor]` 위반이 0이 되어야 한다.** 히어로의 `.map-grid`가 가리키던 17개 섹션이 전부 존재하게 되기 때문이다.

**Files:**
- Modify: `aws_network_security.html` (`#wrap` 뒤에 `<section id="appendix-cli">`, `<section id="appendix-map">` 추가)

**Interfaces:**
- Consumes: Prism (`language-bash` 코드 블록)
- Produces: 없음

- [ ] **Step 1: 부록 A 작성 — 진짜 명령어**

섹션 헤더: kicker `부록 A`, 제목 `⌨️ 진짜 명령어로 확인해 보기`, 🔵 심화

`network_basics.html`의 "진짜 명령어로 확인해 보기" 패턴을 따른다. 각 명령을 `<pre><code class="language-bash">`로 넣고 그 아래에 무엇을 보라는 설명을 붙인다.

1. **내 SG 규칙 전부 보기**

```bash
aws ec2 describe-security-groups \
  --query 'SecurityGroups[].{Name:GroupName,Id:GroupId,In:IpPermissions}' \
  --output json
```

2. **인터넷에 열린 위험한 포트 찾기** — 14장의 첫 항목을 실제로 점검한다

```bash
aws ec2 describe-security-groups \
  --filters Name=ip-permission.cidr,Values=0.0.0.0/0 \
  --query 'SecurityGroups[].{Id:GroupId,Name:GroupName}' \
  --output table
```

3. **라우팅 테이블 확인** — "퍼블릭 서브넷"의 실체를 눈으로 본다

```bash
aws ec2 describe-route-tables \
  --query 'RouteTables[].{Id:RouteTableId,Subnets:Associations[].SubnetId,Routes:Routes[].[DestinationCidrBlock,GatewayId,NatGatewayId]}' \
  --output json
```

4. **Reachability Analyzer 실행**

```bash
aws ec2 create-network-insights-path \
  --source eni-0a1b2c3d --destination eni-0e5f6g7h \
  --protocol tcp --destination-port 5432

aws ec2 start-network-insights-analysis \
  --network-insights-path-id nip-xxxxxxxx
```

5. **Flow Logs 조회 (CloudWatch Logs Insights 쿼리)** — 7장에서 본 필드를 실제로 써 본다

```
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = "REJECT"
| stats count(*) by dstPort, srcAddr
| sort by count(*) desc
| limit 20
```

(이 블록은 bash가 아니므로 `language-bash`를 붙이지 않는다.)

6. **인스턴스 안에서 확인할 것** — 7장의 `refused` 분기

```bash
ss -tlnp                 # 어떤 포트를 누가 듣고 있나, 바인딩이 0.0.0.0인가 127.0.0.1인가
sudo iptables -L -n -v   # OS 방화벽이 걸려 있나 (SG와는 별개다)
curl -v --max-time 5 http://10.0.2.10:5432   # 옆 계층까지 닿는지
```

`.callout.warn` — 위 명령은 전부 **읽기 전용**이다. `authorize-security-group-ingress` 같은 변경 명령은 이 부록에 넣지 않는다. "콘솔이나 CLI에서 손으로 고치지 말라"는 14장의 권고와 어긋나기 때문이다.

- [ ] **Step 2: 부록 B 작성 — 다른 이름, 같은 이야기**

섹션 헤더: kicker `부록 B`, 제목 `🗺️ 다른 이름, 같은 이야기`, 🔵 심화

`.kv`로 매핑한다.

- **GCP** — VPC Firewall Rules. **네트워크 태그**나 서비스 계정으로 대상을 지정한다(SG 참조와 같은 발상). SG와 달리 **우선순위와 deny가 있다.** 서브넷 단위 NACL에 해당하는 건 따로 없고 방화벽 규칙 하나로 통합돼 있다.
- **Azure** — Network Security Group(NSG). 이름은 AWS의 SG와 같지만 동작은 **중간**이다 — **우선순위가 있고 deny를 쓸 수 있는데 상태는 유지한다.** 서브넷과 NIC 양쪽에 붙일 수 있어서 AWS의 SG와 NACL이 하나로 합쳐진 모양에 가깝다.
- **온프레미스 DMZ** — 존(zone) 모델. 퍼블릭/프라이빗/격리 3계층은 사실 **DMZ·내부망·데이터존**을 클라우드 어휘로 옮긴 것이다. 달라진 건 방화벽이 물리 장비가 아니라 **모든 ENI 앞에 분산되어 있다**는 점 — 그래서 "내부망은 신뢰한다"는 전제가 성립하지 않고 계층 간에도 통제를 건다.
- **Kubernetes** — NetworkPolicy. **라벨 셀렉터**로 대상을 지정하는데 이게 SG 참조와 정확히 같은 아이디어다. 기본이 전부 허용이고 정책을 붙이는 순간 그 파드가 화이트리스트 모드로 바뀐다는 점만 반대다.

`.callout.key` — 마무리:
> 이름은 다 다르지만 질문은 하나입니다. **"이 트래픽을, 어디서 온 무엇으로 식별하고, 어느 지점에서 판정할 것인가."** IP로 식별하면 관리가 무너지고, **신원(태그·SG·라벨)으로 식별하면 살아남습니다.** 어느 클라우드로 옮기든 이 감각은 그대로 갑니다.

- [ ] **Step 3: 전체 검사 — 이번엔 `[anchor]`까지 통과해야 한다**

Run: `python3 tools/check_tutorial.py aws_network_security.html`
Expected: `OK aws_network_security.html (섹션 18 · 퀴즈 15 · 데모 14)`

숫자가 다르면 빠진 게 있다. 섹션 18 = 히어로 1 + 본문 15 + 부록 2. 퀴즈 15 = 본문 장마다 1개(부록에는 없음). 데모 14 = 파일 구조 표의 목록.

- [ ] **Step 4: 커밋**

```bash
python3 tools/check_tutorial.py aws_network_security.html && \
git add aws_network_security.html && \
git commit -m "AWS 네트워크 보안 튜토리얼: 부록 A(명령어)·B(타 플랫폼 매핑)"
```

---

## Task 20: 시리즈 인덱스 등록과 최종 점검

**Files:**
- Modify: `index.html`
- Modify: `docs/superpowers/specs/2026-08-12-aws-network-security-tutorial-design.md`

**Interfaces:**
- Consumes: 없음
- Produces: 없음

**주의:** `index.html`에는 이미 커밋되지 않은 변경(IAM 카드의 태그 수정)이 있다. **그 변경을 되돌리거나 건드리지 말고** 카드 추가와 문서 수 갱신만 얹는다. 커밋 시 두 변경이 함께 올라가므로, 작업 전 `git diff index.html`로 기존 변경을 먼저 확인한다.

- [ ] **Step 1: 색상 토큰 추가**

`index.html`의 `:root`에서 색상 줄에 `--vpc:#fb7185;`를 추가한다.

```css
  --net:#38bdf8; --auth:#fbbf24; --authz:#c084fc; --https:#2dd4bf; --iam:#ff9f43; --vpc:#fb7185;
```

- [ ] **Step 2: 카드 추가**

IAM 카드(`iam_tutorial.html`) **바로 뒤**에 넣는다. 두 문서가 짝이라 나란히 있어야 한다.

```html
    <a class="card" href="aws_network_security.html" style="--c:var(--vpc)">
      <div class="top">
        <span class="ic">🧱</span>
        <span class="no">Cloud Network</span>
        <span class="new">NEW</span>
      </div>
      <h2>AWS 네트워크 보안 튜토리얼 — 관문의 순서로 이해하기</h2>
      <p>"SG를 <code>0.0.0.0/0</code>으로 다 열었는데 왜 timeout인가"에서 출발합니다. 라우팅·NACL·SG·Network Firewall·WAF·VPC Endpoint를
      <b>하나의 패킷이 통과하는 관문의 순서</b>로 다시 세우고, 각 관문이 막았을 때 <b>내가 보게 되는 증상</b>까지 짝지어 봅니다. 앞의 IAM 튜토리얼이 API 층에서 한 일을 패킷 층에서 합니다.</p>
      <div class="tags"><i>VPC · 서브넷 · ENI</i><i>라우팅 · IGW · NAT</i><i>Security Group</i><i>NACL · ephemeral</i><i>관문의 순서</i><i>Flow Logs 진단</i><i>SG 참조</i><i>Network Firewall</i><i>WAF · 우회 차단</i><i>VPC Endpoint</i></div>
      <span class="go">열어 보기 <span class="ar">→</span></span>
    </a>
```

- [ ] **Step 3: 문서 수 갱신**

```html
    <span>🗂️ <b>6개 문서</b></span>
```

- [ ] **Step 4: 검사**

Run: `python3 tools/check_tutorial.py index.html aws_network_security.html`
Expected: 둘 다 `OK`.

- [ ] **Step 5: 최종 수동 점검 — spec §9 완료 기준**

`open index.html` 후 아래를 전부 확인한다. 하나라도 실패하면 고치고 다시 확인한다.

- [ ] 인덱스에 카드 6장이 보이고, 새 카드가 로즈 색으로 강조된다
- [ ] 카드를 눌러 튜토리얼이 열린다
- [ ] 목차에 18개 항목이 있고 스크롤하면 현재 위치가 따라온다
- [ ] 데모 14종을 전부 눌러 본다. 콘솔 오류 0건
- [ ] 퀴즈 15개를 풀면 진행률이 100%에 도달한다
- [ ] 용어사전 드로어에 항목이 20개 이상 있고 검색이 동작한다
- [ ] `↺ 초기화` 후 새로고침하면 진행률·체크리스트가 초기화된다
- [ ] 개발자도구 Network 탭에 **요청이 문서 자신 1건뿐이다**
- [ ] 창 폭을 375px로 줄여도 가로 스크롤이 없고 `☰ 목차` 버튼이 동작한다
- [ ] `Tab`만으로 데모 버튼·퀴즈 보기·체크리스트에 접근할 수 있고 포커스 링이 보인다
- [ ] `file://` 경로로 직접 열어도 전부 동일하게 동작한다

- [ ] **Step 6: 커밋**

```bash
git add index.html
git commit -m "시리즈 인덱스에 AWS 네트워크 보안 튜토리얼 추가"
```

- [ ] **Step 7: spec 완료 기준 갱신**

`docs/superpowers/specs/2026-08-12-aws-network-security-tutorial-design.md`의 §9 체크박스를 실제 확인 결과로 채우고 커밋한다.

```bash
git add docs/superpowers/specs/2026-08-12-aws-network-security-tutorial-design.md
git commit -m "설계 문서 완료 기준 갱신"
```
