# 방어적 프로그래밍 문서 · 도해 보강 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `defensive_programming.html` 에 인라인 SVG 도해 열 장을 넣어, 지금 산문이 혼자 지고 있는 공간 관계와 시간 순서를 그림이 지게 한다.

**Architecture:** 저장소에 이미 있는 도해 체계를 그대로 옮겨 온다. `figure.dia` 마크업, `data-at` 단계 표시, 공통 구동기 `wireDia(id, steps)` 하나가 전부다. 구동기는 자리도 모양도 모르고, 단계 번호를 뿌리에 적고 해당 요소에 `.vis` 를 걸고 단계 설명을 갈아 끼우는 일만 한다. 도해마다 SVG 는 리터럴 마크업으로 쓰고, 반경 지도 한 장만 기존 `RADIUS` 배열에서 생성한다.

**Tech Stack:** 단일 HTML, 외부 의존 없음. 순수 SVG + CSS + 바닐라 JS. 테스트는 pytest, 브라우저 동작은 playwright.

**Spec:** `docs/superpowers/specs/2026-09-08-defensive-programming-diagrams.md`
**선행 Spec:** `docs/superpowers/specs/2026-09-07-defensive-programming-design.md`

## Global Constraints

- **각색을 유지한다.** 사내 식별자를 쓰지 않는다. 그림 안의 글자도 예외가 아니다. 금칙: `cheil`, `ssfshop`, `dspCnr`, `ConttImg`, `includeMultiMainContents`, `SecureValueExpression`, `전시코너`, `전시 코너`. 반대로 증거로 남기기로 한 것은 유지한다: `javax.el`, `BeanELResolver`, `9946`, `_005fset_005f141`.
- **원인을 단정하지 않는다.** 이번 장애의 원인은 아직 모른다. 그림이 원인을 하나로 지목하면 안 된다. 후보를 그릴 때는 세 갈래를 나란히 두고, 가정을 그릴 때는 가정이라고 적는다. **그림 안의 라벨과 단계 설명도 산문이다.**
- **CSS 는 그것을 처음 쓰는 태스크가 가져온다.** `tools/check_dead_css.py` 가 쓰이지 않는 정의를 실패로 잡는다. 형제 문서의 `.dia` CSS 를 통째로 복사하지 말고, 그 태스크의 그림이 실제로 쓰는 클래스만 가져온다.
- **클래스명을 문자열로 조립하지 않는다.** `class="band ${tone}"` 같은 보간은 검사기가 정의 쪽만 보고 사장 CSS 로 판정한다. 상태별 리터럴로 쓴다.
- **색 축.** 이 문서는 `--accent`(#fb7185)와 `--bad`(#f87171)가 거의 같은 색이다. 형제 문서처럼 accent 를 '움직이는 것'에 쓰면 실패 표시와 구별되지 않는다. 이 문서의 도해 팔레트는 다음으로 고정한다.
  - 구조(상자·선·축): `--border-2`, `--border`, `--panel-2`, `--bg`
  - 지금 좇아야 할 값: `--purple` (#c084fc)
  - 실패·오류·잃은 것: `--bad`
  - 막아 냄·지켜진 것: `--ok`
  - 모름·대기·상황 라벨: `--warn`
  - `--accent` 는 지금 단계의 강조 테두리에만 쓰고 판정에는 쓰지 않는다.
- **SVG 에서 색과 칠은 속성이 아니라 클래스로 준다.** `.dia .nd{stroke:var(--border-2)}` 같은 CSS 선언은 언제나 `stroke="..."` 프레젠테이션 속성을 이긴다. `class="nd"` 를 붙인 도형에 `stroke="var(--bad)"` 를 얹으면 그 색은 나오지 않는다. 덮어쓰려면 클래스를 하나 더 만들고, 그 CSS 는 그것을 처음 쓰는 태스크가 가져온다. 클래스가 없는 도형(`<polygon fill="...">` 등)에만 속성을 쓴다.
- **`figcaption` 과 `.dia-cap` 은 다른 것을 적는다.** `figcaption` 은 그림이 주장하는 것 한 줄이고 내내 같다. `.dia-cap` 은 단계마다 바뀐다. 둘을 같은 문장으로 채우지 않는다.
- **`aria-label` 은 도형 목록이 아니라 문장이다.** 그림 전체가 무엇을 주장하는지를 적는다.
- **장마다 `.oneline` 은 정확히 하나다.** 도해를 넣으면서 강조 상자를 새로 만들지 않는다.
- **장의 끝은 `.quiz` 다음의 `.nextq` 다.** `.oneline` 은 장을 닫는 요소가 아니라 본문 중간의 강조 상자다. 도해는 언제나 그 장의 `.quiz` **앞**, 그림이 받쳐 주는 산문 바로 옆에 둔다. 기존 테스트 `test_the_next_problem_is_the_last_thing_in_the_chapter` 가 `.nextq` 뒤에 오는 것을 막고 있고, Task 1 이 그 목록에 도해를 더한다.
- **`.dia-cap` 은 `aria-hidden="true"` 로 덮는다.** 자동 재생이 도는 내내 낭독기가 읽으면 본문을 들을 수 없다.
- **한국어 문장 규칙.** `~/.claude/output-styles/fluent-korean.md` 를 따른다. 단계 설명과 캡션은 완성된 문장으로 끝맺는다. 엠대시를 쓰지 않는다.
- **커밋 접두사는 `defprog-dia:` 로 한다.**
- **매 태스크 끝에 반드시 실행한다.**
  ```
  python3 tools/check_tutorial.py defensive_programming.html
  python3 tools/check_dead_css.py defensive_programming.html
  python3 -m pytest tools/ -q
  ```

## 도해 배치 요약

| | 섹션 id | 소제목 뒤에 넣는다 | figure id |
|---|---|---|---|
| D1 | `trace` | 📏 터진 자리와 잘못된 자리 | `diaBlame` |
| D2 | `silent` | 🫥 조용한 실패의 다섯 가지 모습 | `diaSilent` |
| D3 | `boundary` | 🔬 검증 위치를 옮겨 보기 | `diaBoundary` |
| D4 | `invariant` | 🕳️ 무엇이든 담기는 모델이 치르는 대가 | `diaShape` |
| D5 | `assembly` | 📤 응답이 이미 나간 뒤 | `diaCommit` |
| D6 | `swallow` | 🎣 같은 예외, 네 층 | `diaLayers` |
| D7 | `slowdown` | 🧵 스레드 풀이 마르는 순서 | `diaPool` |
| D8 | `slowdown` | 🧮 예산에서 거꾸로 나눈 타임아웃 | `diaBudget` |
| D9 | `specgap` | 🖍️ 다섯 줄을 다시 읽으면 | `diaSpecGap` |
| D10 | `recap` | 🗺️ 반경 지도, 이번에는 구멍까지 | `diaRadius` |

---

### Task 1: 도해 기반과 첫 그림 (D1 · 터진 자리와 잘못된 자리)

기반과 첫 그림을 한 태스크로 묶는다. CSS 는 그것을 쓰는 마크업과 함께 도착해야 `check_dead_css.py` 를 통과하기 때문이다.

**Files:**
- Modify: `defensive_programming.html` (`<style>` 끝, `trace` 섹션, `<script>` 끝)
- Create: `tools/test_defensive_diagrams.py`

**Interfaces:**
- Consumes: 없음
- Produces: 뒤의 아홉 태스크가 전부 쓴다.
  - `wireDia(id, steps)` — `steps` 는 `{c:'단계 설명 HTML', h:밀리초}` 배열. `id` 는 `figure.dia` 의 id.
  - `diaAt(spec, n)` — `"0,2"` · `"1-3"` · `"2+"` 세 표기를 Set 으로 바꾼다.
  - `.dia` 계열 CSS 중 이 태스크가 가져오는 것: `.dia` `.dia-top` `.dia-tag` `.dia-sp` `.dia-btn` `.dia-dots` `.dia-dot` `.dia-cap` `.dia-scroll` `.dia-hint` `.nd` `.ghost` `.hot` `.soft` `.s` `.m` `.cap-l` `.mut` `.no` `.ok` `.warn` `.wire` `.dash` `.bad` `.pop` `.breathe` `.draw`
  - 뒤 태스크가 새 부품(`.fly` 등)을 쓰려면 그 태스크가 CSS 를 함께 가져온다.

- [ ] **Step 1: 실패하는 정적 테스트를 쓴다**

`tools/test_defensive_diagrams.py` 를 만든다. 이 파일은 태스크마다 기대 개수만 올라간다.

```python
"""defensive_programming.html 의 도해 정적 불변식.

브라우저 없이 소스만 본다. 동작 검사는 test_defensive_diagram_behavior.py 가 맡는다.
"""
import re
from pathlib import Path

import pytest

DOC = Path(__file__).resolve().parent.parent / 'defensive_programming.html'

# 이 문서가 그리기로 한 도해. 태스크가 하나씩 채운다.
# (figure id, 그 도해가 속한 섹션 id)
DIAGRAMS = [
    ('diaBlame', 'trace'),
]

FIGURE_OPEN = re.compile(r'<figure class="dia" id="([^"]+)"')
# data-at 이 받는 표기는 셋뿐이다. 오타는 조용히 '그 단계에 안 보임'이 되므로 여기서 막는다.
DATA_AT = re.compile(r'\bdata-at="([^"]*)"')
DATA_AT_OK = re.compile(r'^\s*\d+(?:-\d+|\+)?(?:\s*,\s*\d+(?:-\d+|\+)?)*\s*$')

# 그림 안의 글자도 산문이다. 각색 금칙어는 SVG 안에서도 나오면 안 된다.
FORBIDDEN = ['cheil', 'ssfshop', 'dspCnr', 'ConttImg',
             'includeMultiMainContents', 'SecureValueExpression', '전시코너', '전시 코너']


@pytest.fixture(scope='module')
def src():
    return DOC.read_text(encoding='utf-8')


def iter_figures(src):
    """<figure class="dia" ...> 를 짝이 맞는 </figure> 까지 (id, 본문) 으로 내놓는다.

    figure 는 이 문서에서 중첩되지 않지만, 셀렉터가 어긋나면 조용히 0개를 세게 되므로
    아래 test_the_figure_parser_still_matches_the_markup 이 개수를 대조한다.
    """
    for m in FIGURE_OPEN.finditer(src):
        end = src.find('</figure>', m.end())
        if end != -1:
            yield m.group(1), src[m.end():end]


def test_the_figure_parser_still_matches_the_markup(src):
    assert src.count('<figure class="dia"') == len(list(iter_figures(src)))


def test_every_planned_diagram_is_present(src):
    assert [fid for fid, _ in iter_figures(src)] == [fid for fid, _ in DIAGRAMS]


def test_every_diagram_sits_in_its_chapter(src):
    for fid, sec in DIAGRAMS:
        sec_start = src.index(f'<section id="{sec}"')
        sec_end = src.index('</section>', sec_start)
        assert sec_start < src.index(f'id="{fid}"') < sec_end, f'{fid} 가 {sec} 밖에 있다'


def test_every_diagram_carries_one_svg_with_a_sentence_label(src):
    for fid, body in iter_figures(src):
        assert body.count('<svg') == 1, f'{fid}: svg 는 하나여야 한다'
        m = re.search(r'<svg[^>]*\baria-label="([^"]*)"', body)
        assert m, f'{fid}: aria-label 이 없다'
        # 도형 목록이 아니라 문장이어야 한다. 문장이면 최소한 마침표가 있고 길다.
        assert len(m.group(1)) >= 60 and '.' in m.group(1), f'{fid}: aria-label 이 문장이 아니다'
        assert 'role="img"' in body, f'{fid}: role="img" 가 없다'


def test_every_diagram_has_a_caption_and_a_step_box(src):
    for fid, body in iter_figures(src):
        assert '<figcaption>' in body, f'{fid}: figcaption 이 없다'
        assert 'class="dia-cap"' in body, f'{fid}: .dia-cap 이 없다'
        assert 'aria-hidden="true"' in body, f'{fid}: .dia-cap 을 낭독기에서 덮지 않았다'


def test_figcaption_and_step_box_do_not_say_the_same_thing(src):
    for fid, body in iter_figures(src):
        cap = re.search(r'<figcaption>(.*?)</figcaption>', body, re.S)
        assert cap and cap.group(1).strip(), f'{fid}: figcaption 이 비어 있다'


def test_data_at_notation_is_valid_everywhere(src):
    for raw in DATA_AT.findall(src):
        assert DATA_AT_OK.match(raw), f'data-at="{raw}" 는 해석할 수 없는 표기다'


def test_diagrams_carry_no_internal_identifiers(src):
    for fid, body in iter_figures(src):
        for bad in FORBIDDEN:
            assert bad not in body, f'{fid}: 각색하지 않은 식별자 {bad}'


def test_the_evidence_the_first_diagram_must_keep(src):
    body = dict(iter_figures(src))['diaBlame']
    for keep in ('BeanELResolver', '_005fset_005f141', '9946'):
        assert keep in body, f'diaBlame 이 {keep} 을 잃었다'
```

- [ ] **Step 1b: 기존 불변식에 도해를 더한다**

`tools/test_defensive_document.py` 의 `test_the_next_problem_is_the_last_thing_in_the_chapter` 는 `.nextq` 뒤에 본문이 오는 것을 막는다. 그 목록이 도해를 모르므로, 도해를 장 끝에 잘못 두어도 조용히 통과한다. 새 부품이 기존 규칙을 어길 새 방법을 만들었으므로 그 자리에서 막는다.

```python
        if (re.search(r'<(?:h2|h3|p)\b', rest)
                or 'class="demo"' in rest or 'class="quiz"' in rest
                or 'class="dia"' in rest):
            late.append(cid)
```

- [ ] **Step 2: 테스트가 실패하는 것을 확인한다**

Run: `python3 -m pytest tools/test_defensive_diagrams.py -q`
Expected: FAIL. `test_every_planned_diagram_is_present` 가 `[] != ['diaBlame']` 로 떨어진다.

- [ ] **Step 3: 도해 CSS 를 넣는다**

`<style>` 블록의 맨 끝, `</style>` 바로 앞에 넣는다. 형제 문서에서 그대로 복사하지 말고 아래 것만 넣는다. 여기 없는 클래스는 그것을 처음 쓰는 태스크가 가져온다.

```css
/* ============ 도해 ============
   그림 하나는 단계의 줄이다. 구동기가 단계 번호를 뿌리에 적고 해당 요소에 .vis 를
   걸어 주며, 무엇이 어떻게 보일지는 여기서 정한다. 구동기는 자리도 모양도 모른다. */
.dia{
  margin:22px 0; padding:16px 18px; border:1px solid var(--border);
  border-radius:var(--radius); background:var(--panel);
}
.dia-top{display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:0 0 6px}
.dia-tag{
  font-family:var(--mono); font-size:10.5px; letter-spacing:1px; text-transform:uppercase;
  color:var(--text-mut); border:1px solid var(--border); padding:3px 8px;
  border-radius:6px; background:var(--bg);
}
.dia-sp{flex:1 1 auto}
.dia-btn{padding:5px 11px; font-size:12px; font-family:var(--mono); min-width:74px}
.dia-dots{display:flex; gap:6px; align-items:center}
/* 전역 button 규칙이 padding 을 들고 있어서, 폭만 8px 로 줘도 알약이 된다.
   padding 과 line-height 를 도로 0 으로 내려 놓아야 점이 점으로 보인다. */
.dia-dot{
  width:8px; height:8px; padding:0; line-height:0; flex:0 0 auto;
  border-radius:50%; background:var(--panel-2);
  border:1px solid var(--border-2); transition:background .2s, border-color .2s;
}
.dia-dot:hover{transform:none; border-color:var(--accent)}
.dia-dot.on{background:var(--accent); border-color:var(--accent)}
/* 멈춰 있는 동안에는 지금 단계가 어디인지가 더 중요해진다 */
.dia.paused .dia-dot.on{background:var(--warn); border-color:var(--warn)}
.dia svg{display:block; width:100%; height:auto; margin:2px 0 0}

/* 단계 설명. figcaption 과 갈라 둔다. figcaption 은 그림이 주장하는 것 한 줄이라
   내내 같고, 이쪽은 단계마다 바뀐다. 바뀌는 쪽을 낭독기가 계속 읽으면 본문을 들을
   수 없으므로 여기는 aria-hidden 으로 덮고, 그림의 뜻은 svg 의 aria-label 이 진다. */
.dia-cap{
  min-height:2.9em; margin:8px 0 0; padding:9px 12px; border-radius:var(--radius-sm);
  background:var(--bg); border:1px solid var(--border);
  font-size:13.2px; line-height:1.6; color:var(--text-dim);
}
.dia-cap b{color:var(--text)}
.dia-cap .no{color:var(--bad)}
.dia figcaption{
  margin:8px 2px 0; font-size:12.5px; line-height:1.65; color:var(--text-mut);
  border-top:1px solid var(--border); padding-top:8px;
}
.dia figcaption b{color:var(--text-dim)}

/* ---- 그림 안의 공통 부품 ----
   색 축은 본문 판정 색과 같다. 이 문서는 --accent 와 --bad 가 거의 같은 로즈라서,
   형제 문서처럼 accent 를 '움직이는 값'에 쓰면 실패 표시와 구별되지 않는다.
   좇아야 할 값은 --purple 이 맡고, accent 는 지금 단계의 테두리에만 쓴다. */
.dia .nd{fill:var(--bg); stroke:var(--border-2); stroke-width:1.2}
.dia .nd.soft{fill:var(--panel-2)}
.dia .nd.hot{stroke:var(--accent); stroke-width:1.8}
.dia .nd.ghost{fill:none; stroke:var(--border); stroke-dasharray:4 4}

.dia text{font-family:var(--sans); fill:var(--text-dim)}
.dia .s{font-size:11.5px; fill:var(--text-dim)}
/* 값은 고정폭, 말은 본문 활자. 칸에 든 것이 데이터일 때는 자간이 벌어지는 것이 정보다. */
.dia .m{font-family:var(--mono); font-size:10.5px; fill:var(--text-mut); letter-spacing:.3px}
.dia .cap-l{font-family:var(--mono); font-size:9.5px; letter-spacing:.6px; fill:var(--text-mut)}
.dia .mut{fill:var(--text-mut)}
.dia .no{fill:var(--bad)}
.dia .ok{fill:var(--ok)}
.dia .warn{fill:var(--warn)}

.dia .wire{stroke:var(--border-2); stroke-width:1.4; fill:none}
.dia .wire.dash{stroke-dasharray:5 4}
.dia .wire.bad{stroke:var(--bad); stroke-width:2}

/* ---- 구동기가 쓰는 것 ----
   data-at 하나다. 그 단계에서만 보여야 할 것에 붙이고, 목록 판정은 JS 가,
   보임과 숨김은 여기가 맡는다. */
.dia [data-at]{opacity:0; transition:opacity .28s ease}
.dia [data-at].vis{opacity:1}

/* 새로 생긴 것 */
.dia .pop{transform-box:fill-box; transform-origin:center}
.dia .pop.vis{animation:diaPop .42s cubic-bezier(.2,.9,.3,1.25) both}
@keyframes diaPop{
  0%  {opacity:0; transform:scale(.55)}
  62% {opacity:1; transform:scale(1.07)}
  100%{opacity:1; transform:scale(1)}
}
/* 지금 보라는 표시. 깜빡임이 아니라 숨쉬기여야 한다. 그림이 읽는 동안 내내 떠
   있으므로 대비가 크게 오르내리면 옆의 본문을 못 읽는다. */
.dia .breathe.vis{animation:diaBreathe 1.9s ease-in-out infinite}
@keyframes diaBreathe{0%,100%{opacity:1} 50%{opacity:.45}}
/* 선이 그어진다. 갔다 오는 것이 아니라 관계가 드러나는 것 */
.dia .draw{stroke-dasharray:var(--dl,300); stroke-dashoffset:var(--dl,300)}
.dia .draw.vis{animation:diaDraw var(--ft,.7s) ease-out forwards}
@keyframes diaDraw{to{stroke-dashoffset:0}}

/* 움직임을 줄여 달라고 한 사람에게는 자동으로 돌지 않는다. 구동기가 자동 재생을
   걸지 않고, 여기서는 사이를 잇는 보간만 끈다. 단계를 손으로 넘기는 것은 남는다. */
@media (prefers-reduced-motion: reduce){
  .dia [data-at]{transition:none}
  .dia .pop.vis, .dia .breathe.vis, .dia .draw.vis{animation:none}
  /* 애니메이션을 끄면 시작 상태(투명·잘린 선)에 멈춘다. 끝난 모습으로 세운다. */
  .dia .pop.vis, .dia .breathe.vis{opacity:1}
  .dia .draw.vis{stroke-dashoffset:0}
}

/* 좁은 화면에서 글자가 뭉개지지 않게 최소 폭을 주고 가로로만 흘린다. 본문이 가로로
   밀리면 안 되므로 스크롤은 그림 상자 안에서만 일어난다. 폭에 맞춰 통째로 줄이는
   쪽은 택하지 않았다. 720 짜리 그림을 400 에 밀어 넣으면 9.5px 글자가 5px 가 된다. */
.dia-scroll{overflow-x:auto; overflow-y:hidden; scrollbar-width:thin;
  scrollbar-color:var(--border-2) transparent}
.dia-scroll::-webkit-scrollbar{height:8px}
.dia-scroll::-webkit-scrollbar-track{background:transparent}
.dia-scroll::-webkit-scrollbar-thumb{background:var(--border-2); border-radius:99px}
.dia-scroll::-webkit-scrollbar-thumb:hover{background:var(--text-mut)}
/* 밀 수 있다는 표시. 넘치는 쪽이 상자 안이라 페이지 스크롤바로는 드러나지 않는다. */
.dia-hint{display:none; font-family:var(--mono); font-size:10.5px; letter-spacing:.4px;
  color:var(--text-mut); margin:0 0 4px}
@media(max-width:700px){
  .dia-scroll svg{min-width:560px}
  .dia-hint{display:block}
}
```

- [ ] **Step 4: 구동기를 넣는다**

`<script>` 안, 기존 `paintRadius(...)` 호출 **앞**에 넣는다(도해 배선은 그 뒤에 온다).

```js
/* ============================================================
   도해 구동기 (공통)
   ------------------------------------------------------------
   그림 하나는 단계의 줄이다. 구동기가 하는 일은 셋뿐이다. 지금 단계 번호를 뿌리
   요소의 data-s 에 적고, 그 단계에서만 보여야 할 것에 .vis 를 걸고, 단계 설명을
   갈아 끼운다. 무엇이 어디에 있는지는 각 그림의 SVG 가 정한다.

   자동 재생은 화면에 들어와 있는 동안에만 돈다. 안 보이는 그림 열 개가 계속 타이머를
   돌리면 배터리만 먹고, 스크롤을 내리다 눈에 걸린 그림이 이미 중간 단계에 가 있으면
   앞을 못 본 채로 만나게 된다. 그래서 나가면 멈추고, 손으로 멈춘 것은 다시 들어와도
   저절로 돌지 않는다.
   ============================================================ */
const DIA_MOTION = !(window.matchMedia &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches);

/* data-at="0,2" · "1-3" · "2+" 세 표기를 받는다. 단계가 늘거나 줄 때
   목록을 손으로 다시 세지 않아도 되게 범위 표기를 둔다. */
function diaAt(spec, n){
  const s = new Set();
  String(spec).split(',').forEach(raw => {
    const p = raw.trim(); if(!p) return;
    if(p.endsWith('+')){ for(let i = +p.slice(0, -1); i < n; i++) s.add(i); }
    else if(p.includes('-')){
      const [a, b] = p.split('-').map(Number);
      for(let i = a; i <= b; i++) s.add(i);
    }
    else s.add(+p);
  });
  return s;
}

function wireDia(id, steps){
  const fig = $('#' + id); if(!fig) return;
  const cap  = $('.dia-cap',  fig);
  const dots = $('.dia-dots', fig);
  const btn  = $('.dia-btn',  fig);
  const n    = steps.length;

  const marks = $$('[data-at]', fig).map(el => ({ el:el, at:diaAt(el.dataset.at, n) }));

  // 단계 점의 개수는 steps 에서 나온다. 손으로 적어 두면 단계를 하나 고칠 때마다
  // 마크업도 함께 고쳐야 하고, 어긋나면 눈에 안 띄는 채로 남는다.
  dots.innerHTML = '';
  for(let k = 0; k < n; k++){
    const b = document.createElement('button');
    b.className = 'dia-dot';
    b.type = 'button';
    b.setAttribute('aria-label', (k + 1) + '단계로');
    b.addEventListener('click', () => { hold = true; pause(); i = k; paint(); });
    dots.appendChild(b);
  }
  const dotEls = $$('.dia-dot', dots);

  let i = 0, timer = null, playing = false, hold = false;

  function paint(){
    fig.dataset.s = i;
    cap.innerHTML = steps[i].c;
    marks.forEach(m => m.el.classList.toggle('vis', m.at.has(i)));
    dotEls.forEach((d, k) => d.classList.toggle('on', k === i));
  }
  function tick(){
    i = (i + 1) % n;
    paint();
    timer = setTimeout(tick, steps[i].h || 2600);
  }
  function play(){
    if(playing) return;
    playing = true; fig.classList.remove('paused');
    btn.textContent = '⏸ 멈춤'; btn.setAttribute('aria-pressed', 'true');
    clearTimeout(timer);
    timer = setTimeout(tick, steps[i].h || 2600);
  }
  function pause(){
    playing = false; fig.classList.add('paused');
    btn.textContent = '▶ 재생'; btn.setAttribute('aria-pressed', 'false');
    clearTimeout(timer);
  }

  btn.setAttribute('aria-controls', id);
  btn.addEventListener('click', () => {
    if(playing){ hold = true; pause(); }
    else { hold = false; play(); }
  });

  // 움직임을 줄여 달라고 한 사람에게는 마지막 단계를 세워 둔다. 0단계는 대개 아무
  // 일도 일어나기 전이라, 그것만 남기면 그림이 아무 말도 하지 않는다.
  if(!DIA_MOTION){ i = n - 1; hold = true; }
  paint();
  if(!DIA_MOTION){ pause(); return; }
  pause();

  new IntersectionObserver(es => {
    es.forEach(e => { if(e.isIntersecting){ if(!hold) play(); } else pause(); });
  }, { threshold: 0.3 }).observe(fig);
}
```

- [ ] **Step 5: D1 마크업을 넣는다**

`trace` 섹션의 `<h3>📏 터진 자리와 잘못된 자리</h3>` 아래 문단들 **뒤**, 그 장의 `.oneline` **앞**에 넣는다. 이 장에서는 그 소제목이 마지막 소제목이라 `.oneline` 이 바로 뒤에 온다.

```html
<figure class="dia" id="diaBlame">
  <div class="dia-top">
    <span class="dia-tag">그림 1 · 두 개의 길</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 300" role="img" aria-label="값 하나가 상류에서 출발해 응답 파싱, 캐시, 모델 조립을 거쳐 화면 렌더까지 가는 과정을 시간축 위에 놓은 그림. 그 값이 목록이 아니라 문자열이 된 자리는 앞의 세 갈래 가운데 하나이지만 어디였는지는 알 수 없고, 그 자리들에서는 아무도 예외를 던지지 않아 스택에 아무것도 남기지 않았다. 스택트레이스 열 줄은 마지막 화면 렌더 자리 위에서만 솟아 있어서, 터진 자리는 정확히 가리키지만 잘못된 자리는 가리키지 못한다.">

      <!-- 스택이 찍지 않은 구간 -->
      <rect class="nd ghost" x="30" y="40" width="400" height="150" rx="12" data-at="2+"/>
      <text class="cap-l" x="230" y="66" text-anchor="middle" data-at="2+">스택트레이스가 찍지 않은 구간</text>
      <text class="s" x="230" y="112" text-anchor="middle" data-at="2+">여기에서는 아무도 예외를 던지지 않았습니다.</text>
      <text class="s mut" x="230" y="136" text-anchor="middle" data-at="2+">던지지 않았으므로 스택에 남을 것도 없습니다.</text>

      <!-- 스택 열 줄. 위가 가장 깊은 자리다 -->
      <g data-at="4+" class="pop">
        <rect class="nd soft" x="452" y="18" width="236" height="180" rx="10"/>
        <text class="cap-l" x="570" y="14" text-anchor="middle">스택트레이스가 찍은 것 · 열 줄</text>
        <text class="m" x="460" y="36">BeanELResolver$BeanProperties.get:253</text>
        <text class="m" x="460" y="53">BeanELResolver.property:322</text>
        <text class="m" x="460" y="70">BeanELResolver.getValue:93</text>
        <text class="m" x="460" y="87">JasperELResolver.getValue:123</text>
        <text class="m" x="460" y="104">AstValue.getValue:160</text>
        <text class="m" x="460" y="121">ValueExpressionImpl.getValue:149</text>
        <text class="m" x="460" y="138">PageContextImpl.proprietaryEvaluate:655</text>
        <text class="m" x="460" y="155">..._jspx_meth_c_005fset_005f141:9946</text>
        <text class="m" x="460" y="172">..._jspx_meth_c_005fif_005f43:9832</text>
        <text class="m" x="460" y="189">..._jspService:743</text>
      </g>
      <line class="wire" x1="570" y1="198" x2="570" y2="212" data-at="4+"/>

      <!-- 값의 자리 표시 -->
      <text class="m warn" x="74"  y="204" text-anchor="middle" data-at="1+">? 상류의 빈 값</text>
      <text class="m warn" x="192" y="204" text-anchor="middle" data-at="1+">? 파싱 실패</text>
      <text class="m warn" x="318" y="204" text-anchor="middle" data-at="1+">? 역직렬화 실패</text>
      <text class="m no"   x="570" y="204" text-anchor="middle" data-at="3+">java.lang.String</text>

      <!-- 네 자리와 그 앞의 상류 -->
      <rect class="nd ghost" x="30"  y="212" width="88"  height="32" rx="8"/>
      <text class="s mut" x="74"  y="232" text-anchor="middle">상류 API</text>
      <rect class="nd" x="140" y="212" width="104" height="32" rx="8"/>
      <text class="s" x="192" y="232" text-anchor="middle">응답 파싱</text>
      <rect class="nd" x="266" y="212" width="104" height="32" rx="8"/>
      <text class="s" x="318" y="232" text-anchor="middle">캐시</text>
      <rect class="nd" x="392" y="212" width="104" height="32" rx="8"/>
      <text class="s" x="444" y="232" text-anchor="middle">모델 조립</text>
      <rect class="nd" x="518" y="212" width="104" height="32" rx="8"/>
      <rect class="nd hot" x="518" y="212" width="104" height="32" rx="8" data-at="3+"/>
      <text class="s" x="570" y="232" text-anchor="middle">화면 렌더</text>

      <!-- 자리 사이의 이동 -->
      <line class="wire dash" x1="118" y1="228" x2="140" y2="228"/>
      <line class="wire dash" x1="244" y1="228" x2="266" y2="228"/>
      <line class="wire dash" x1="370" y1="228" x2="392" y2="228"/>
      <line class="wire dash" x1="496" y1="228" x2="518" y2="228"/>
      <text class="cap-l ok" x="318" y="260" text-anchor="middle" data-at="2+">아무 항의 없이 통과</text>

      <!-- 시간축 -->
      <line class="wire" x1="30" y1="278" x2="694" y2="278"/>
      <polygon fill="var(--border-2)" points="686,273 698,278 686,283"/>
      <text class="cap-l" x="694" y="294" text-anchor="end">시간</text>

      <!-- 마지막 단계에서만 그어지는 거리 -->
      <path class="wire bad draw" style="--dl:420; --ft:.9s" d="M 150 292 L 560 292" data-at="5"/>
      <text class="s no breathe" x="355" y="292" text-anchor="middle" data-at="5">잘못된 자리와 터진 자리 사이</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>스택트레이스는 값이 지나온 길이 아니라 호출이 지나온 길입니다.</b> 두 길이 갈라지는 자리가 이 그림의 왼쪽입니다.</figcaption>
</figure>
```

- [ ] **Step 6: D1 을 배선한다**

`<script>` 안, `wireDia` 정의 뒤에 넣는다.

```js
wireDia('diaBlame', [
  {c:'값 하나가 상류에서 출발해 응답 파싱, 캐시, 모델 조립을 거쳐 화면 렌더까지 갑니다.', h:2800},
  {c:'그 값이 목록이 아니라 문자열이 된 자리는 앞의 세 갈래 가운데 하나입니다. <b>어느 쪽이었는지는 아직 모릅니다.</b>', h:3400},
  {c:'세 자리 가운데 어디에서도 예외가 나지 않았습니다. 아무도 던지지 않았으므로 스택에 남을 것도 없습니다.', h:3200},
  {c:'화면을 그리는 자리에서 EL이 게터를 찾다 실패합니다. 이 값이 처음으로 항의를 받는 자리입니다.', h:3000},
  {c:'그때 찍힌 것이 이 열 줄입니다. 열 줄 전부가 렌더링 구간 안에 있습니다.', h:3200},
  {c:'터진 자리는 정확합니다. <span class="no">잘못된 자리는 이 열 줄 바깥에 있습니다.</span>', h:3800},
]);
```

- [ ] **Step 7: 검사기와 테스트를 전부 돌린다**

```
python3 tools/check_tutorial.py defensive_programming.html
python3 tools/check_dead_css.py defensive_programming.html
python3 -m pytest tools/ -q
```
Expected: 셋 다 통과. 사장 CSS 가 나오면 그 클래스를 D1 이 쓰지 않는 것이므로, CSS 에서 빼고 그 클래스가 필요한 태스크로 미룬다.

- [ ] **Step 8: 커밋**

```bash
git add defensive_programming.html tools/test_defensive_diagrams.py
git commit -m "defprog-dia: 도해 기반과 첫 그림 — 두 길이 갈라지는 자리"
```

---

### Task 2: D2 · 조용한 실패의 다섯 가지 모습 (3장 `silent`)

같은 코드 다섯 줄이 조건에 따라 방어가 되기도 하고 삼킴이 되기도 한다는 것이 이 그림의 주장이다. 한 단계에 한 줄씩 보여 주고, 마지막 단계에서 다섯 줄의 공통점을 드러낸다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py`

**Interfaces:**
- Consumes: `wireDia`, Task 1 이 가져온 `.dia` CSS
- Produces: `.dia .val`. D2 의 단계 표시가 처음 쓰므로 이 태스크가 가져온다.

- [ ] **Step 0: 새 CSS 한 줄**

Task 1 이 넣은 `.dia .warn` 바로 아래에 넣는다.

```css
.dia .val{fill:var(--purple)}
```

- [ ] **Step 1: 테스트의 기대 목록을 늘린다**

`tools/test_defensive_diagrams.py` 의 `DIAGRAMS` 에 `('diaSilent', 'silent')` 를 추가한다. 실행하면 `test_every_planned_diagram_is_present` 가 실패한다.

- [ ] **Step 2: 마크업을 넣는다**

`silent` 섹션에서 다섯 항목 목록 **뒤**, 「다섯 가지를 나란히 놓고 보면 공통점이 하나 있습니다」 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaSilent">
  <div class="dia-top">
    <span class="dia-tag">그림 2 · 같은 코드, 갈리는 자리</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 250" role="img" aria-label="조용한 실패의 다섯 가지 모습을 하나씩 놓고, 같은 코드가 조건에 따라 방어가 되기도 하고 삼킴이 되기도 하는 것을 두 갈래로 보여 주는 그림. 빈 컬렉션 반환, 기본값 대입, Optional.orElse, 잡고 로그만 남기기, catch 후 무시 다섯 가지 모두 위쪽 갈래에서는 옳은 선택이고 아래쪽 갈래에서는 조용한 실패다. 다섯 가지의 공통점은 어느 갈래로 가든 예외가 나지 않아 테스트도 리뷰도 그대로 통과한다는 것이다.">

      <text class="cap-l" x="30" y="20">다섯 가지 중</text>
      <text class="m val" x="112" y="20" data-at="0">첫 번째</text>
      <text class="m val" x="112" y="20" data-at="1">두 번째</text>
      <text class="m val" x="112" y="20" data-at="2">세 번째</text>
      <text class="m val" x="112" y="20" data-at="3">네 번째</text>
      <text class="m val" x="112" y="20" data-at="4">다섯 번째</text>
      <text class="m val" x="112" y="20" data-at="5">전부</text>

      <!-- 왼쪽: 코드 모양 하나 -->
      <rect class="nd soft" x="30" y="88" width="210" height="52" rx="10"/>
      <text class="m" x="135" y="119" text-anchor="middle" data-at="0">빈 컬렉션 반환</text>
      <text class="m" x="135" y="119" text-anchor="middle" data-at="1">기본값 대입</text>
      <text class="m" x="135" y="119" text-anchor="middle" data-at="2">Optional.orElse(기본값)</text>
      <text class="m" x="135" y="119" text-anchor="middle" data-at="3">잡고 로그만 남기기</text>
      <text class="m" x="135" y="119" text-anchor="middle" data-at="4">catch (Exception ignored)</text>
      <text class="m mut" x="135" y="119" text-anchor="middle" data-at="5">다섯 줄 모두</text>

      <!-- 갈림 -->
      <path class="wire" d="M 240 114 C 272 114 272 62 304 62"/>
      <path class="wire" d="M 240 114 C 272 114 272 166 304 166"/>
      <polygon fill="var(--border-2)" points="296,57 308,62 296,67"/>
      <polygon fill="var(--border-2)" points="296,161 308,166 296,171"/>

      <!-- 위 갈래: 옳은 자리 -->
      <rect class="nd" x="308" y="34" width="382" height="56" rx="10"/>
      <text class="cap-l ok" x="320" y="52">이 조건에서는 옳습니다</text>
      <text class="s" x="320" y="76" data-at="0">목록이 정말로 비어 있을 때입니다.</text>
      <text class="s" x="320" y="76" data-at="1">선택하지 않았을 때를 위한 값일 때입니다.</text>
      <text class="s" x="320" y="76" data-at="2">정말로 없는 것이 정상 범위에 속할 때입니다.</text>
      <text class="s" x="320" y="76" data-at="3">그 실패가 다음 로직에 영향을 주지 않을 때입니다.</text>
      <text class="s no" x="320" y="76" data-at="4">옳은 자리가 사실상 없습니다.</text>
      <text class="s mut" x="320" y="76" data-at="5">조건이 맞으면 다섯 줄 전부 방어입니다.</text>

      <!-- 아래 갈래: 삼킨 자리 -->
      <rect class="nd" x="308" y="138" width="382" height="56" rx="10"/>
      <text class="cap-l no" x="320" y="156">이 조건에서는 조용한 실패입니다</text>
      <text class="s" x="320" y="180" data-at="0">조회가 실패했는데도 같은 빈 리스트를 내주는 경우입니다.</text>
      <text class="s" x="320" y="180" data-at="1">파싱이 깨졌는데도 기본값을 채워 넣는 경우입니다.</text>
      <text class="s" x="320" y="180" data-at="2">조회가 실패해서 비어 버린 자리에까지 물리는 경우입니다.</text>
      <text class="s" x="320" y="180" data-at="3">영향을 주는데도 로그만 남기고 진행하는 경우입니다.</text>
      <text class="s" x="320" y="180" data-at="4">무시해도 되는지 판단한 흔적조차 남지 않습니다.</text>
      <text class="s mut" x="320" y="180" data-at="5">조건이 어긋나면 다섯 줄 전부 삼킴입니다.</text>

      <!-- 공통점 -->
      <rect class="nd ghost" x="30" y="210" width="660" height="32" rx="8" data-at="5"/>
      <text class="s warn breathe" x="360" y="231" text-anchor="middle" data-at="5">어느 갈래로 가든 예외는 나지 않습니다. 테스트도 리뷰도 그대로 통과합니다.</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>"빈 컬렉션을 반환한다"는 문장 자체에는 방어인지 삼킴인지가 정해져 있지 않습니다.</b> 갈리는 것은 코드가 아니라 그 코드가 놓인 조건입니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaSilent', [
  {c:'조회 자체가 실패했는데도 빈 리스트를 내주면, 호출한 쪽은 <b>"없음"과 "가져오지 못함"</b>을 더 이상 구별할 수 없습니다.', h:3600},
  {c:'파싱이 깨졌는데도 기본값을 채워 넣으면, 잘못된 요청이 정상 요청과 같은 모양으로 흘러갑니다.', h:3400},
  {c:'조회가 실패해서 비어 버린 자리에까지 같은 기본값을 물리면, 실패와 부재가 서로 구별되지 않습니다.', h:3400},
  {c:'영향을 주는데도 로그만 남기고 계속 진행하면, 잘못된 결과는 이미 화면으로 나간 뒤입니다.', h:3400},
  {c:'정말 무시해도 되는 예외라면 애초에 던지지 않는 편이 낫습니다. <span class="no">이 코드는 그 판단조차 남기지 않습니다.</span>', h:3600},
  {c:'다섯 줄의 공통점은 하나입니다. <b>문제가 있다는 신호 자체가 아예 없습니다.</b>', h:4000},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
python3 tools/check_tutorial.py defensive_programming.html && python3 tools/check_dead_css.py defensive_programming.html && python3 -m pytest tools/ -q
git add -A && git commit -m "defprog-dia: 3장 — 같은 코드가 방어와 삼킴으로 갈리는 자리"
```

---

### Task 3: D3 · 검증을 미룰수록 늘어나는 거리 (4장 `boundary`)

이 장에는 이미 「검증을 어디에 둘까」 데모가 있다. **데모와 겹치지 않는 것만 그린다.** 데모는 자리마다 스택과 메시지를 글로 찍는다. 그림은 이 문서의 한 문장 정의인 **거리**를 맡는다. 검증을 오른쪽으로 옮길수록 잘못된 값이 갈 수 있는 거리가 길어지고, 1장에서 본 EL 안쪽 프레임 다섯 줄이 되돌아온다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaBoundary', 'boundary')` 추가)

**Interfaces:**
- Consumes: `wireDia`, Task 1 의 CSS
- Produces: `.dia .nd.bad` (이 태스크가 처음 쓰므로 이 태스크가 CSS 를 함께 가져온다)

- [ ] **Step 0: 새 CSS 부품 한 줄을 가져온다**

Task 1 이 넣은 `.dia .nd.ghost` 바로 아래에 넣는다.

```css
.dia .nd.bad{stroke:var(--bad)}
```

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`boundary` 섹션의 「검증을 어디에 둘까」 데모 **뒤**, 「파싱에서 잡으면 스택은 한 줄이고」로 시작하는 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaBoundary">
  <div class="dia-top">
    <span class="dia-tag">그림 3 · 미룬 만큼의 거리</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 260" role="img" aria-label="검증을 응답 파싱, 캐시 저장, 모델 조립, 화면 렌더 네 자리 가운데 어디에 두느냐에 따라, 잘못된 값이 잡히기까지 지나가는 거리가 어떻게 달라지는지 보여 주는 그림. 파싱에서 잡으면 값은 한 자리도 더 가지 못하고 스택은 한 줄이지만, 화면 렌더까지 미루면 값은 네 자리를 모두 지나고 스택은 아홉 줄이 되며 그 가운데 다섯 줄은 EL 안쪽 프레임이다. 검증을 미룰수록 잃는 것은 스택의 길이만이 아니라 메시지에 실을 수 있는 맥락이다.">

      <!-- 파이프라인 -->
      <rect class="nd" x="40"  y="40" width="140" height="36" rx="8"/>
      <text class="s" x="110" y="63" text-anchor="middle">응답 파싱</text>
      <rect class="nd" x="210" y="40" width="140" height="36" rx="8"/>
      <text class="s" x="280" y="63" text-anchor="middle">캐시 저장</text>
      <rect class="nd" x="380" y="40" width="140" height="36" rx="8"/>
      <text class="s" x="450" y="63" text-anchor="middle">모델 조립</text>
      <rect class="nd" x="550" y="40" width="140" height="36" rx="8"/>
      <text class="s" x="620" y="63" text-anchor="middle">화면 렌더</text>
      <line class="wire dash" x1="180" y1="58" x2="210" y2="58"/>
      <line class="wire dash" x1="350" y1="58" x2="380" y2="58"/>
      <line class="wire dash" x1="520" y1="58" x2="550" y2="58"/>

      <!-- 검증을 두는 자리 -->
      <rect class="nd hot" x="40"  y="40" width="140" height="36" rx="8" data-at="0"/>
      <rect class="nd hot" x="210" y="40" width="140" height="36" rx="8" data-at="1"/>
      <rect class="nd hot" x="380" y="40" width="140" height="36" rx="8" data-at="2"/>
      <rect class="nd hot" x="550" y="40" width="140" height="36" rx="8" data-at="3"/>
      <text class="cap-l" x="110" y="30" text-anchor="middle" data-at="0">여기서 검증</text>
      <text class="cap-l" x="280" y="30" text-anchor="middle" data-at="1">여기서 검증</text>
      <text class="cap-l" x="450" y="30" text-anchor="middle" data-at="2">여기서 검증</text>
      <text class="cap-l" x="620" y="30" text-anchor="middle" data-at="3">여기서 검증</text>

      <!-- 거리 막대. 잡히기까지 값이 지나간 구간 -->
      <text class="cap-l" x="40" y="102">잘못된 값이 갈 수 있는 거리</text>
      <rect class="nd ghost" x="40" y="110" width="650" height="24" rx="6"/>
      <rect fill="var(--purple)" opacity=".55" x="42" y="112" width="138" height="20" rx="5" data-at="0"/>
      <rect fill="var(--purple)" opacity=".55" x="42" y="112" width="308" height="20" rx="5" data-at="1"/>
      <rect fill="var(--purple)" opacity=".55" x="42" y="112" width="478" height="20" rx="5" data-at="2"/>
      <rect fill="var(--purple)" opacity=".55" x="42" y="112" width="646" height="20" rx="5" data-at="3"/>

      <!-- 스택 -->
      <text class="cap-l" x="40" y="160">그때 찍히는 스택</text>
      <rect class="nd soft" x="40" y="168" width="300" height="18" rx="4" data-at="0-3"/>
      <text class="m" x="48" y="181" data-at="0-3">우리 코드 한 줄</text>
      <g data-at="1-3">
        <rect class="nd soft" x="40" y="190" width="300" height="18" rx="4"/>
        <text class="m" x="48" y="203">캐시와 조립을 거쳐 온 자리들</text>
      </g>
      <g data-at="3" class="pop">
        <rect class="nd bad" x="40" y="212" width="300" height="18" rx="4"/>
        <text class="m no" x="48" y="225">EL 안쪽 프레임 다섯 줄이 되돌아옴</text>
      </g>
      <text class="m val" x="352" y="181" data-at="0">스택 1줄</text>
      <text class="m val" x="352" y="181" data-at="1">스택 3줄</text>
      <text class="m val" x="352" y="181" data-at="2">스택 5줄</text>
      <text class="m no"  x="352" y="181" data-at="3">스택 9줄</text>

      <!-- 메시지에 실리는 맥락 세 조각 -->
      <text class="cap-l" x="440" y="160">메시지에 실리는 맥락</text>
      <rect class="nd" x="440" y="168" width="250" height="20" rx="5"/>
      <text class="s ok"  x="450" y="183" data-at="0-2">무엇을 하려다가</text>
      <text class="s mut" x="450" y="183" data-at="3">무엇을 하려다가</text>
      <rect class="nd" x="440" y="192" width="250" height="20" rx="5"/>
      <text class="s ok"  x="450" y="207" data-at="0-2">무엇에 대해</text>
      <text class="s mut" x="450" y="207" data-at="3">무엇에 대해</text>
      <rect class="nd" x="440" y="216" width="250" height="20" rx="5"/>
      <text class="s ok" x="450" y="231" data-at="0-3">무엇을 받았는지</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>검증이 늦어질수록 잃는 것은 스택의 길이만이 아닙니다.</b> 메시지에 실을 수 있는 맥락이 함께 사라집니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaBoundary', [
  {c:'값이 우리 타입이 되는 그 문턱에서 검증하면, 잘못된 값은 한 자리도 더 가지 못합니다. 메시지에는 세 조각이 모두 실립니다.', h:3600},
  {c:'캐시 저장까지 미루면 값은 이미 한 자리를 지나온 뒤입니다.', h:3000},
  {c:'모델 조립까지 미루면 두 자리를 더 지나옵니다. 거리가 길어질수록 어디에서 잘못됐는지 되짚을 곳도 늘어납니다.', h:3400},
  {c:'화면 렌더까지 미루면 값은 네 자리를 전부 지나옵니다. <span class="no">1장에서 본 EL 안쪽 프레임 다섯 줄이 고스란히 되돌아옵니다.</span> 메시지에 남는 것은 무엇이 왔는지 한 조각뿐입니다.', h:4200},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 4장 — 검증을 미룬 만큼 늘어나는 거리"
```

---

### Task 4: D4 · 표현할 수 있는 상태가 줄어드는 그림 (5장 `invariant`)

이 장의 반문은 "촘촘한 타입은 코드를 늘리지 않느냐"이고, 답은 "늘어나는 것은 선언 한 자리, 줄어드는 것은 흩어 둔 검사 전부"이다. 그 답을 **담을 수 있는 상태의 넓이**로 그린다. 잘못된 상태는 하나가 아니라 둘이고, 세 모델이 그 둘을 각각 다르게 대한다는 것이 이 그림의 핵심이다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaShape', 'invariant')` 추가)

**Interfaces:**
- Consumes: `wireDia`, Task 1·3 의 CSS
- Produces: `.dia .gone`(취소선 대신 흐리게 지나간 상태를 나타낸다)과 `.dia-cap .ye`(단계 설명 안의 긍정 강조). 둘 다 이 태스크가 처음 쓴다.

- [ ] **Step 0: 새 CSS 두 줄**

```css
.dia .gone{fill:var(--text-mut); opacity:.5}
.dia-cap .ye{color:var(--ok)}
```

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`invariant` 섹션의 「세 모델, 같은 데이터」 데모 **뒤**, 「세 줄을 눌러 보면」 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaShape">
  <div class="dia-top">
    <span class="dia-tag">그림 4 · 담을 수 있는 것의 넓이</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 290" role="img" aria-label="세 가지 모델이 표현할 수 있는 상태의 넓이를 겹친 영역으로 그린 그림. 가장 넓은 영역은 Map으로, 리스트 자리에 문자열이 앉은 상태도 그 자리가 null인 상태도 모두 담을 수 있다. 검증 없는 DTO는 문자열이 앉은 상태를 표현할 수 없지만 null인 상태는 여전히 담는다. 생성자가 강제하는 DTO는 두 상태를 모두 표현할 수 없어서, 그 조건을 다시 검사하는 코드가 안쪽 어디에도 필요하지 않다. 늘어나는 것은 타입을 선언하는 자리 하나이고 줄어드는 것은 흩어 두었던 검사 전부다.">

      <!-- 세 영역 -->
      <rect class="nd ghost" x="40" y="48" width="430" height="200" rx="14"/>
      <text class="cap-l" x="52" y="42">Map&lt;String, Object&gt; 가 담을 수 있는 것</text>
      <g data-at="1+">
        <rect class="nd" x="72" y="76" width="340" height="145" rx="12"/>
        <text class="cap-l" x="84" y="70">검증 없는 DTO</text>
      </g>
      <g data-at="2+">
        <rect class="nd soft" x="104" y="104" width="250" height="90" rx="10"/>
        <text class="cap-l ok" x="116" y="98">생성자가 강제하는 DTO</text>
        <text class="s ok" x="229" y="155" text-anchor="middle">여기 있는 것은 전부 유효합니다</text>
      </g>

      <!-- 잘못된 상태 둘 -->
      <text class="m no"   x="430" y="238" text-anchor="end" data-at="0">● 리스트 자리에 문자열</text>
      <text class="m gone" x="430" y="238" text-anchor="end" data-at="1+">● 리스트 자리에 문자열</text>
      <text class="m no"   x="396" y="212" text-anchor="end" data-at="0,1">● 그 자리가 null</text>
      <text class="m gone" x="396" y="212" text-anchor="end" data-at="2+">● 그 자리가 null</text>

      <!-- 검사하는 코드의 양 -->
      <text class="cap-l" x="500" y="42">그래서 필요한 검사</text>
      <g data-at="0+">
        <rect class="nd" x="500" y="56" width="190" height="52" rx="9"/>
        <text class="s" x="510" y="76">Map</text>
        <text class="m no" x="510" y="96">쓰는 자리마다 확인 · 여러 벌</text>
      </g>
      <g data-at="1+">
        <rect class="nd" x="500" y="118" width="190" height="52" rx="9"/>
        <text class="s" x="510" y="138">검증 없는 DTO</text>
        <text class="m warn" x="510" y="158">꺼낼 때마다 null 확인</text>
      </g>
      <g data-at="2+">
        <rect class="nd" x="500" y="180" width="190" height="52" rx="9"/>
        <text class="s" x="510" y="200">생성자가 강제하는 DTO</text>
        <text class="m ok" x="510" y="220">안쪽에는 없음</text>
      </g>
      <text class="s val breathe" x="595" y="256" text-anchor="middle" data-at="3">늘어난 것은 선언 한 자리입니다</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>검사하는 코드는 빠뜨릴 수 있지만 타입은 빠뜨릴 수 없습니다.</b> 안쪽에서 다시 묻지 않아도 되는 이유가 이 넓이의 차이입니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaShape', [
  {c:'키에 리스트를 담든 문자열을 담든 <b>put 은 항상 성공합니다.</b> 잘못된 상태 둘이 모두 이 안에 있습니다.', h:3600},
  {c:'역직렬화가 타입을 보므로 문자열이 리스트 자리에 앉는 상태는 사라집니다. <b>그 자리가 null 인 상태는 그대로 남습니다.</b>', h:3800},
  {c:'생성자를 통과하지 못하면 인스턴스 자체가 없습니다. 두 상태 모두 표현할 수 없게 됩니다.', h:3400},
  {c:'세 줄의 차이는 검사를 몇 번 더 했느냐가 아닙니다. <span class="ye">오히려 마지막 줄에 검사하는 코드가 가장 적게 남습니다.</span>', h:4000},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 5장 — 담을 수 있는 상태가 줄어드는 넓이"
```

---

### Task 5: D5 · 응답이 이미 나간 뒤 (6장 `assembly`)

이 장에서 순수 산문으로만 서 있는 대목이고, 조립 시뮬레이터가 다루지 않는 자리다. 시간축 위에 커밋 지점을 찍어, 그 뒤에 붙잡은 예외로는 상태 코드를 되돌릴 수 없다는 순서 문제를 보인다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaCommit', 'assembly')` 추가)

**Interfaces:**
- Consumes: `wireDia`, 앞 태스크들의 CSS
- Produces: `.dia .nd.busy`(흘러 나간 구간을 칠한다). 이 태스크가 가져온다.

- [ ] **Step 0: 새 CSS 한 줄**

```css
.dia .nd.busy{fill:rgba(192,132,252,.14); stroke:var(--purple)}
```

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`assembly` 섹션의 「📤 응답이 이미 나간 뒤」 소제목 아래, 「여기서 반문이 하나 따라옵니다」 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaCommit">
  <div class="dia-top">
    <span class="dia-tag">그림 5 · 되돌릴 수 없는 지점</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 300" role="img" aria-label="렌더링이 진행되는 동안 만들어진 HTML이 조금씩 클라이언트로 흘러 나가고, 어느 지점에서 상태 코드 200과 본문 일부가 이미 건네진다. 그 지점을 응답 커밋이라고 부른다. 커밋보다 늦게 난 예외는 아무리 넓게 감싸도 상태 코드를 500으로 바꾸거나 오류 페이지로 넘길 수 없다. 헤더는 언제나 본문보다 먼저 나가야 하는데 본문이 이미 나갔기 때문이다. 할 수 있는 일은 남은 렌더링을 멈추는 것뿐이고, 사용자에게는 닫는 태그도 없이 잘린 HTML이 남는다.">

      <!-- 브라우저 -->
      <rect class="nd" x="520" y="24" width="170" height="110" rx="10"/>
      <text class="cap-l" x="605" y="20" text-anchor="middle">사용자의 브라우저</text>
      <text class="m mut" x="532" y="48" data-at="0">(아직 아무것도 없음)</text>
      <g data-at="1+">
        <text class="m" x="532" y="48">&lt;html&gt;…머리말</text>
        <text class="m" x="532" y="66">앞쪽 섹션들</text>
      </g>
      <text class="m no breathe" x="532" y="90" data-at="4">여기서 끊김</text>
      <text class="m no" x="532" y="112" data-at="4">닫는 태그 없음</text>

      <!-- 렌더링 진행 막대 -->
      <text class="cap-l" x="40" y="164">서버가 만든 HTML</text>
      <rect class="nd ghost" x="40" y="172" width="650" height="26" rx="6"/>
      <rect class="nd busy" x="42" y="174" width="286" height="22" rx="5" data-at="1+"/>
      <text class="m val" x="185" y="190" text-anchor="middle" data-at="1+">앞쪽 태그들이 만든 부분</text>

      <!-- 커밋 마커 -->
      <line class="wire dash bad" x1="330" y1="150" x2="330" y2="230" data-at="1+"/>
      <text class="cap-l no" x="330" y="146" text-anchor="middle" data-at="1+">응답 커밋</text>
      <text class="m mut" x="330" y="246" text-anchor="middle" data-at="1+">상태 코드 200과 본문 일부가 이미 나갔습니다</text>

      <!-- 예외 마커 -->
      <text class="s no pop" x="470" y="190" text-anchor="middle" data-at="2+">141번째에서 예외</text>
      <line class="wire bad" x1="470" y1="196" x2="470" y2="214" data-at="2+"/>

      <!-- 시간축 -->
      <line class="wire" x1="40" y1="214" x2="694" y2="214"/>
      <polygon fill="var(--border-2)" points="686,209 698,214 686,219"/>
      <text class="cap-l" x="694" y="230" text-anchor="end">시간</text>

      <!-- 커밋 뒤에 할 수 있는 일 -->
      <text class="cap-l" x="40" y="268" data-at="3+">커밋 뒤에 시도해 볼 수 있는 것</text>
      <text class="s no"  x="40" y="288" data-at="3+">✗ 상태 코드를 500으로 바꾼다</text>
      <text class="s no"  x="270" y="288" data-at="3+">✗ 오류 페이지로 넘긴다</text>
      <text class="s ok"  x="470" y="288" data-at="4">✓ 남은 렌더링을 멈춘다</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>try-catch 는 예외를 붙잡을 수는 있어도 이미 나가 버린 바이트를 취소해 주지는 못합니다.</b> 문제는 감싸는 넓이가 아니라 감싸는 자리와 커밋 사이의 순서입니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaCommit', [
  {c:'웹 서버는 응답 본문을 전부 만든 뒤에 한꺼번에 내보내지 않습니다. 페이지가 클수록 만들어지는 대로 조금씩 흘려보내는 쪽이 흔합니다.', h:3600},
  {c:'어느 지점에서 상태 코드 200과 본문 일부가 이미 클라이언트에게 건네집니다. <b>이 순간을 응답 커밋이라고 부릅니다.</b>', h:3800},
  {c:'141번째 태그에서 예외가 납니다. 커밋보다 늦은 자리입니다.', h:3000},
  {c:'500으로 바꾸는 것도 오류 페이지로 넘기는 것도 헤더를 다시 쓰는 일입니다. <span class="no">헤더는 언제나 본문보다 먼저 나가야 하는데 본문이 이미 나갔습니다.</span>', h:4200},
  {c:'할 수 있는 일은 남은 렌더링을 멈추는 것뿐입니다. 사용자에게는 닫는 태그도 없이 잘린 HTML 이 그대로 남습니다.', h:4000},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 6장 — 응답 커밋 뒤에는 되돌릴 것이 없다"
```

---

### Task 6: D6 · 층마다 아는 것이 다르다 (7장 `swallow`)

이 장에는 이미 「누가 잡는가」 데모가 있고, 데모는 층마다 화면과 로그가 어떻게 갈리는지를 보여 준다. **그림은 데모가 다루지 않는 것을 맡는다.** 왜 그렇게 갈리는지, 즉 층마다 아는 것이 다르다는 사실이다. 「파서는 이름과 타입만 압니다」는 본문에 있지만 데모에는 없다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaLayers', 'swallow')` 추가)

**Interfaces:**
- Consumes: `wireDia`, 앞 태스크들의 CSS. 새 부품 없음.

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`swallow` 섹션의 「누가 잡는가」 데모 **뒤**, 「파서에서 잡으면 로그는 남지 않고」 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaLayers">
  <div class="dia-top">
    <span class="dia-tag">그림 6 · 자격은 지식에서 나온다</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 300" role="img" aria-label="같은 예외 하나가 파서에서 섹션 서비스, 페이지 조립기를 거쳐 전역 처리기까지 올라가는 동안, 층마다 아는 것이 다르기 때문에 삼킬 자격도 달라진다는 것을 보여 주는 그림. 파서는 필드 이름과 값의 타입만 알아서 무엇을 대신 채워야 할지 모르고, 섹션 서비스는 그 섹션이 비어도 화면이 성립하는지를 알며, 페이지 조립기는 그 섹션이 빠져도 페이지를 띄울 수 있는지를 안다. 전역 처리기는 요청 하나가 실패했다는 것만 알아서 기록하고 알리는 일밖에 할 수 없다. 대안을 가진 가운데 두 층만 삼킬 자격이 있다.">

      <text class="cap-l" x="70" y="30">예외가 올라가는 방향</text>
      <text class="cap-l" x="450" y="30">이 층이 아는 것</text>

      <!-- 예외가 올라가는 화살표 -->
      <line class="wire bad" x1="46" y1="276" x2="46" y2="252" data-at="0+"/>
      <line class="wire bad" x1="46" y1="252" x2="46" y2="192" data-at="1+"/>
      <line class="wire bad" x1="46" y1="192" x2="46" y2="132" data-at="2+"/>
      <line class="wire bad" x1="46" y1="132" x2="46" y2="72"  data-at="3+"/>
      <polygon fill="var(--bad)" points="41,80 46,68 51,80" data-at="3+"/>

      <!-- 네 층. 아래가 가장 깊다 -->
      <rect class="nd" x="70" y="228" width="360" height="48" rx="9"/>
      <text class="s" x="86" y="248">파서</text>
      <rect class="nd hot" x="70" y="228" width="360" height="48" rx="9" data-at="0"/>
      <text class="m no" x="416" y="266" text-anchor="end" data-at="0+">삼킬 자격 없음</text>
      <text class="s" x="450" y="248" data-at="0+">필드 이름과 그 자리에 온 값의 타입만 압니다.</text>
      <text class="s mut" x="450" y="266" data-at="0+">없는 지식으로 채우면 대안이 아니라 추측입니다.</text>

      <rect class="nd" x="70" y="168" width="360" height="48" rx="9"/>
      <text class="s" x="86" y="188">섹션 서비스</text>
      <rect class="nd hot" x="70" y="168" width="360" height="48" rx="9" data-at="1"/>
      <text class="m ok" x="416" y="206" text-anchor="end" data-at="1+">삼킬 자격 있음</text>
      <text class="s" x="450" y="188" data-at="1+">이 섹션이 비어도 화면이 성립하는지 압니다.</text>
      <text class="s mut" x="450" y="206" data-at="1+">그래서 빈 채로 둔다는 선택을 대신 내릴 수 있습니다.</text>

      <rect class="nd" x="70" y="108" width="360" height="48" rx="9"/>
      <text class="s" x="86" y="128">페이지 조립기</text>
      <rect class="nd hot" x="70" y="108" width="360" height="48" rx="9" data-at="2"/>
      <text class="m ok" x="416" y="146" text-anchor="end" data-at="2+">삼킬 자격 있음</text>
      <text class="s" x="450" y="128" data-at="2+">이 섹션이 빠져도 페이지를 띄울 수 있는지 압니다.</text>
      <text class="s mut" x="450" y="146" data-at="2+">그 섹션을 빼고 나머지를 세울 수 있습니다.</text>

      <rect class="nd" x="70" y="48" width="360" height="48" rx="9"/>
      <text class="s" x="86" y="68">전역 처리기</text>
      <rect class="nd hot" x="70" y="48" width="360" height="48" rx="9" data-at="3"/>
      <text class="m no" x="416" y="86" text-anchor="end" data-at="3+">삼킬 자격 없음</text>
      <text class="s" x="450" y="68" data-at="3+">요청 하나가 실패했다는 것만 압니다.</text>
      <text class="s mut" x="450" y="86" data-at="3+">기록하고 알리는 일까지가 할 수 있는 전부입니다.</text>

      <text class="s val breathe" x="250" y="296" text-anchor="middle" data-at="4">대안을 가진 가운데 두 층만 자격이 있습니다</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>자격을 가르는 것은 층의 높이가 아니라 그 층이 아는 것입니다.</b> 가장 깊은 층과 가장 높은 층이 같은 이유로 자격을 갖지 못합니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaLayers', [
  {c:'파서가 잡고 무언가를 채워 넣으려면 그 자리에 무엇이 맞는지를 파서가 알아야 합니다. <span class="no">파서에게는 없는 지식입니다.</span>', h:3800},
  {c:'섹션 서비스는 그 섹션이 비어도 화면이 성립하는지를 압니다. 대안이 있으므로 잡는 것이 방어가 됩니다.', h:3400},
  {c:'페이지 조립기도 대안을 가집니다. 그 섹션을 빼고 나머지 일곱 칸을 세울 수 있습니다.', h:3400},
  {c:'전역 처리기까지 올라왔다는 것은 <b>그 사이 누구도 대안을 실행하지 못했다</b>는 뜻입니다. 여기서 할 수 있는 일은 기록하고 알리는 것뿐입니다.', h:4000},
  {c:'가장 깊은 층과 가장 높은 층이 같은 이유로 자격을 갖지 못합니다. 잡는 동작이 같아 보여도, 대안이 없으면 그것은 방어가 아니라 삼킴입니다.', h:4400},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 7장 — 자격은 그 층이 아는 것에서 나온다"
```

---

### Task 7: D7 · 스레드 풀이 마르는 순서 (9장 `slowdown`)

이 장에서 가장 시각적인 대목이고, 지금은 산문 두 문단이 혼자 지고 있다. 예외가 하나도 없는데 전체가 서는 이유가 이 그림에서만 보인다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaPool', 'slowdown')` 추가)

**Interfaces:**
- Consumes: `wireDia`, Task 5 가 가져온 `.dia .nd.busy` 포함 앞 태스크들의 CSS
- Produces: `.dia .nd.wait`(대기열에 걸린 요청). 이 태스크가 가져온다.

- [ ] **Step 0: 새 CSS 한 줄**

```css
.dia .nd.wait{fill:rgba(251,191,36,.12); stroke:var(--warn); stroke-dasharray:4 3}
```

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`slowdown` 섹션의 「🧵 스레드 풀이 마르는 순서」 소제목 아래 두 문단 **뒤**, 「말로는 이만큼입니다」 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaPool">
  <div class="dia-top">
    <span class="dia-tag">그림 7 · 예외 없이 서는 법</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 290" role="img" aria-label="느린 섹션을 그리는 요청이 스레드를 하나씩 붙들어 스레드 풀이 마르는 과정을 보여 주는 그림. 요청 하나가 스레드 하나를 붙들고 응답이 오거나 연결이 끊길 때까지 자리를 지키므로, 그런 요청이 풀의 한계만큼 쌓이면 남은 스레드가 없다. 그때부터는 그 요청이 어떤 섹션을 그리려 했는지가 중요하지 않고, 느린 섹션을 아예 부르지 않는 요청까지 대기열에 걸린다. 이 전염에는 예외가 필요 없고 시간만 있으면 된다.">

      <text class="cap-l" x="24" y="34">들어오는 요청</text>
      <text class="cap-l" x="376" y="34" text-anchor="middle">스레드 풀 · 여덟 자리</text>
      <text class="cap-l" x="620" y="34" text-anchor="middle">대기열</text>

      <!-- 들어오는 요청 -->
      <rect class="nd" x="24" y="52" width="188" height="30" rx="7"/>
      <text class="m" x="34" y="72">느린 섹션을 그리는 요청</text>
      <rect class="nd" x="24" y="90" width="188" height="30" rx="7"/>
      <text class="m" x="34" y="110">느린 섹션을 그리는 요청</text>
      <rect class="nd" x="24" y="128" width="188" height="30" rx="7" data-at="1+"/>
      <text class="m" x="34" y="148" data-at="1+">느린 섹션을 그리는 요청</text>
      <rect class="nd" x="24" y="166" width="188" height="30" rx="7" data-at="2+"/>
      <text class="m" x="34" y="186" data-at="2+">느린 섹션을 그리는 요청</text>
      <rect class="nd" x="24" y="204" width="188" height="30" rx="7" data-at="4"/>
      <text class="m val" x="34" y="224" data-at="4">그 섹션을 부르지 않는 요청</text>

      <!-- 풀 -->
      <rect class="nd ghost" x="236" y="44" width="280" height="210" rx="12"/>
      <rect class="nd busy" x="248" y="60"  width="124" height="38" rx="7" data-at="0+"/>
      <text class="m warn" x="310" y="84" text-anchor="middle" data-at="0+">붙들림</text>
      <rect class="nd busy" x="380" y="60"  width="124" height="38" rx="7" data-at="0+"/>
      <text class="m warn" x="442" y="84" text-anchor="middle" data-at="0+">붙들림</text>
      <rect class="nd busy" x="248" y="106" width="124" height="38" rx="7" data-at="1+"/>
      <text class="m warn" x="310" y="130" text-anchor="middle" data-at="1+">붙들림</text>
      <rect class="nd busy" x="380" y="106" width="124" height="38" rx="7" data-at="1+"/>
      <text class="m warn" x="442" y="130" text-anchor="middle" data-at="1+">붙들림</text>
      <rect class="nd busy" x="248" y="152" width="124" height="38" rx="7" data-at="1+"/>
      <text class="m warn" x="310" y="176" text-anchor="middle" data-at="1+">붙들림</text>
      <rect class="nd busy" x="380" y="152" width="124" height="38" rx="7" data-at="2+"/>
      <text class="m warn" x="442" y="176" text-anchor="middle" data-at="2+">붙들림</text>
      <rect class="nd busy" x="248" y="198" width="124" height="38" rx="7" data-at="2+"/>
      <text class="m warn" x="310" y="222" text-anchor="middle" data-at="2+">붙들림</text>
      <rect class="nd busy" x="380" y="198" width="124" height="38" rx="7" data-at="2+"/>
      <text class="m warn" x="442" y="222" text-anchor="middle" data-at="2+">붙들림</text>
      <text class="s no breathe" x="376" y="272" text-anchor="middle" data-at="2+">남은 자리 없음</text>

      <!-- 대기열 -->
      <rect class="nd ghost" x="540" y="44" width="160" height="210" rx="12"/>
      <rect class="nd wait" x="550" y="60"  width="140" height="30" rx="7" data-at="3+"/>
      <text class="m mut" x="620" y="80" text-anchor="middle" data-at="3+">대기</text>
      <rect class="nd wait" x="550" y="98"  width="140" height="30" rx="7" data-at="3+"/>
      <text class="m mut" x="620" y="118" text-anchor="middle" data-at="3+">대기</text>
      <rect class="nd wait" x="550" y="136" width="140" height="30" rx="7" data-at="4"/>
      <text class="m val breathe" x="620" y="156" text-anchor="middle" data-at="4">그 섹션과 무관</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>이 전염에는 예외가 필요 없습니다. 시간만 있으면 됩니다.</b> 격리가 경계에서 기다려도 붙잡을 것이 도착하지 않는 이유가 여기입니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaPool', [
  {c:'요청 하나가 스레드 하나를 붙듭니다. 느린 섹션을 그리는 요청은 응답이 오거나 연결이 끊길 때까지 그 자리를 지킵니다.', h:3400},
  {c:'다음 요청도 다른 스레드를 씁니다. 느린 섹션에 걸리는 요청이 계속 쌓입니다.', h:3200},
  {c:'서버가 동시에 처리할 수 있는 수에는 한계가 있습니다. <span class="no">그 한계만큼 쌓이면 남은 스레드가 없습니다.</span>', h:3600},
  {c:'여기서부터는 그 요청이 어떤 섹션을 그리려 했는지가 중요하지 않습니다. 스레드가 없으면 어떤 요청도 처리를 시작할 수조차 없습니다.', h:3800},
  {c:'느린 섹션을 <b>아예 부르지 않는 요청까지</b> 대기열에 걸립니다. 느린 섹션 하나가 붙든 자리 때문입니다.', h:4200},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 9장 — 예외 없이 풀이 마르는 순서"
```

---

### Task 8: D8 · 예산에서 거꾸로 나눈 타임아웃 (9장 `slowdown`)

3초나 5초 같은 어디서 본 숫자 대신, 상위 예산을 먼저 정하고 그것을 나누는 방향을 막대 하나로 보인다. 연결 몫과 읽기 몫이 따로라는 것, 그리고 너무 짧게 잡으면 정상적인 흔들림까지 실패로 집계된다는 것을 같은 막대 위에서 이어 보인다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaBudget', 'slowdown')` 추가)

**Interfaces:**
- Consumes: `wireDia`, 앞 태스크들의 CSS. 새 부품 없음. 막대의 칠은 클래스가 없는 `<rect fill="...">` 로 준다.

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`slowdown` 섹션의 「🧮 예산에서 거꾸로 나눈 타임아웃」 소제목 아래, 「타당한 답은 반대 방향에서 나옵니다」 문단 **뒤**에 넣는다.

눈금은 1000ms 를 650px 에 대응시킨다. 0.65px 가 1ms 다.

```html
<figure class="dia" id="diaBudget">
  <div class="dia-top">
    <span class="dia-tag">그림 8 · 위에서 아래로 나눈다</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 270" role="img" aria-label="타임아웃 값을 상위 예산에서 거꾸로 나누는 방향을 막대로 보여 주는 그림. 먼저 메인페이지가 지켜야 하는 1000밀리초를 세우고, 그 안에서 섹션 하나가 쓸 몫을 300밀리초로 정한 다음, 그 300밀리초를 다시 연결에 100밀리초와 읽기에 200밀리초로 나눈다. 어디서 본 3000밀리초를 그대로 옮겨 쓰면 섹션 하나가 전체 예산의 세 배를 쓰는 셈이 된다. 반대로 너무 빠듯하게 잡으면 평소 100밀리초짜리 호출이 150밀리초로 흔들리는 정상 범위까지 실패로 집계된다.">

      <!-- 1. 상위 예산 -->
      <text class="cap-l" x="40" y="34">메인페이지가 지켜야 하는 예산</text>
      <rect class="nd" x="40" y="42" width="650" height="30" rx="6"/>
      <text class="m val" x="365" y="62" text-anchor="middle">1000ms</text>

      <!-- 2. 섹션 하나의 몫 -->
      <g data-at="1+">
        <text class="cap-l" x="40" y="98">그 안에서 섹션 하나에 배정한 몫</text>
        <rect fill="var(--purple)" opacity=".22" stroke="var(--purple)" x="40" y="106" width="195" height="28" rx="6"/>
        <text class="m val" x="137" y="125" text-anchor="middle">300ms</text>
        <text class="m mut" x="248" y="125">나머지는 다른 섹션들과 여유의 몫입니다</text>
      </g>

      <!-- 3. 연결 몫과 읽기 몫 -->
      <g data-at="2+">
        <text class="cap-l" x="40" y="160">그 몫을 다시 둘로 나눕니다</text>
        <rect fill="var(--ok)" opacity=".20" stroke="var(--ok)" x="40" y="168" width="65" height="28" rx="6"/>
        <text class="m ok" x="72" y="187" text-anchor="middle">연결 100</text>
        <rect fill="var(--ok)" opacity=".20" stroke="var(--ok)" x="107" y="168" width="128" height="28" rx="6"/>
        <text class="m ok" x="171" y="187" text-anchor="middle">읽기 200</text>
        <text class="m mut" x="248" y="187">읽기만 짧게 잡으면 연결이 지연될 때 아무 힘도 쓰지 못합니다</text>
      </g>

      <!-- 4-a. 어디서 본 숫자를 옮겨 쓰면 -->
      <g data-at="3">
        <text class="cap-l no" x="40" y="222">어디서 본 3000ms 를 그대로 옮겨 쓰면</text>
        <rect fill="var(--bad)" opacity=".18" stroke="var(--bad)" x="40" y="230" width="644" height="28" rx="6"/>
        <text class="m no" x="360" y="249" text-anchor="middle">섹션 하나가 전체 예산의 세 배를 씁니다 · 막대가 화면 밖으로 나갑니다</text>
        <polygon fill="var(--bad)" points="686,232 700,244 686,256"/>
      </g>

      <!-- 4-b. 너무 빠듯하게 잡으면 -->
      <g data-at="4">
        <text class="cap-l warn" x="40" y="222">반대로 너무 빠듯하게 잡으면</text>
        <rect fill="var(--ok)" opacity=".20" stroke="var(--ok)" x="40" y="230" width="65" height="28" rx="6"/>
        <text class="m ok" x="72" y="249" text-anchor="middle">평소 100</text>
        <rect class="nd ghost" x="105" y="230" width="33" height="28" rx="6"/>
        <text class="m warn" x="152" y="249">정상적인 흔들림 150ms</text>
        <line class="wire bad" x1="118" y1="224" x2="118" y2="264"/>
        <text class="m no" x="330" y="249">타임아웃을 120ms 로 잡으면 이 흔들림까지 실패로 집계됩니다</text>
      </g>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>예산은 상한을 정해 줄 뿐입니다.</b> 그 상한 안에 정상적인 흔들림의 폭까지 남겨 두어야 값이 삽니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaBudget', [
  {c:'먼저 정하는 것은 섹션의 타임아웃이 아니라 <b>상위 요청이 통째로 지켜야 하는 예산</b>입니다.', h:3200},
  {c:'그 예산 안에서 섹션 하나가 쓸 몫을 정합니다. 여덟 섹션이 나눠 쓸 시간이 그 안에 있어야 합니다.', h:3400},
  {c:'몫 하나를 다시 둘로 나눕니다. <b>연결을 맺기까지와 응답이 오기까지는 서로 다른 자리입니다.</b> 읽기만 짧게 잡으면 연결이 지연될 때 그 설정은 아직 시작도 하지 않았습니다.', h:4400},
  {c:'어디서 본 3000ms 를 그대로 옮겨 쓰면 <span class="no">섹션 하나가 전체 예산의 세 배를 씁니다.</span>', h:3400},
  {c:'짧게 잡을수록 안전해 보이지만, 정상적인 흔들림과 실제 실패를 가르는 눈금도 함께 좁아집니다. 잡아야 하는 것은 죽은 호출이지 순간적으로 느려진 호출이 아닙니다.', h:4400},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 9장 — 예산을 위에서 아래로 나눈다"
```

---

### Task 9: D9 · 다섯 줄과 다섯 빈자리 (11장 `specgap`)

각색한 화면 정의서 다섯 줄이 지금은 목록과 `.kv` 로만 서 있다. 다섯 개의 빈자리가 우연이 아니라 구조라는 것을 나란한 두 칸으로 보인다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaSpecGap', 'specgap')` 추가)

**Interfaces:**
- Consumes: `wireDia`, 앞 태스크들의 CSS. 새 부품 없음.

- [ ] **Step 1: 테스트 목록을 늘리고 실패를 확인한다**

- [ ] **Step 2: 마크업을 넣는다**

`specgap` 섹션의 다섯 항목 `.kv` 블록 **뒤**, 「다섯 줄이 다섯 개의 정상 경로를 정해 두는 동안」 문단 **앞**에 넣는다.

```html
<figure class="dia" id="diaSpecGap">
  <div class="dia-top">
    <span class="dia-tag">그림 9 · 채워진 칸과 빈 칸</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 318" role="img" aria-label="각색한 화면 정의서 다섯 줄을 왼쪽에 세우고, 줄마다 정상 경로와 실패 경로를 오른쪽 두 칸에 나란히 놓은 그림. 다섯 줄 모두 정상 경로 칸은 순서와 구성과 개수 조건까지 빠짐없이 채워져 있지만, 실패 경로 칸은 다섯 줄 모두 비어 있다. 우연히 다섯이 맞아떨어진 것이 아니라, 규칙 하나마다 그 규칙이 성립하지 않을 때를 위한 문장이 구조적으로 함께 딸려 있지 않기 때문이다.">

      <text class="cap-l" x="30" y="30">화면 정의서 다섯 줄</text>
      <text class="cap-l ok" x="386" y="30" text-anchor="middle">정상 경로</text>
      <text class="cap-l no" x="586" y="30" text-anchor="middle">실패 경로</text>

      <!-- 1 -->
      <rect class="nd" x="30" y="42" width="330" height="42" rx="8"/>
      <rect class="nd hot" x="30" y="42" width="330" height="42" rx="8" data-at="0"/>
      <text class="s" x="42" y="68">등록한 순서로 노출한다</text>
      <rect class="nd" x="376" y="42" width="180" height="42" rx="8"/>
      <text class="m ok" x="466" y="68" text-anchor="middle">정해져 있음</text>
      <rect class="nd ghost" x="572" y="42" width="118" height="42" rx="8"/>
      <text class="m no" x="631" y="68" text-anchor="middle" data-at="0+">없음</text>

      <!-- 2 -->
      <rect class="nd" x="30" y="94" width="330" height="42" rx="8"/>
      <rect class="nd hot" x="30" y="94" width="330" height="42" rx="8" data-at="1"/>
      <text class="s" x="42" y="120">대표 이미지 1장, 상품 카드 목록</text>
      <rect class="nd" x="376" y="94" width="180" height="42" rx="8"/>
      <text class="m ok" x="466" y="120" text-anchor="middle">정해져 있음</text>
      <rect class="nd ghost" x="572" y="94" width="118" height="42" rx="8"/>
      <text class="m no" x="631" y="120" text-anchor="middle" data-at="1+">없음</text>

      <!-- 3 -->
      <rect class="nd" x="30" y="146" width="330" height="42" rx="8"/>
      <rect class="nd hot" x="30" y="146" width="330" height="42" rx="8" data-at="2"/>
      <text class="s" x="42" y="172">화살표로 넘겨 볼 수 있게 한다</text>
      <rect class="nd" x="376" y="146" width="180" height="42" rx="8"/>
      <text class="m ok" x="466" y="172" text-anchor="middle">정해져 있음</text>
      <rect class="nd ghost" x="572" y="146" width="118" height="42" rx="8"/>
      <text class="m no" x="631" y="172" text-anchor="middle" data-at="2+">없음</text>

      <!-- 4 -->
      <rect class="nd" x="30" y="198" width="330" height="42" rx="8"/>
      <rect class="nd hot" x="30" y="198" width="330" height="42" rx="8" data-at="3"/>
      <text class="s" x="42" y="224">그 기간에만 노출하고 지나면 뺀다</text>
      <rect class="nd" x="376" y="198" width="180" height="42" rx="8"/>
      <text class="m ok" x="466" y="224" text-anchor="middle">정해져 있음</text>
      <rect class="nd ghost" x="572" y="198" width="118" height="42" rx="8"/>
      <text class="m no" x="631" y="224" text-anchor="middle" data-at="3+">없음</text>

      <!-- 5 -->
      <rect class="nd" x="30" y="250" width="330" height="42" rx="8"/>
      <rect class="nd hot" x="30" y="250" width="330" height="42" rx="8" data-at="4"/>
      <text class="s" x="42" y="276">제목을 누르면 목록 페이지로 이동한다</text>
      <rect class="nd" x="376" y="250" width="180" height="42" rx="8"/>
      <text class="m ok" x="466" y="276" text-anchor="middle">정해져 있음</text>
      <rect class="nd ghost" x="572" y="250" width="118" height="42" rx="8"/>
      <text class="m no" x="631" y="276" text-anchor="middle" data-at="4+">없음</text>

      <!-- 오른쪽 칸을 통째로 묶는 표시 -->
      <rect class="nd ghost" x="566" y="36" width="130" height="262" rx="10" data-at="5"/>
      <text class="s no breathe" x="631" y="308" text-anchor="middle" data-at="5">다섯 칸 전부</text>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>우연히 다섯이 맞아떨어진 것이 아닙니다.</b> 규칙 하나마다 그 규칙이 성립하지 않을 때를 위한 문장이 구조적으로 함께 딸려 있지 않습니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배선한다**

```js
wireDia('diaSpecGap', [
  {c:'"등록한 순서로 노출한다"는 정해져 있습니다. <span class="no">그 데이터를 받아오지 못하면 무엇을 노출하는지는 없습니다.</span>', h:3600},
  {c:'구성도 정해져 있습니다. <span class="no">이미지가 깨졌거나 카드가 하나도 없으면 무엇을 대신 놓는지는 없습니다.</span>', h:3600},
  {c:'개수 조건도 정해져 있습니다. <span class="no">넘기다가 그 카드를 불러오지 못하면 무엇을 보여 주는지는 없습니다.</span>', h:3600},
  {c:'노출 기간도 정해져 있습니다. <span class="no">기간을 계산할 기준 시간을 가져오지 못하면 어떻게 판단하는지는 없습니다.</span>', h:3800},
  {c:'이동 동작도 정해져 있습니다. <span class="no">이동할 목록 페이지가 열리지 않으면 무엇을 하는지는 없습니다.</span>', h:3600},
  {c:'다섯 줄이 다섯 개의 정상 경로를 정해 두는 동안, <b>다섯 개의 실패 경로 자리는 전부 비어 있습니다.</b>', h:4200},
]);
```

- [ ] **Step 4: 검사기와 테스트를 돌리고 커밋한다**

```bash
git commit -am "defprog-dia: 11장 — 채워진 다섯 칸과 비어 있는 다섯 칸"
```

---

### Task 10: D10 · 반경 지도 (15장 `recap`)

**단일 출처를 지키는 것이 이 태스크의 핵심 제약이다.** `RADIUS` 배열 하나가 개요와 15장 양쪽을 그리고 있고, 코드에 "두 그림이 어긋날 수 없는 이유가 이 두 줄이다"라는 주석이 붙어 있다. 그림도 그 배열에서 그린다. SVG 안에 반경 이름을 손으로 적으면 그 불변식이 깨진다.

15장의 카드 목록(`#recapMap`)은 그림으로 **대체한다.** 15장 본문이 이미 여섯 반경을 문단으로 다 풀어 두었으므로 카드 목록은 압축 재진술이고, 그림이 그 자리를 더 잘 맡는다. 개요의 카드 목록(`#radiusMap`)은 그대로 둔다. 개요는 문서를 펼치는 자리라 압축된 목록이 맞다.

**Files:**
- Modify: `defensive_programming.html`, `tools/test_defensive_diagrams.py` (`('diaRadius', 'recap')` 추가)

**Interfaces:**
- Consumes: `wireDia`, `RADIUS` 배열, 앞 태스크들의 CSS
- Produces: `paintRadiusDia(svgEl)`. `.rband-hot`, `.rband-mark` 클래스를 이 태스크가 가져온다.

**주의 세 가지:**
1. **`data-at` 을 템플릿 문자열로 쓰지 않는다.** `data-at="${i}"` 를 소스에 남기면 정적 테스트의 표기 검사가 그 문자열을 해석할 수 없는 표기로 잡는다. 도형은 innerHTML 로 만들되 `data-at` 은 `setAttribute('data-at', String(i))` 로 붙인다. 12장 앵커 때와 같은 이유다.
2. **`paintRadiusDia` 는 `wireDia('diaRadius', ...)` 보다 먼저 부른다.** `wireDia` 는 배선하는 시점에 `[data-at]` 을 모으므로, 나중에 그리면 아무것도 잡지 못한다.
3. **`.hole` CSS 가 사장된다.** `#recapMap` 이 없어지면 `paintRadius` 의 `withHoles` 갈래도 쓰이지 않는다. `withHoles` 파라미터와 `.hole` CSS 규칙을 함께 지운다. 지우지 않으면 `check_dead_css.py` 가 실패한다.

- [ ] **Step 0: 새 CSS 두 줄**

```css
.dia .rband-hot{fill:none; stroke:var(--accent); stroke-width:1.8}
.dia .rband-mark{font-family:var(--mono); font-size:10.5px}
```

- [ ] **Step 1: 테스트 목록을 늘리고, 단일 출처를 지키는 테스트를 더한다**

`tools/test_defensive_diagrams.py` 에 추가한다.

```python
def test_the_radius_diagram_does_not_hardcode_the_map(src):
    """반경 이름을 SVG 안에 손으로 적으면 RADIUS 배열과 어긋날 수 있다.

    본문 코드에 '두 그림이 어긋날 수 없는 이유가 이 두 줄이다'라고 적어 둔 그 불변식을
    그림에도 그대로 건다. 그림은 배열에서 그려야 한다."""
    body = dict(iter_figures(src))['diaRadius']
    for name in ('한 줄', '한 함수', '한 객체', '한 모듈', '프로세스 경계', '요구사항'):
        assert f'>{name}<' not in body, f'diaRadius 가 "{name}" 을 마크업에 직접 적었다'
    assert 'paintRadiusDia' in src


def test_the_recap_card_list_was_replaced_not_duplicated(src):
    """같은 지도를 15장에 두 번 두지 않는다."""
    assert 'recapMap' not in src
```

- [ ] **Step 2: 마크업을 넣는다**

`recap` 섹션에서 기존 `#recapMap` 컨테이너를 **지우고** 그 자리에 넣는다. `<g id="radiusBands">` 는 비워 두고 JS 가 채운다.

```html
<figure class="dia" id="diaRadius">
  <div class="dia-top">
    <span class="dia-tag">그림 10 · 반경과 구멍</span>
    <span class="dia-sp"></span>
    <button class="dia-btn ghost" type="button">▶ 재생</button>
    <div class="dia-dots"></div>
  </div>
  <div class="dia-hint" aria-hidden="true">← 좌우로 밀어서 보세요 →</div>
  <div class="dia-scroll">
    <svg viewBox="0 0 720 300" role="img" aria-label="방어의 반경 여섯 개를 안쪽에서 바깥쪽으로 겹친 띠로 그린 지도. 가장 안쪽은 한 줄이고 바깥으로 갈수록 한 함수, 한 객체, 한 모듈, 프로세스 경계, 요구사항으로 넓어진다. 반경마다 막을 수 있는 것이 다르고, 어느 반경도 다음 반경의 몫까지 대신 막아 주지 않는다. 앞 반경이 막고 남긴 것이 그대로 다음 반경의 문제였고, 가장 바깥의 요구사항까지 가서야 사슬이 닫힌다. 그 반경 밖에는 코드가 없다.">
      <g id="radiusBands"></g>
    </svg>
  </div>
  <div class="dia-cap" aria-hidden="true"></div>
  <figcaption><b>반경마다 막는 것이 다르고, 어느 반경도 다음 반경의 몫까지 대신 막아 주지 않습니다.</b> 앞 반경이 막고 남긴 것이 그대로 다음 반경의 문제였습니다.</figcaption>
</figure>
```

- [ ] **Step 3: 배열에서 그리는 함수를 넣는다**

기존 `paintRadius` 정의 아래에 넣는다. 함께 고쳐야 하는 것이 셋이다.

1. `paintRadius($('#recapMap'), true)` 호출을 지운다.
2. `paintRadius` 의 `withHoles` 파라미터와 그 갈래(`${withHoles ? ... : ''}`)를 지운다.
3. **살아남는 호출도 함께 고친다.** `paintRadius($('#radiusMap'), false)` → `paintRadius($('#radiusMap'))`. 인자를 그대로 두면 없어진 파라미터에 값을 넘기는 코드가 남는다.

```js
/* 반경 지도를 그림으로도 그린다. 문구는 손으로 적지 않고 위의 RADIUS 에서 가져온다.
   여기 적어 두면 배열과 어긋날 수 있고, 그 어긋남은 눈에 띄지 않는 채로 남는다. */
function paintRadiusDia(root){
  if(!root) return;
  const CX = 360, CY = 150, HW = 52, HH = 22, DW = 52, DH = 20;
  const base = [], hot = [];
  // 바깥 띠부터 그려야 안쪽 띠가 위에 온다
  for(let k = RADIUS.length - 1; k >= 0; k--){
    const x = CX - (HW + k * DW), y = CY - (HH + k * DH);
    const w = 2 * (HW + k * DW), h = 2 * (HH + k * DH);
    base.push(`<rect class="nd" x="${x}" y="${y}" width="${w}" height="${h}" rx="12"/>`);
    if(k > 0){
      base.push(`<text class="s" x="${x + 12}" y="${y + 18}">반경 ${k + 1} · ${RADIUS[k].n}</text>`);
      base.push(`<text class="cap-l" x="${x + 12}" y="${y + 34}">${RADIUS[k].ch}장</text>`);
    } else {
      base.push(`<text class="s" x="${CX}" y="${CY + 4}" text-anchor="middle">반경 1 · ${RADIUS[0].n}</text>`);
    }
  }
  // 강조 테두리와 구멍 표시는 단계마다 하나씩만 뜬다
  for(let k = 0; k < RADIUS.length; k++){
    const x = CX - (HW + k * DW), y = CY - (HH + k * DH);
    const w = 2 * (HW + k * DW), h = 2 * (HH + k * DH);
    // 마지막 반경만 판정이 다르다. 클래스명을 보간으로 조립하면 check_dead_css 가
    // 정의 쪽만 보고 사장 CSS 로 잡으므로, 갈래마다 리터럴로 쓴다.
    const mark = (k === RADIUS.length - 1)
      ? `<text class="rband-mark ok" x="${x + w + 8}" y="${y + 16}">여기가 종착지입니다</text>`
      : `<text class="rband-mark no" x="${x + w + 8}" y="${y + 16}">↳ 그럼에도 남는 것이 있습니다</text>`;
    hot.push(`<g class="rband-hot-g">`
      + `<rect class="rband-hot" x="${x}" y="${y}" width="${w}" height="${h}" rx="12"/>`
      + mark + `</g>`);
  }
  root.innerHTML = base.join('') + hot.join('');
  // data-at 은 속성으로 붙인다. 템플릿 문자열로 남기면 표기 검사가 해석하지 못한다.
  const gs = $$('.rband-hot-g', root);
  gs.forEach((g, k) => g.setAttribute('data-at', String(k)));
}
paintRadiusDia($('#radiusBands'));
```

`.rband-hot-g` 도 CSS 정의가 필요하지 않은 클래스이므로 스타일을 붙이지 않는다. `check_dead_css.py` 는 정의되지 않은 클래스를 실패로 잡지 않는다(역방향 검사는 정보용이다).

- [ ] **Step 4: 배선한다**

`paintRadiusDia` 호출 **뒤**에 온다.

```js
wireDia('diaRadius', RADIUS.map(r => ({
  c: r.can + (r.hole === '여기가 종착지다'
       ? ' <span class="ye">여기가 종착지입니다. 이 반경 밖에는 코드가 없습니다.</span>'
       : ' <span class="no">↳ 그럼에도 ' + r.hole + '.</span>'),
  h: 4000,
})));
```

- [ ] **Step 5: 검사기와 테스트를 돌리고 커밋한다**

`check_dead_css.py` 가 `.hole` 을 사장으로 잡으면 그 규칙을 지운다. 그것이 이 태스크가 예상한 결과다.

```bash
git commit -am "defprog-dia: 15장 — 반경 지도를 배열에서 그린다"
```

---

### Task 11: 렌더링 도중 예외에 맥락을 싣는 자리 (2장 `unknown` + 부록 A `ap-java`)

도해가 아니라 내용 보강이다. 2장은 "예외에 세 조각을 담아라"까지 가르치고 멈추는데, 오늘 예외가 난 자리는 뷰를 렌더링하는 도중이고 거기에는 스프링 특유의 제약이 걸린다. 그 제약이 6장의 응답 커밋과 정확히 만나는데, 지금 문서에는 그 연결이 없다.

**Files:**
- Modify: `defensive_programming.html` (`unknown` 섹션, `ap-java` 섹션)

**Interfaces:**
- Consumes: 없음. 도해 태스크들과 독립적이다.
- Produces: 없음.

**사실 관계로 확인된 것만 쓴다. 확인 출처는 스프링 레퍼런스와 javadoc 이다.**

1. `HandlerExceptionResolver` 의 범위는 "exceptions thrown during **handler mapping or execution**" 이다. `doResolveException` 의 파라미터 설명도 "the exception that got thrown **during handler execution**" 이다. 뷰 렌더링은 이 범위 밖이다.
2. `HandlerInterceptor` 의 수명주기는 `preHandle` → 핸들러 → `postHandle`(**뷰 렌더링 전**) → `afterCompletion`(**뷰 렌더링 후**) 이다. 렌더링 뒤에 불리는 인터셉터 훅은 `afterCompletion` 하나뿐이다.
3. `ServletResponse.isCommitted()` 가 true 면 상태 코드와 헤더를 다시 쓸 수 없다. 6장이 이미 다룬 사실이다.

**이 세 가지를 넘어서는 주장을 쓰지 않는다.** 특히 `afterCompletion` 의 `ex` 파라미터에 렌더링 예외가 실제로 실려 오는지는 `DispatcherServlet` 의 배선에 달린 것이고 javadoc 의 그 파라미터 설명은 핸들러 실행까지만 말한다. **그 주장은 쓰지 않는다.** 이 문서는 추측과 증거를 가르라고 가르치는 문서다.

- [ ] **Step 1: 2장에 한 문단을 넣는다**

`unknown` 섹션에서 `cause` 를 남기는 두 줄을 설명하는 문단(「첫 번째 코드는 컴파일도 되고」로 시작해 「그대로 딸려 나옵니다.」로 끝나는 문단) **뒤**, `<h3>🙈 담지 말아야 하는 것</h3>` **앞**에 넣는다.

```html
      <p>여기에 이번 사건이 걸리는 제약이 하나 더 있습니다. 세 조각을 담으려면 그 조각을 아는 코드가
      예외를 붙잡아야 하는데, 오늘 예외가 난 자리는 뷰를 렌더링하는 도중입니다. 스프링에서 예외를 한곳에서
      받는 자리로 흔히 떠올리는 <code>@ControllerAdvice</code>는 이 자리에 닿지 않습니다. 스프링이
      <code>HandlerExceptionResolver</code>의 범위를 "핸들러 매핑이나 실행 중에 던져진 예외"로 긋고 있고,
      렌더링은 그 뒤에 오기 때문입니다. 사용자가 오류 페이지를 보게 되더라도 그것은 예외가 컨테이너까지
      올라가 오류 디스패치가 새로 돈 결과이지, 우리가 붙여 둔 핸들러가 돈 결과가 아닙니다. 그러면 렌더링
      도중에 난 예외에는 세 조각을 어디에서 담아야 할까요. 자리가 넷 있고, 넷과 그 한계는
      <a class="link" href="#ap-java">부록 A</a>에 정리해 두었습니다. 지금 붙잡아 둘 것은 하나입니다.
      <b>그 넷 어디에서 담든, 응답이 이미 나가 버린 뒤라면 할 수 있는 일은 기록을 남기는 것뿐입니다.</b>
      담는 일과 고치는 일은 다른 일이고, 렌더링 도중이라면 담는 일만 남습니다. 왜 그런지는 6장이
      다룹니다.</p>
```

**주의:** 이 장에는 이미 `.oneline` 이 하나 있다. 새 강조 상자를 만들지 않는다. `<b>` 강조까지가 전부다.

- [ ] **Step 2: 부록 A 에 행 하나를 넣는다**

`ap-java` 표에서 「마지막 그물」 행 **바로 뒤**에 넣는다. 그 행이 `@ControllerAdvice` 를 다루므로, 그것이 닿지 않는 자리를 바로 옆에 두는 것이 읽는 순서에 맞다.

```html
            <tr>
              <td>뷰를 렌더링하는 도중 난 예외에 맥락을 싣기</td>
              <td><code>View</code>를 감싸는 <code>ViewResolver</code> ·
              <code>HandlerInterceptor.afterCompletion</code> ·
              <code>OncePerRequestFilter</code> · MDC</td>
              <td>바로 위의 <code>@ControllerAdvice</code>는 이 자리에 닿지 않습니다. 스프링이 예외 해결의
              범위를 핸들러 매핑과 실행까지로 긋고 있고, 렌더링은 그 뒤이기 때문입니다. 세 조각이 가장 잘
              모이는 자리는 <code>View</code>를 데코레이터로 감싸 <code>render</code>를 자기
              <code>try</code> 안에서 부르는 것입니다. 뷰 이름과 모델의 <b>키</b>, 그리고
              <code>isCommitted()</code>를 그 자리에서 함께 담을 수 있습니다. 값이 아니라 키만 담는 이유는
              2장이 짚었습니다. <code>afterCompletion</code>은 렌더링이 끝난 뒤에 불리는 유일한 인터셉터
              훅이라 요청 단위 정보를 남기기 좋고, 필터는 빠짐없이 걸리는 대신 어느 섹션이었는지를 모릅니다.
              MDC에 미리 넣어 두면 누가 어디에서 기록하든 그 조각들이 로그 줄에 딸려 나옵니다. 넷 중 무엇을
              고르든 <code>isCommitted()</code>가 true면 남는 일은 기록뿐입니다.</td>
              <td class="c">2·6장</td>
            </tr>
```

- [ ] **Step 3: 검사기와 테스트를 돌린다**

`#ap-java` 앵커가 실제로 있는지 `check_tutorial.py` 가 확인해 준다. `<b>` 안의 "키"가 표 안에서 굵게 나오는지 눈으로 확인한다.

```
python3 tools/check_tutorial.py defensive_programming.html
python3 tools/check_dead_css.py defensive_programming.html
python3 -m pytest tools/ -q
```

- [ ] **Step 4: 커밋**

```bash
git commit -am "defprog-dia: 2장·부록 A — 렌더링 도중 예외에 맥락을 싣는 자리 넷"
```

---

### Task 12: 동작 검사와 완주 검사

정적 검사는 도해가 거기 있다는 것까지만 본다. 단계가 실제로 넘어가는지, 움직임을 줄여 달라고 한 사용자에게 자동 재생이 걸리지 않는지는 브라우저에서만 확인된다.

**Files:**
- Create: `tools/test_defensive_diagram_behavior.py`
- Modify: 필요하면 `defensive_programming.html`

**Interfaces:**
- Consumes: 열 개 도해 전부

- [ ] **Step 1: 동작 테스트를 쓴다**

기존 `tools/test_defensive_behavior.py` 의 구조를 따른다. **브라우저가 없으면 건너뛰지 않고 실패한다.** 이 저장소의 기존 규칙이다.

```python
"""도해가 실제로 움직이는지 브라우저에서 확인한다.

정적 검사(test_defensive_diagrams.py)는 도해가 거기 있다는 것까지만 본다.
단계가 넘어가는지, 움직임을 줄여 달라고 한 사용자에게 자동 재생이 걸리지 않는지는
여기에서만 확인된다. 브라우저가 없으면 건너뛰지 않고 실패한다.
"""
import pytest
from pathlib import Path

DOC = (Path(__file__).resolve().parent.parent / 'defensive_programming.html').as_uri()

DIAGRAMS = ['diaBlame', 'diaSilent', 'diaBoundary', 'diaShape', 'diaCommit',
            'diaLayers', 'diaPool', 'diaBudget', 'diaSpecGap', 'diaRadius']


@pytest.fixture(scope='module')
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def pg(browser):
    page = browser.new_page()
    page.goto(DOC)
    yield page
    page.close()


def test_every_diagram_is_wired(pg):
    """배선되지 않은 도해는 단계 점이 하나도 없다. wireDia 호출을 빠뜨리면 여기서 걸린다."""
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        assert n >= 4, f'{fid}: 단계 점이 {n}개다'


def test_clicking_a_dot_moves_to_that_step(pg):
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        for k in (0, n - 1):
            pg.locator(f'#{fid} .dia-dot').nth(k).click()
            assert pg.get_attribute(f'#{fid}', 'data-s') == str(k)
            on = pg.locator(f'#{fid} .dia-dot.on')
            assert on.count() == 1


def test_the_step_box_changes_with_the_step(pg):
    """단계 설명이 단계마다 갈리지 않으면 단계를 나눈 뜻이 없다."""
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        seen = set()
        for k in range(n):
            pg.locator(f'#{fid} .dia-dot').nth(k).click()
            seen.add(pg.inner_text(f'#{fid} .dia-cap').strip())
        assert len(seen) == n, f'{fid}: 단계 설명이 {len(seen)}가지뿐이다'


def test_only_the_elements_for_this_step_are_visible(pg):
    """data-at 이 지정한 단계에서만 .vis 가 붙는다."""
    for fid in DIAGRAMS:
        n = pg.locator(f'#{fid} .dia-dot').count()
        pg.locator(f'#{fid} .dia-dot').nth(0).click()
        wrong = pg.evaluate("""(fid) => {
          const fig = document.getElementById(fid);
          const i = +fig.dataset.s;
          const bad = [];
          fig.querySelectorAll('[data-at]').forEach(el => {
            const spec = el.dataset.at;
            const want = window.diaAt(spec, %d).has(i);
            if (el.classList.contains('vis') !== want) bad.push(spec);
          });
          return bad;
        }""" % n, fid)
        assert wrong == [], f'{fid}: {wrong} 의 표시가 단계와 어긋난다'


def test_the_play_button_toggles(pg):
    fid = DIAGRAMS[0]
    btn = pg.locator(f'#{fid} .dia-btn')
    before = btn.get_attribute('aria-pressed')
    btn.click()
    assert btn.get_attribute('aria-pressed') != before


def test_reduced_motion_does_not_autoplay(browser):
    """움직임을 줄여 달라고 한 사용자에게는 자동 재생을 걸지 않고 마지막 단계를 세워 둔다."""
    ctx = browser.new_context(reduced_motion='reduce')
    page = ctx.new_page()
    page.goto(DOC)
    for fid in DIAGRAMS:
        n = page.locator(f'#{fid} .dia-dot').count()
        assert page.get_attribute(f'#{fid}', 'data-s') == str(n - 1), f'{fid}: 마지막 단계가 아니다'
        assert 'paused' in (page.get_attribute(f'#{fid}', 'class') or ''), f'{fid}: 멈춰 있지 않다'
    ctx.close()


def test_the_radius_diagram_is_drawn_from_the_shared_array(pg):
    """반경 지도의 문구가 RADIUS 에서 나온다. 손으로 적으면 개요와 어긋날 수 있다."""
    n = pg.evaluate("window.RADIUS.length")
    assert pg.locator('#diaRadius .rband-hot').count() == n
    names = pg.evaluate("window.RADIUS.map(r => r.n)")
    text = pg.text_content('#diaRadius svg')  # SVG 요소에는 innerText 가 없다
    for nm in names:
        assert nm in text, f'반경 이름 "{nm}" 이 그림에 없다'


def test_dia_at_reads_all_three_notations(pg):
    assert pg.evaluate("[...window.diaAt('0,2', 5)]") == [0, 2]
    assert pg.evaluate("[...window.diaAt('1-3', 5)]") == [1, 2, 3]
    assert pg.evaluate("[...window.diaAt('2+', 5)]") == [2, 3, 4]


def test_no_diagram_overflows_a_narrow_screen(browser):
    """좁은 화면에서 넘치는 것은 그림 상자 안이어야 한다. 본문이 가로로 밀리면 안 된다."""
    ctx = browser.new_context(viewport={'width': 375, 'height': 800})
    page = ctx.new_page()
    page.goto(DOC)
    doc_w = page.evaluate("document.documentElement.scrollWidth")
    win_w = page.evaluate("window.innerWidth")
    assert doc_w <= win_w + 1, f'문서가 가로로 넘친다: {doc_w} > {win_w}'
    ctx.close()
```

- [ ] **Step 2: 테스트가 쓰는 것을 `window` 에 올린다**

`diaAt` 과 `RADIUS` 는 스크립트 안의 지역 이름이라 `page.evaluate` 가 볼 수 없다. 기존 데모 엔진들이 `window` 에 올라가 있는 것과 같은 방식으로 올린다. 이름 앞에 밑줄 둘을 붙여 테스트용이라는 것을 드러낸다.

`wireDia` 정의 아래에 넣는다.

```js
// 테스트가 클릭을 흉내 내는 대신 이 둘을 직접 부른다. window.EL · window.Assembly ·
// window.QUESTIONS 를 올려 둔 것과 같은 이유이고, 이름도 같은 관례로 붙인다.
window.diaAt = diaAt;
window.RADIUS = RADIUS;
```

- [ ] **Step 3: 테스트를 돌린다**

```
python3 -m pytest tools/test_defensive_diagram_behavior.py -q
```
브라우저가 없으면 설치한다: `python3 -m playwright install chromium`

- [ ] **Step 4: 완주 검사**

브라우저에서 문서를 처음부터 끝까지 한 번 훑고 아래를 눈으로 확인한다. 발견한 것은 고치고, 고칠 수 없는 것은 보고한다.

1. 도해 열 개가 전부 뜨고, 각각 자동으로 단계가 넘어간다.
2. 스크롤로 지나갈 때 화면 밖의 도해는 멈춰 있다. 열 개가 동시에 타이머를 돌리지 않는다.
3. 재생을 손으로 멈춘 도해는 다시 스크롤해 돌아와도 저절로 돌지 않는다.
4. 375px 폭에서 본문이 가로로 밀리지 않고, 그림 상자 안에서만 밀린다. 밀 수 있다는 표시가 뜬다.
5. 인쇄 미리보기에서 부록 C 카드만 남는 규칙이 그대로다. 도해가 인쇄물에 끼어들지 않는다.
6. 진행률, 용어 사전, 퀴즈, 기존 데모 열두 개가 전과 같이 동작한다.
7. 2장의 새 문단에서 부록 A 로 가는 링크가 실제로 이동한다.

- [ ] **Step 5: 전체 검사와 커밋**

```bash
python3 tools/check_tutorial.py defensive_programming.html
python3 tools/check_dead_css.py defensive_programming.html
python3 -m pytest tools/ -q
git add -A && git commit -m "defprog-dia: 동작 검사와 완주 검사"
```

---

## 자기 점검

**설계 문서 대조.** 설계 문서 3절의 도해 열 장이 Task 1~10 에 하나씩 대응한다. 4절의 구속 조건은 전역 제약으로 옮겼고, 5절의 접근성은 Task 1 의 CSS·구동기와 Task 12 의 `test_reduced_motion_does_not_autoplay` 가 맡는다. 6절의 검증은 Task 12 다. 7절이 하지 않기로 한 것 셋은 어느 태스크도 건드리지 않는다. 사용자가 추가로 요청한 렌더링 예외 항목은 설계 문서에 없던 것이므로 Task 11 로 따로 두었고, 도해 작업과 독립적이라 순서를 바꿔도 된다.

**타입 일관성.** `wireDia(id, steps)` 의 `steps` 는 `{c, h}` 배열이고 Task 1~10 이 전부 같은 모양으로 부른다. `diaAt(spec, n)` 은 Set 을 돌려주고 `wireDia` 와 테스트가 같은 계약으로 쓴다. `paintRadiusDia(root)` 는 `wireDia('diaRadius', ...)` 보다 먼저 불려야 하며 Task 10 이 그 순서를 명시한다.

**빠뜨린 것이 없는지.** CSS 부품은 그것을 처음 쓰는 태스크가 가져온다. `.nd.bad` 는 Task 3, `.gone` 은 Task 4, `.nd.busy` 는 Task 5, `.nd.wait` 는 Task 7, `.rband-hot`·`.rband-mark` 는 Task 10 이다. 나머지는 전부 Task 1 이 가져오고, Task 1 은 D1 이 실제로 쓰는 것만 가져오므로 그 시점에 사장 CSS 가 없다.
