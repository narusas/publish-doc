# 남겨 둔 것들 — 2026-08-14

`aws_network_security.html` 작업을 마치며, 알고도 고치지 않은 것과 이번 범위 밖에서
발견된 것을 기록한다. 게시를 막지 않는다고 판단한 항목들이다.

## 1. 다른 튜토리얼 3종에 같은 모바일 버그가 있다

**이번 계획 범위 밖이라 손대지 않았다. 별건으로 판단이 필요하다.**

모바일에서 `☰ 목차` 드로어를 열면 그 안의 어떤 것도 누를 수 없다. `#scrim`이
`#sidebar`보다 위에 있어서, 탭하면 항목이 눌리는 대신 드로어가 닫힌다.

| 파일 | `#sidebar` | `#scrim` | 상태 |
|---|---|---|---|
| `aws_network_security.html` | 160 (모바일) | 150 | **수정됨** |
| `iam_tutorial.html` | 50 | 150 | 버그 있음 |
| `rbac_tutorial.html` | 50 | 150 | 버그 있음 |
| `network_basics.html` | 50 | 150 | 버그 있음 |
| `https_tutorial.html` | 50 | 60 | 버그 있음 |
| `oauth2_tutorial.html` | — | 없음 | 해당 없음 |

수정 방법은 `aws_network_security.html`의 `@media(max-width:980px)` 블록 참고 —
그 안에서만 `#sidebar`의 `z-index`를 스크림 위로 올렸다. 데스크톱 레이어링은 건드리지 않는다.

함께 고칠 것: TOC 링크 클릭 핸들러가 `sidebar.open`만 지우고 `scrim.open`은 남겨 두면,
내비게이션 후에도 화면을 덮는 오버레이가 남는다. 첫 버그에 가려져 있던 문제다.

## 2. `oauth2_tutorial.html`이 외부 폰트를 불러온다

`oauth2_tutorial.html:8`에 Google Fonts `@import`가 있다. [index.html](../../../index.html)은
"각 파일은 외부 CDN이나 스크립트를 전혀 불러오지 않는 단일 HTML이라, 내려받아 오프라인에서
열어도 그대로 동작합니다"라고 말하는데, 그 문서만 예외다.

## 3. 검사기가 잡는 기존 파일의 결함

`python3 tools/check_tutorial.py *.html`로 재현된다. 전부 이번 작업 이전부터 있던 것이다.

- `https_tutorial.html` — `id="tooltip"` 실제 중복, meta description 없음
- `network_basics.html` — 죽은 앵커 `#appendix-encoding`
- `rbac_tutorial.html` — meta description 없음
- `oauth2_tutorial.html` — 위 폰트 문제 + meta description 없음
- 네 파일이 `// @GLOSSARY_END` 마커를 쓰지 않아 용어 검사가 통째로 오탐을 낸다.
  이건 파일의 결함이 아니라 검사기가 새 문서용으로 정한 관례의 한계다.

## 4. `aws_network_security.html`에 남긴 것

- **사장된 CSS 약 12KB (전체 35KB 중 34%)** — `iam_tutorial.html`에서 뼈대를 복제할 때
  딸려 온 IAM 전용 컴포넌트(`.ar-*` `.tag-*` `.ladder` `.esc-*` 등). 사용처가 0이지만
  게시 직전에 걷어내는 건 회귀 위험 대비 이득이 없다고 판단했다. `.ev-*`는 관문 파이프라인
  주제와 맞아 재사용 여지가 있다.
- **`.pick` 버튼 88개에 `aria-pressed` 없음** — 토글이 아니라 라디오형 선택이라 치명적이지
  않지만, 접근성을 더 다듬는다면 첫 후보다.
- **체크리스트 점수가 "9 / 8"처럼 나올 수 있음** — 저장된 키 목록과 현재 항목 수가 어긋나면
  발생한다. 항목을 추가·삭제하거나 `data-k`를 바꾸면 재현된다.
- **퀴즈 id `q-outside`가 섹션 id `attach`와 어긋남** — 1장을 재작성하며 섹션 이름은 바꾸고
  퀴즈 id는 유지했다. 기존 독자의 진행률 기록을 보존하려는 의도였다. 바꾸려면 위의
  체크리스트 문제와 같은 종류의 마이그레이션이 필요하다.

## 5. 사실 검증의 교훈

이 문서를 만들며 사실 오류 **네 건**이 리뷰에서 걸렸고, **전부 계획 문서에서 나왔다** —
구현 과정에서 생긴 게 아니라 기억으로 초안을 쓴 데서 나왔다.

1. Flow Logs가 NACL 차단을 기록하지 않는다 (틀림 — SG와 똑같이 `REJECT`를 남긴다)
2. Flow Logs 집계 주기 5분 (틀림 — 10분 기본 / 1분)
3. `local` 라우트의 타깃을 바꿀 수 없다 (틀림 — 바꿀 수 있고, 그게 동서 검사의 원리다)
4. Transit Gateway를 쓰면 각 VPC가 라우팅 테이블을 갖지 않는다 (틀림 — 여전히 필요하다)

반대 방향의 실수도 한 번 있었다. 구현자가 실재하는 규칙명 `SQLi_BODY`를 "지어낸 것 같다"며
일반 표현으로 뭉갠 일이다. **올바른 처리는 "불확실하면 완화"가 아니라 "확인한 뒤 유지하거나
제거"다.** 참인 구체를 뭉개면 독자가 찾아볼 수 있는 유일한 단서를 잃는다.

`docs/superpowers/notes/2026-08-12-aws-facts.md`가 이 문서의 근거 기록이다. 서술을 고칠 때는
그 파일을 먼저 보고, 없는 사실은 확인한 뒤에 쓴다.
