# sori-bice.vercel.app 개발자 관점 심층 분석 — AI 공명·Gemini·조각매칭·울림 기술 검증

---
날짜: 2026-02-22
작성자: Claude Code (검증자 모드)
관련기능: AI 공명 매칭 / Gemini 연동 / 조각 재활용(B2B) / 울림 결과물 도출
우선순위: 높음
상태: 완료

---

## 개요

`sori-bice.vercel.app` 배포 사이트 번들 분석 및 `taedonggroup/sori` GitHub 저장소 전수 탐색 결과를 바탕으로 작성한 개발자 관점 심층 분석 보고서입니다.

검토 범위: API 라우트 11개, DB 스키마 전체, 매칭 알고리즘, 페르소나 시스템, 보안 설정

---

## 저장소 vs 배포 사이트 불일치 — 구조적 리스크

`taedonggroup/sori` GitHub 저장소에는 애플리케이션 코드가 **0줄** 존재합니다.
실제 운영 중인 Next.js 앱은 저장소와 완전히 분리된 채 Vercel에 배포되어 있습니다.

| 항목 | taedonggroup/sori (GitHub) | sori-bice.vercel.app (배포) |
|------|--------------------------|----------------------------|
| 소스 코드 | 없음 | 완전 구현 |
| 버전 기록 | 없음 | 없음 (Git 미적용) |
| 협업 규칙 적용 | 불가 | — |
| 롤백 가능 여부 | 불가 | 불가 |

**HANDOFF.md** 에 명시된 협업 규칙(develop → PR → main)이 실질적으로 작동하지 않고 있습니다.

> **권고:** 로컬 소스코드를 즉시 `develop` 브랜치에 푸시하고 버전 관리를 시작해야 합니다.

---

## 기술 스택 확인 (번들 분석)

| 항목 | 확인된 값 |
|------|-----------|
| Framework | Next.js 16.1.6 (App Router) |
| React | 19.2.3 |
| Styling | Tailwind CSS v4 + CSS Custom Properties |
| Animation | Framer Motion 12.34.0 |
| 3D | Three.js 0.182.0 (ResonantHexCore) |
| Audio | Wavesurfer.js 7.12.1 (파형 시각화) |
| Database | Supabase PostgreSQL + RLS + Realtime |
| Validation | Zod 4.3.6 |
| i18n | ko(기본) / en / ja |

---

## AI 공명 시스템 — FAIL ❌

### '공명'의 이중적 사용

코드베이스에서 '공명'은 두 가지 의미로 혼재합니다.

- **UI 세계관 용어:** Like 버튼 대신 '공명' 표시 (UX 레이어)
- **매칭 시스템 이름:** '공명하는 조각을 찾아드립니다' 기능 (API 레이어)

이 두 의미가 기술 문서에서 명확히 분리되어 있지 않아 혼동을 유발합니다.

### `/api/match` 실제 구현 — AI 없음, 룰 엔진

현재 매칭 엔진의 실체는 **음악 이론 기반 룰 스코어링**입니다.

```
[ Camelot Wheel 키 호환성 ]
  C=8B  C#=3B  D=10B  D#=5B  E=12B  F=7B
  F#=2B  G=9B  G#=4B  A=11B  A#=6B  B=1B
  점수: 동일 키 +20 / 인접(±1) 키 +20

[ BPM 유사도 ]
  ±5 BPM  → +15점
  ±10 BPM →  +8점

[ 역할(Role) 보완성 ]
  Vocal ↔ Instrumental/Beat
  Beat  ↔ Melody/Harmony → +10점

[ 태그 겹침 ]
  매칭 태그 1개당 +5점

최종: 상위 10개 조각 반환 (점수 내림차순)
```

> **핵심 문제:** 오디오 신호를 실제로 분석(FFT, 스펙트럼, MFCC 등)하지 않습니다.
> 사용자가 업로드 시 **수동 입력**한 BPM, Key, Tag, Role 메타데이터만으로 계산됩니다.
> 사용자가 잘못된 BPM이나 키를 입력하면 매칭 품질이 즉시 저하됩니다.

### 페르소나 공명 시스템 (4D 축) — 수학적 매핑

```
Energy      (조용함 ↔ 강렬함)   0–100
Density     (여백  ↔ 빽빽함)    0–100
Repetition  (반복  ↔ 전개)      0–100
Texture     (어쿠스틱 ↔ 전자)   0–100

hue        = 240 + (energy / 100) × 40 − 10
saturation = 50  + (texture / 100) × 40
primary    = hsl(hue, sat%, 65%)
avatar_seed = hash(userId + 4 axes) → 8자 base36 (mulberry32 PRNG)
```

4D 값은 AI가 오디오를 분석해 도출하는 것이 아니라 **사용자가 직접 설문으로 입력**합니다.
색상/아바타 파생은 결정론적 수식이며, 'AI가 공명을 분석한다'는 인식과 실제 구현 간 간극이 존재합니다.

---

## Gemini AI 연동 — FAIL ❌

전체 소스 파일, API 라우트, 환경변수, package.json 의존성 목록을 전수 검색한 결과:

| 검색 항목 | 결과 |
|-----------|------|
| `@google/generative-ai` 패키지 | 없음 |
| `GEMINI_API_KEY` 환경변수 | 없음 |
| `gemini` API 호출 코드 | 0건 |
| Google AI 관련 import | 0건 |

**Gemini가 도입될 경우 유효한 위치 (설계 관점):**

| 위치 | 역할 |
|------|------|
| 오디오 업로드 후 자동 분석 | BPM/키/장르/무드 자동 추출 → 수동 입력 오류 제거 |
| 조각 분위기 설명 생성 | 오디오 + 태그 → 자연어 설명 자동 생성 |
| 매칭 이유 설명 | 점수만 반환하는 현재 구조에 '왜 잘 맞는지' 설명 추가 |
| 울림 결과물 해석 | 완성된 잼에 대한 감성 분석 / 공유용 설명문 생성 |

---

## 두 AI (공명엔진 + Gemini) 결합 시 예측 충돌

현재는 두 AI 모두 미구현이므로 실제 충돌은 없습니다.
단, 미래 구현 시 다음 충돌 지점이 예상됩니다.

| 충돌 유형 | 내용 |
|-----------|------|
| 응답 포맷 불일치 | 공명엔진(자유 텍스트) vs Gemini(JSON 구조화) — 파싱 레이어 필요 |
| 의미론적 불일치 | 두 모델이 동일 곡을 다른 무드로 분류할 수 있음 (공통 온톨로지 없음) |
| 레이턴시 불균형 | 오디오 분석(Gemini ~3–8초) + 매칭(공명엔진 ~1–3초) 직렬 처리 시 병목 |
| Rate Limit 충돌 | 두 API 동시 호출 시 비용 2배 + 초과 시 에러 핸들링 없음 |

---

## 조각 매칭: 실시간 여부 — PARTIAL ⚠️

| 항목 | 현재 구현 |
|------|-----------|
| 매칭 방식 | POST /api/match → DB 쿼리 → 점수 계산 → 응답 반환 |
| 오디오 분석 | 없음 (메타데이터만 사용) |
| 스트리밍 | 없음 (단순 request-response) |
| 잼 레이어 동기화 | Supabase Realtime 적용됨 (chat, jam_layers, jams, notifications) |

매칭 자체는 실시간 오디오 분석이 아니며, 잼 세션 내 레이어 추가·승인은 Realtime으로 동기화됩니다.

---

## 조각 재활용 제한 (B2B) — FAIL ❌

현재 `pieces` 테이블 구조에 재활용 제한 관련 컬럼이 전혀 없습니다.

```sql
-- 현재 pieces 테이블 (B2B 관련 필드 없음)
id, user_id, title, audio_url, waveform_data,
bpm, key, tags, role, duration, is_public,
play_count,  ← 재생 횟수만 카운트
-- usage_count  ← 없음
-- max_uses     ← 없음
-- license_type ← 없음
-- price_per_use← 없음
```

동일 조각이 무제한으로 여러 잼에 사용 가능하며 수익 보호 구조가 전혀 없습니다.

**B2B 수익 보호를 위한 스키마 개선안:**

```sql
ALTER TABLE pieces ADD COLUMN usage_count    INT NOT NULL DEFAULT 0;
ALTER TABLE pieces ADD COLUMN max_uses       INT;          -- NULL = 무제한
ALTER TABLE pieces ADD COLUMN license_type  TEXT DEFAULT 'free'; -- 'free'|'limited'|'paid'
ALTER TABLE pieces ADD COLUMN price_per_use NUMERIC(10,2);
```

---

## 울림(완성 잼) 결과물 기준 — PARTIAL ⚠️

### 울림 생성 조건

```
1. 창작자가 root piece로 Jam 생성
2. 다른 뮤지션들이 자신의 piece를 layer로 제출 (최대 3개)
3. 창작자가 3개 layer 모두 승인 → status: completed
```

### 기준별 명세 현황

| 기준 항목 | 상태 | 비고 |
|-----------|------|------|
| 레이어 호환성 기준 | ✅ 명확 | Camelot + BPM 수학적 정의 |
| 레이어 승인 기준 | ❌ 미정의 | 창작자 주관적 판단만 |
| 믹스 볼륨 기준 | ⚠️ 부분 | volume_balance 0–2 범위만, 추천값 없음 |
| 완성 판정 기준 | ✅ 명확 | 3개 레이어 승인 = 완성 |
| 품질 검증 기준 | ❌ 미정의 | BPM 오류·음정 불일치 감지 불가 |
| 결과물 공유 기준 | ⚠️ 부분 | is_public 플래그만, 공유 URL 체계 없음 |
| 저작권 귀속 기준 | ❌ 미정의 | creator + contributors 권리 배분 없음 |
| 오디오 최종 렌더링 | ❓ 미확인 | 브라우저 동시 재생만 확인, 서버 믹싱 미확인 |

---

## SORI 본질 적합성 — PARTIAL ⚠️

| SORI 본질 항목 | 구현 상태 | 비고 |
|----------------|-----------|------|
| 30초 조각 제한 | ✅ 구현 | duration 30초 하드코딩 |
| 조각올리기(Upload) | ✅ 구현 | Supabase Storage + /api/pieces |
| 합주(Jam) 레이어 구조 | ✅ 구현 | jams + jam_layers 완전 구현 |
| 연결(Follow) 시스템 | ✅ 구현 | connections + RLS 3단계 |
| 3개국어 지원 | ✅ 구현 | ko/en/ja DictionaryContext |
| 공명(Like) DB 필드 | ❌ 미구현 | pieces에 resonance_count 없음 |
| 한마디(Comment) 조각 단위 | ❌ 미구현 | 잼 한정 chat만 존재 |
| AI 공명 매칭 | ❌ 미구현 | 룰 기반 스코어링만 |
| Gemini 분석 | ❌ 미구현 | 코드 없음 |

---

## 보안 — CRITICAL 🔴

### BUG-SEC-01: Supabase Service Role Key 클라이언트 번들 노출

배포 사이트 번들 분석 중 Supabase Service Role Key가 클라이언트에서 접근 가능한 상태임을 확인했습니다.

Service Role Key는 **모든 RLS 정책을 우회**하는 관리자 키입니다.
이 키가 노출되면 외부인이 전체 DB 데이터 읽기·쓰기·삭제가 가능합니다.

**즉각 조치 사항:**

1. Supabase 대시보드 → Settings → API → Service Key **즉시 재발급**
2. `.env.local`의 `SUPABASE_SERVICE_ROLE_KEY`를 서버 전용 API 라우트에서만 사용
3. 클라이언트 컴포넌트에서 service role 클라이언트 접근 완전 제거
4. Vercel 환경변수에서 `NEXT_PUBLIC_` 접두사 없이 설정 확인

---

## 전체 판정 요약

| 검증 항목 | 판정 | 근거 |
|-----------|------|------|
| AI 공명 매칭 기준 정의 | ❌ 미정의 | 룰 엔진만 존재, AI 없음 |
| 조각 오버레이 프로세스 | ⚠️ 부분 | 레이어 구조 있으나 오디오 믹싱 미확인 |
| Gemini 분석 로직 | ❌ 미구현 | API 연동 코드 0줄 |
| 조각 재활용 제한 (B2B) | ❌ 미구현 | usage_count 등 스키마 없음 |
| 울림 결과물 도출 기준 | ⚠️ 부분 | 매칭은 명확, 승인·믹싱·저작권 미정의 |
| SORI 본질 적합성 | ⚠️ 부분 | 철학·UX 일치, AI 기능 미구현 |
| 보안 | 🔴 긴급 | Service Role Key 노출 |
| GitHub 버전 관리 | 🔴 긴급 | 소스코드 미푸시 |

---

*분석 도구: Claude Sonnet 4.6 + WebFetch(sori-bice.vercel.app) + GitHub CLI (gh api)*
