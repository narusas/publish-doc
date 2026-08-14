# 웹 인증 기초 문서 — 사실 검증 기록

`docs/superpowers/specs/2026-08-14-web-auth-basics-design.md` §7의 검증 항목 8건.
서술을 고칠 때는 이 파일을 먼저 보고, 여기에 없는 사실은 확인한 뒤에 쓴다.

검증일: 2026-08-14 · 기준 버전: Spring Security 6.5, Spring Session 현행, Tomcat 10.1

---

## V1 · Spring Security 6의 `SecurityContext` 저장 변경 — **확인됨**

> "In Spring Security 6, the default behavior is that the `SecurityContextHolderFilter` will only
> read the `SecurityContext` from `SecurityContextRepository` and populate it in the
> `SecurityContextHolder`. **Users now must explicitly save the `SecurityContext`** with the
> `SecurityContextRepository` if they want the `SecurityContext` to persist between requests."
> — [Session Management Migrations](https://docs.spring.io/spring-security/reference/6.5/migration/servlet/session-management.html)

- Spring Security 5의 `SecurityContextPersistenceFilter`(읽기+쓰기)가 6에서
  **`SecurityContextHolderFilter`(읽기 전용)로 대체**되었다.
- `requireExplicitSave`는 **6에서 기본 true**다. `.requireExplicitSave(true)`를 명시하는 설정
  예제가 레퍼런스에 있지만, 그것은 5의 동작을 보존하려는 **마이그레이션 용도**의 반대편 설명이다.
- 이유: "removes ambiguity and improves performance by only requiring writing to the
  `SecurityContextRepository` (i.e. HttpSession) when it is necessary."

### ⚠️ 중간에 한 번 틀렸던 지점

`persistence.html`을 요약해 읽었을 때 **"requireExplicitSave는 기본값이 아니다"**라는 정반대
결론이 나왔다. 마이그레이션 가이드 원문으로 교차 확인해 뒤집었다. 이 항목은 낡은 블로그 글과
요약본이 특히 자주 틀리는 곳이므로, 서술할 때 위 인용문을 근거로 삼는다.

### 확정하지 못한 것

내장 폼 로그인 필터가 인증 성공 시 컨텍스트를 저장하는 **경로**는 확정하지 못했다.
`AbstractAuthenticationProcessingFilter.setSecurityContextRepository` 자바독은
"The default action is not to save the `SecurityContext`"라고 하는데, 이는 필터 단독 기본값이고
`HttpSecurity` 설정자가 무엇을 주입하는지는 확인하지 못했다.

**→ 13장 서술 제한**: "직접 `SecurityContextHolder`에 값을 넣는 커스텀 코드는 명시적으로
저장해야 한다"까지만 쓴다. 내장 필터의 내부 동작은 서술하지 않는다.

---

## V2 · 비밀번호 인코더 — **확인됨**

출처: [Password Storage](https://docs.spring.io/spring-security/reference/6.5/features/authentication/password-storage.html),
[Cryptography](https://docs.spring.io/spring-security/reference/6.5/features/integrations/cryptography.html)

- `BCryptPasswordEncoder` **기본 강도(strength) = 10**, 지정 가능 범위 **4~31**.
- **16바이트 무작위 salt**를 자체적으로 포함한다.
- 강도 값이 **해시 문자열 안에 저장**되어, 나중에 강도를 바꿔도 기존 비밀번호가 깨지지 않는다.
  → 2장에서 "work factor를 올릴 수 있다"를 말할 때 이 성질이 근거다.
- "intentionally slow to hinder password crackers" — 2장의 **"느린 것이 기능이다"** 프레이밍이
  공식 문서 표현과 일치한다.
- 권장 생성법: `PasswordEncoderFactories.createDelegatingPasswordEncoder()`.

**미확인**: `{bcrypt}` 접두어 문자열 자체를 원문에서 직접 인용하지 못했다. 접두어 형식을
코드로 쓸 때는 구현 단계에서 재확인한다.

### V2 보강 (2026-08-14, 1~2장 구현 중 추가 확인)

구현자가 "work factor를 1 올리면 비용이 두 배"를 facts에 없다는 이유로 **사실로 쓰지 않고
남겨 둔** 것을 보고, 확인해서 보강한다. 올바른 판단이었다.

출처: [Wikipedia — bcrypt](https://en.wikipedia.org/wiki/Bcrypt) (**2차 출처**. 다만 아래는
파라미터의 정의 자체라 위험이 낮고, Spring 문서의 "strength 4~31이 계산량을 조절한다"와
어긋나지 않는다.)

- **cost는 반복 횟수의 log2다.** `cost: Number (4..31) log2(Iterations). e.g. 12 ==> 2^12 =
  4,096 iterations` → **1 올리면 정확히 두 배.** 본문에 사실로 써도 된다.
- salt는 **16바이트(128비트)** — Spring 문서와 일치한다.
- 인코딩된 해시 형식: `$2<a/b/x/y>$[cost]$[22자 salt][31자 해시]`.
  **cost가 문자열 안에 들어 있다**는 V2 본문의 서술이 형식 차원에서 확인된다.
  `$2a$`/`$2b$` 등 버전 표시는 구현 버그 수정 이력을 나타낸다.

→ 2장에서 "work factor를 1 올리면 비용이 두 배"를 **사실로 단언해도 된다.** 다만 `$2a$` 같은
구체적 리터럴을 코드로 쓸 거라면 `{bcrypt}` 접두어와 마찬가지로 Spring 원문을 한 번 더 확인한다.

---

## V3 · Spring Session의 쿠키 — **확인됨 · 문서의 핵심 함정**

출처: [Spring Session API](https://docs.spring.io/spring-session/reference/api.html)

- **기본 쿠키 이름은 `SESSION`이다. `JSESSIONID`가 아니다.**
  > "`cookieName`: The name of the cookie to use. Default: `SESSION`."
  레퍼런스에 `serializer.setCookieName("JSESSIONID")` 예제가 있는데 그것은 **커스터마이즈
  예제**다. 기본값으로 착각하기 쉽다.
- `sameSite` **기본값 `Lax`**. `null`로 두면 디렉티브 자체를 내보내지 않는다.
- `maxAge` 기본 `-1` (브라우저 닫으면 사라짐).

→ **8장에 그대로 쓴다**: 세션 저장소를 Redis로 옮기면 애플리케이션 코드는 거의 안 바뀌지만
**쿠키 이름이 바뀐다.** 배포 직후 전원이 로그아웃되는 것처럼 보이는 실제 원인이 된다.

---

## V4 · 세션 고정 방어 — **확인됨**

출처: [Session Management](https://docs.spring.io/spring-security/reference/6.5/servlet/authentication/session-management.html)

세 전략이 있다.

| 전략 | 동작 | 기본값 |
|---|---|---|
| `changeSessionId` | 서블릿 컨테이너의 방어를 사용 | **Servlet 3.1+ 기본** |
| `newSession` | 새 세션 생성, Spring Security 속성만 복사 | |
| `migrateSession` | 새 세션 생성, **모든** 속성 복사 | Servlet 3.0 이하 기본 |

방어를 끄는 것은 권장되지 않는다. 현대 컨테이너는 전부 3.1+이므로 5장에서는
**`changeSessionId`가 사실상의 기본**이라고 쓴다.

---

## V5 · Tomcat 세션 복제 — **확인됨 · 8장 데모의 근거**

출처: [Tomcat 10.1 Clustering/Session Replication How-To](https://tomcat.apache.org/tomcat-10.1-doc/cluster-howto.html)

**`DeltaManager` — all-to-all**
> "By all-to-all, we mean that _every_ session gets replicated to _all the other nodes_ in the cluster."
> "Tomcat will replicate sessions to _all_ nodes, _even nodes that don't have the application deployed_."

**`BackupManager` — 백업 1개**
> "The `BackupManager` only replicates the session data to _one_ backup node, and only to nodes that
> have the application deployed."

**실용 한계 — 공식 수치가 있다**
> "This works great for smaller clusters, but we don't recommend it for larger clusters —
> **more than 4 nodes or so.**"
> "Once you have a simple cluster running with the `DeltaManager`, you will probably want to migrate
> to the `BackupManager` as you increase the number of nodes in your cluster."

→ 8장 데모에서 **"4대"라는 수치를 쓸 수 있다.** 다만 이것은 Tomcat 문서의 권고치이지 물리
법칙이 아니다. 데모는 "복제 대상 수가 노드 수에 따라 어떻게 늘어나는지"의 **구조**를 보이는
데 쓰고, 대역폭이나 지연의 절대 수치는 지어내지 않는다.

부가로 확인된, 문서에 쓸 만한 사실: DeltaManager는 **앱이 배포되지도 않은 노드에까지** 복제한다.
낭비의 성격을 한 줄로 보여 주는 좋은 예다.

---

## V6 · 브라우저의 `SameSite`·`HttpOnly`·`Secure` — **확인됨**

출처: [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)

- **미지정 시 기본값은 브라우저마다 다르다.**
  > "**Some browsers** use `Lax` as the default value if `SameSite` is not specified"

  → "요즘 브라우저는 전부 Lax가 기본"이라고 **단정하지 않는다.** 흔한 오서술이다.
- **기본으로 적용된 `Lax`는 명시한 `Lax`보다 느슨하다.**
  > "When `Lax` is applied as a default, a more permissive version is used. In this more permissive
  > version, cookies are also included in `POST` requests, as long as they were set no more than
  > **two minutes** before the request was made."

  → 6장 CSRF에서 중요하다. "SameSite 기본값이 있으니 CSRF는 끝났다"가 왜 틀린지의 근거다.
- `SameSite=None`은 **`Secure`가 필수**다.
- `Strict`: 쿠키를 설정한 것과 같은 사이트에서 온 요청에만 전송.
- `Lax`: 같은 사이트 + **최상위 내비게이션이면서 안전한 메서드**인 교차 사이트 요청.
- `HttpOnly`: JS의 `document.cookie` 접근 차단 → XSS 완화.
- `Secure`: `https:` 요청에만 전송. **단 localhost는 예외.**

### V6 보강 — "같은 사이트"란 무엇인가 (2026-08-14, 3~4장 구현 중 추가 확인)

4장 구현자가 `Domain` 시나리오를 판정하려면 `shop.example.com` ↔ `api.example.com`이 같은
사이트인지 정해야 했는데 V6에 근거가 없어, **정의를 한 줄만 쓰고 정확한 규칙은 6장으로
미뤄 두었다.** 올바른 처리였다. 확인해서 보강한다.

출처: [MDN Glossary — Site](https://developer.mozilla.org/en-US/docs/Glossary/Site)

> "a site is determined by the **registrable domain** portion of the domain name. The registrable
> domain consists of an entry in the Public Suffix List plus the portion of the domain name just
> before it." (= **eTLD+1**)

| 요소 | 사이트 구분에 영향? | 근거 |
|---|---|---|
| 등록 가능 도메인(eTLD+1) | **그렇다** | 이것이 정의다 |
| 서브도메인 | **아니다** | "`support.mozilla.org` and `developer.mozilla.org` are part of the same site" |
| 포트 | **아니다** | "the port number is ignored when determining the site" |
| 스킴(http/https) | **`SameSite` 쿠키에서는 그렇다** | 아래 참조 |

**스킴이 걸리는 것이 중요하다.** 일반적인 "사이트" 정의는 스킴을 안 보지만, 스킴까지 보는
더 엄격한 정의를 *schemeful same-site*라고 부르고 —

> "This stricter definition is applied in the rules for handling `SameSite` cookies."

즉 `http://example.com`과 `https://example.com`은 **`SameSite` 판정에서는 서로 다른 사이트다.**

→ **4장의 "도메인을 등록한 단위가 같으면 된다"는 서술은 맞다.** 6장에서 규칙을 정확히 풀 때
포트 무시와 **schemeful same-site**를 함께 쓴다. 후자는 `Secure`의 localhost 예외와 묶어
"로컬에선 되는데 배포하면 안 된다"의 또 다른 원인으로 설명할 수 있다.

---

## V7 · Spring Security의 CSRF 기본값 — **확인됨**

출처: [CSRF](https://docs.spring.io/spring-security/reference/6.5/servlet/exploits/csrf.html),
[네임스페이스 부록](https://docs.spring.io/spring-security/reference/6.5/servlet/appendix/namespace/http.html)

- `@EnableWebSecurity` 사용 시 **기본 활성**이다. 별도 코드가 필요 없다.
- **서블릿(MVC)의 보호 대상**: 기본 매처가 **`GET`·`TRACE`·`HEAD`·`OPTIONS`를 제외한** 메서드.
- **리액티브(WebFlux)의 보호 대상**: 기본 매처가 **`PUT`·`POST`·`DELETE`**.
  → 둘이 다르다. 6장에서 뭉뚱그리지 말 것.
- 토큰 저장소 기본값: 서블릿 `HttpSessionCsrfTokenRepository`, 리액티브
  `WebSessionServerCsrfTokenRepository`.
- `disable()`에 대한 공식 표현:
  > "Only recommended if the application is never used within a browser."
  → 6장의 "`csrf().disable()`이 언제 정당한가"에 이 문장을 근거로 쓴다.

---

## V8 · `alg: none` — **부분 확인 · 서술 범위를 좁힌다**

- 공격의 원리는 확인됐다: 헤더의 `alg`를 `none`으로 바꾸고 서명을 지우면, **검증할 알고리즘을
  공격자가 고르는 것**이 되어 검증 자체가 일어나지 않는다.
- 방어의 원칙도 확인됐다: **서버가 기대하는 알고리즘을 화이트리스트로 고정**하고, 토큰이
  주장하는 `alg`를 신뢰하지 않는다.
- 여전히 살아 있는 문제군이다. 최근에도 관련 취약점이 보고된다.

### 확정하지 못한 것 — 서술 제한

- CVE-2015-9235가 `alg:none`인지 **알고리즘 혼동(RS256→HS256)**인지 자료마다 설명이 엇갈린다.
  **CVE 번호를 본문에 쓰지 않는다.**
- 확인된 라이브러리 사례는 전부 JVM 밖이다 (npm `jsonwebtoken` 9.0.0에서 `none` 기본 지원
  제거, `python-jose` ≤3.3.0이 `alg=none`을 수용). **JVM 라이브러리별 현황은 확인하지 못했다.**

→ **10장 서술 제한**: 특정 라이브러리·버전·CVE 번호를 지목하지 않는다. **공격의 원리와
방어 원칙(알고리즘을 서버가 고정한다)만 쓴다.** 데모는 실제 라이브러리 동작이 아니라
"검증자가 헤더를 믿으면 무슨 일이 생기는가"를 보인다.

---

## 이번 검증에서 얻은 것

1. **요약본과 원문이 정반대일 수 있다** (V1). 결론이 문서의 다른 서술과 어긋나 보이면
   마이그레이션 가이드나 릴리스 노트 같은 **1차 원문으로 교차 확인**한다.
2. **커스터마이즈 예제를 기본값으로 착각하기 쉽다** (V3). 예제 코드에 적힌 값은 기본값이 아니다.
3. **확인 못 한 것은 뭉개지 말고 범위를 좁힌다** (V1 후반, V8). 지난 문서의 교훈대로,
   "불확실하면 완화"가 아니라 **"확인한 뒤 유지하거나, 아예 쓰지 않는다"**로 처리했다.
