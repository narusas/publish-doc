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
