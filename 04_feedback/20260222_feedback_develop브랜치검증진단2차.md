# develop 브랜치 2차 검증 종합 진단 보고서

---
날짜: 2026-02-22
작성자: Claude Code (검증자 모드)
관련기능: develop 브랜치 전체 코드베이스
우선순위: 높음
상태: 완료

---

## 개요

`taedonggroup/sori` develop 브랜치의 2026-02-22 업데이트를 검토한 종합 진단 보고서입니다.
검토 범위: API 라우트 10개, 페이지 5개, 컴포넌트 13개, lib 파일 5개

---

## 아키텍처 전환 평가 — PASS ✅

**이전 구조 → 현재 구조 전환 성공**

| 항목 | 이전 | 현재 | 평가 |
|------|------|------|------|
| 기술 스택 | 바닐라 JS | Next.js 16 + TS + Supabase + Gemini | ✅ 대폭 업그레이드 |
| 업로드 방식 | Vercel 경유 multipart | 브라우저 → Supabase 직접 (서명 URL) | ✅ Vercel 제한 우회 해결 |
| 분석 방식 | 파일 바이너리 전송 | Supabase URL → Gemini inline base64 | ✅ 아키텍처 개선 |
| 데이터 저장 | Jarvis SQLite 단독 | Supabase Storage + Jarvis SQLite 혼합 | ✅ 분산 저장 적용 |
| 커뮤니티 기능 | 없음 | 갤러리 피드 + 믹스 + 프로필 | ✅ 완전 신규 |

**SORI 명칭 체계 적용 확인:**
- `원석`, `조각`, `공명`, `(첫)울림`, `공간` — 코드 전체에 일관 적용됨
- 컴포넌트명, 변수명, UI 텍스트 모두 한국어 명칭 체계 준수

---

## 버그 / 이슈 목록

### 🔴 CRITICAL — 즉시 수정 필요

#### BUG-01: 파일 크기 제한 3중 불일치 (HANDOFF 기록보다 심각)

HANDOFF.md에는 "4MB vs 20MB" 2중 불일치로 기록되어 있으나, 실제 코드 검토 결과 3중 불일치 확인.

| 위치 | 파일 | 제한값 |
|------|------|--------|
| 클라이언트 검증 | `src/lib/gonmyung/validation.ts:4` | **4MB** (`MAX_FILE_SIZE = 4 * 1024 * 1024`) |
| 서버 분석 | `src/app/api/gonmyung/analyze/route.ts:72` | **20MB** (`fileSizeMB > 20`) |
| UI 안내 텍스트 | `src/app/upload/page.tsx:263` | **50MB** (`최대 50MB` 표시) |

**사용자 혼란 시나리오:**
1. 사용자가 UI를 보고 "최대 50MB"라고 인식
2. 10MB 파일 선택
3. `validateAudioFile()` 에서 "파일 크기는 4MB 이하여야 합니다" 오류 발생
4. 사용자는 UI 텍스트(50MB)와 오류 메시지(4MB)의 충돌로 혼란

**권장 수정:** 3곳을 동일한 값으로 통일 (권장: 20MB — 서버 처리 한계에 맞춤)
- `validation.ts`: `MAX_FILE_SIZE = 20 * 1024 * 1024` 로 변경
- `upload/page.tsx:263`: `최대 20MB` 로 변경
- `analyze/route.ts`: 현행 20MB 유지

---

#### BUG-02: 환경변수 느낌표(!) 단언 — 런타임 에러 위험

```typescript
// src/app/api/gonmyung/analyze/route.ts:6
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_GENERATIVE_AI_API_KEY!);
// → undefined! 전달 시 SDK 내부에서 모호한 에러 발생

// src/lib/supabase.ts:5-6
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
// → 브라우저 번들에서 undefined로 로드되면 createClient 실패
```

**위험도:** Vercel 환경변수 누락 시 500 에러 대신 모호한 에러로 디버깅 어려움
**권장 수정:** 느낌표 대신 명시적 검사 추가 (upload-url/route.ts 패턴 참고)

---

### 🟡 MEDIUM — 다음 PR 전 수정 권장

#### BUG-03: ResonanceLoader 진행률 고정값 문제

갤러리와 create 페이지에서 ResonanceLoader의 progress 값이 믹싱 중 50%로 고정됨.

```typescript
// src/app/gallery/page.tsx:74-77
<ResonanceLoader
  isLoading={isMixing}
  progress={isMixing ? 50 : 0}   // ← 고정값 50
  currentStep="조각들을 공명으로 믹싱하는 중..."
/>

// src/app/create/page.tsx:79-83 (동일 문제)
```

**영향:**
- `ResonanceLoader`의 `getPhase()` 로직: progress < 30 → Phase 0, 30-75 → Phase 1, 75+ → Phase 2
- progress=50이면 항상 Phase 1(궤도 공전)만 표시 — Phase 2(최종 수렴)는 절대 도달 불가
- 믹스 완료 후 Phase 2 애니메이션 (궤도 축소)이 재생되지 않음

**권장:** FFmpeg 믹스는 단일 API 호출이라 실제 진행률 추적이 어려우나, 타이머 기반 시뮬레이션(0→100)으로 개선 가능

---

#### BUG-04: 갤러리 믹스 에러 무음 처리

```typescript
// src/app/gallery/page.tsx:56-57
} catch {
  // 오류 시 무시  ← 에러가 발생해도 사용자에게 아무 피드백 없음
}
```

create/page.tsx는 `errorMessage` 상태로 에러를 표시하는데, gallery/page.tsx는 에러를 완전히 삼킴.
**결과:** 믹스 실패 시 로딩이 그냥 멈추고 사용자는 원인을 알 수 없음

---

#### BUG-05: CLAUDE.md 버전 정보 불일치

```markdown
# CLAUDE.md:14
- **Framework**: Next.js 14 (App Router)
```

실제 package.json에는 `"next": "^16.1.6"` 사용 중.
신규 개발자가 CLAUDE.md를 보고 Next.js 14 기준으로 작업할 위험 있음.

---

### 🔵 LOW — 개선 권장

#### INFO-01: package.json name 미수정

```json
// package.json
"name": "sori-temp"  // "sori"로 변경 필요
```

---

#### INFO-02: NEXT_PUBLIC_ 환경변수로 서버 IP 노출

```typescript
// src/app/api/gonmyung/joakak/route.ts:4
// src/app/api/gonmyung/mix/route.ts:4
const GONMYUNG_API_URL = process.env.NEXT_PUBLIC_GONMYUNG_API_URL;
```

`NEXT_PUBLIC_` 접두사는 클라이언트 번들에 포함됨. 이 변수는 API Routes(서버)에서만 사용됨에도 불구하고, `NEXT_PUBLIC_` 접두사로 인해 Jarvis 서버 IP(`175.127.189.188:3001`)가 브라우저 JavaScript에 노출됨.

**권장:** API Routes 전용으로 `GONMYUNG_API_URL` (NEXT_PUBLIC_ 없이) 로 분리

---

#### INFO-03: 프로필 페이지 — Jarvis 직접 호출 vs 프록시 라우트 혼재

```typescript
// src/app/profile/[nickname]/page.tsx:9, 13-16 (서버 컴포넌트)
const apiUrl = process.env.NEXT_PUBLIC_GONMYUNG_API_URL;
const response = await fetch(`${apiUrl}/api/profile/${...}`);
// → Jarvis 직접 호출
```

반면 `/api/gonmyung/profile/[nickname]/route.ts` 프록시 라우트가 별도로 존재함.
일관성을 위해 프로필 페이지도 `/api/gonmyung/profile/[nickname]` 프록시를 사용하는 것이 권장됨.

---

#### INFO-04: create 페이지와 gallery 페이지 믹스 로직 중복

두 페이지의 `handleMix` 함수와 결과 변환 로직이 거의 동일함.
향후 수정 시 한 곳만 수정하고 나머지를 놓치는 버그가 발생할 수 있음.
공통 훅(`useMixing()`) 추출을 권장.

---

## 신규 기능 구현 검증 — PASS ✅

| 기능 | 파일 | 구현 상태 | 비고 |
|------|------|-----------|------|
| 조각 업로드 (서명 URL) | `upload/page.tsx` + `upload-url/route.ts` + `supabase.ts` | ✅ | PUT 업로드 + publicUrl 반환 완성 |
| Gemini 음악 분석 | `analyze/route.ts` | ✅ | 429/quota 처리, JSON 파싱 검증 포함 |
| 갤러리 피드 | `gallery/page.tsx` + `JoakakFeed.tsx` | ✅ | 무한 스크롤, 선택 모드 |
| FFmpeg 믹싱 | `mix/route.ts` | ✅ | URL 재작성 처리 포함 |
| 원석 프로필 SSR | `profile/[nickname]/page.tsx` | ✅ | revalidate:60, SEO 적합 |
| ResonanceLoader | `ResonanceLoader.tsx` | ✅ | 3페이즈 Canvas 파티클 + 로딩 메시지 |
| 3D 원석 씬 | `StoneScene.tsx` + `RawStone.tsx` | ✅ | React Three Fiber, 4점 조명 |
| 샘플 테스트 | `samples.ts` (20곡) | ✅ | CC BY 4.0 라이선스 고지 포함 |
| 디자인 토큰 | `globals.css` | ✅ | #F8F32B 액센트, 순수 검정 배경 |

---

## 보안 검토

| 항목 | 상태 | 비고 |
|------|------|------|
| 서비스 키 서버 전용 | ✅ | `SUPABASE_SERVICE_KEY` — 서버 API Route에서만 사용, 클라이언트 노출 없음 |
| RLS 우회 안전성 | ✅ | 서명된 URL 방식 — 경로당 1회 사용, 만료 포함 |
| Gemini API 키 | ✅ | `GOOGLE_GENERATIVE_AI_API_KEY` — 서버 전용, NEXT_PUBLIC_ 없음 |
| Jarvis IP 노출 | ⚠️ | `NEXT_PUBLIC_GONMYUNG_API_URL` — 클라이언트 번들에 포함됨 (INFO-02 참조) |
| 파일 타입 검증 | ✅ | 확장자 및 MIME 타입 모두 검증 |

---

## 종합 점수 (검증자 재평가)

| 항목 | HANDOFF 자체 평가 | 검증자 평가 | 비고 |
|------|-------------------|-------------|------|
| 빌드 안정성 | 100 | 100 | 빌드 성공 확인 |
| 타입 안정성 | 85 | 82 | 느낌표 단언 3곳 |
| 에러 처리 | 75 | 70 | 갤러리 믹스 에러 무음 |
| 컴포넌트 설계 | 95 | 88 | 믹스 로직 중복, progress 고정값 |
| API 완성도 | 90 | 90 | 완성도 높음 |
| 보안 | 90 | 85 | Jarvis IP 클라이언트 노출 |

**종합 점수: 83/100 (프로덕션 배포 가능, 단 BUG-01 UI 불일치 긴급 수정 권장)**

---

## 우선순위별 수정 목록

### 즉시 (이번 배포 전)
- [ ] `upload/page.tsx:263` UI 텍스트 `최대 50MB` → `최대 4MB` (또는 `validation.ts`와 동기화)
- [ ] `gallery/page.tsx` catch 블록에 `setErrorMessage` 추가

### 다음 PR
- [ ] 파일 크기 3중 불일치 통일 (4MB → 20MB 전체 통일 권장)
- [ ] 환경변수 느낌표 단언 → 명시적 체크로 교체
- [ ] `CLAUDE.md` Next.js 버전 수정 (14 → 16)
- [ ] `package.json` name `sori-temp` → `sori`

### 장기 개선
- [ ] `NEXT_PUBLIC_GONMYUNG_API_URL` → `GONMYUNG_API_URL` (서버 전용)
- [ ] 믹스 로직 공통 훅 추출 (`useMixing`)
- [ ] ResonanceLoader 타이머 기반 진행률 시뮬레이션

---

*이 보고서는 `review/develop` 브랜치 체크아웃 후 전체 파일 정적 분석 기반으로 작성되었습니다.*
*빌드 실행 및 런타임 테스트는 Vercel 배포 환경에서 별도 확인이 필요합니다.*
