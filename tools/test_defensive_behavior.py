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
