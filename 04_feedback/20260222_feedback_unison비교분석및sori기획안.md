# unison-kappa 비교 분석 및 sori-bice 적용 기획안

---
날짜: 2026-02-22
작성자: Claude Code (검증자 모드)
관련기능: 전체 서비스 기획 — 두 배포 사이트 비교 및 통합 적용안
우선순위: 높음
상태: 완료

---

## 개요

`unison-kappa.vercel.app` (구 테스트 서버)와 `sori-bice.vercel.app` (현 본 서버)를
개발자 관점에서 전수 비교 분석하고, unison에서 계승해야 할 요소와
sori-bice에 신규 적용할 기획안을 도출한 문서입니다.

---

## 1. 두 사이트 핵심 비교

### 기술 스택 차이

| 항목 | unison-kappa (구) | sori-bice (현) | 방향 |
|------|------------------|----------------|------|
| 3D 비주얼 | 없음 | Three.js ResonantHexCore (WebGL + Bloom) | 현재가 우위 |
| 배경 효과 | SVG 필터 노이즈 텍스처 (grain) | Canvas 파티클 50개 | **둘 다 필요** |
| 파형 바 수 | 24개 (단순) | 48–64개 (고밀도) | 현재가 우위 |
| 카드 디자인 | 라운드 코너 16px | Hex-corner 클립패스 (8각형) | 현재가 우위 |
| 타이포그래피 | clamp(2rem, 5vw, 3rem) | clamp(2.5rem, 6vw, 4.5rem) | 현재가 우위 |
| 섹션 진입 애니 | section-reveal 키프레임 | fade+slide (framer) | **구가 더 가볍고 재사용 용이** |
| 빈 상태 아이콘 | 4s 숨쉬기 애니 | 정적 | **구가 우위** |

### 디자인 시스템 차이

| 항목 | unison-kappa | sori-bice |
|------|-------------|-----------|
| 기본 배경 | `#0f0f14` | `#0B0B0F` (더 진한 검정) |
| 카드 배경 | `#1e1e26` | `#1A1A1F` |
| 보조 색상 | cyan `#00e0ff` | cyan `#00F5FF` (더 밝음) |
| 시맨틱 컬러 | 없음 | success/warning/error/info 완비 |
| 필름 그레인 | ✅ 노이즈 오버레이 (opacity 0.018) | ❌ 없음 |
| 원형 처리 | `border-radius: 3.40282e38px` CSS 트릭 | 표준 `9999px` |

---

## 2. unison-kappa에서 계승해야 할 요소

### 2-1. 필름 그레인 노이즈 오버레이 ⭐ 즉시 도입 권장

unison-kappa는 SVG 필터 기반 노이즈 텍스처를 고정 캔버스 레이어로 사용합니다.
이 효과가 sori-bice에서 사라지면서 **고급스러운 인화지 질감**이 제거됐습니다.

```css
/* unison-kappa 구현 방식 */
.grain-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.018;
  z-index: 1000;
  background-image: url("data:image/svg+xml,..."); /* SVG noise */
}
```

- 파티클 배경(sori-bice)은 동적이고 화려하지만 grain은 **정적이고 미묘한 깊이감**을 줍니다.
- 두 효과는 충돌하지 않으며 레이어로 공존 가능합니다.
- **모바일에서 자동 비활성화**하는 조건부 렌더링 포함 권장.

---

### 2-2. 프로필 — Gear 탭 ⭐⭐ 핵심 B2B 기능

unison-kappa의 프로필에는 **Gear 탭**이 존재합니다.
사용자가 자신이 보유한 악기, DAW, 장비를 등록하는 기능입니다.

현재 sori-bice의 users 테이블에는 `gear_closet JSONB[]` 컬럼이 이미 존재하지만
프론트엔드 UI가 구현되지 않은 상태입니다.

```sql
-- DB는 준비됨 (미구현)
gear_closet JSONB[]  -- [{ name, type, brand, year }]
```

**기획 확장 포인트:**
- Gear 등록 → 장비 기반 협업자 검색 (같은 DAW, 같은 악기)
- B2B: 악기 브랜드와 제휴 시 "이 사용자가 사용하는 장비" 데이터 활용
- 뮤지션이 자신의 셋업을 공유하는 커뮤니티 문화 형성

---

### 2-3. 프로필 — Availability 탭 ⭐⭐ 실시간 협업 스케줄링

unison-kappa 프로필의 **Availability 탭**은 사용자가 협업 가능한 시간대를 등록하는 기능입니다.
users 테이블에 `availability_schedule JSONB[]`가 이미 준비되어 있습니다.

```sql
-- DB는 준비됨 (미구현)
availability_schedule JSONB[]  -- [{ day, start, end, timezone }]
```

**기획 확장 포인트:**
- 협업 매칭 시 "지금 가능한 사람"만 필터링
- 실시간 온라인 상태 + 스케줄 결합 → 즉각 잼 세션 제안
- 타임존 기반 글로벌 협업 (ko/en/ja 3국어 이미 지원)

---

### 2-4. 프로필 — "Tracks Made Together" 탭

unison-kappa는 **함께 만든 트랙** 전용 탭이 프로필에 존재합니다.
sori-bice는 "My Pieces" 탭만 있어 **협업 결과물이 묻힙니다**.

completed 상태의 jam에서 해당 유저가 레이어를 기여한 경우를
별도 탭으로 집계해 보여주는 기능입니다.

```sql
-- 필요한 쿼리
SELECT j.*, jl.* FROM jams j
JOIN jam_layers jl ON j.id = jl.jam_id
WHERE jl.user_id = $userId
AND j.status = 'completed'
ORDER BY j.updated_at DESC;
```

---

### 2-5. 대시보드 "Today's Line" 에디터블 필드

unison-kappa는 대시보드 상단에 **오늘의 한 줄** 인라인 편집 필드가 있습니다.
사용자가 그날의 음악적 감정/상태를 짧게 남기는 마이크로 저널 기능입니다.

- `bio_one_liner` 컬럼이 DB에 이미 존재
- 매일 갱신 → 피드에서 "오늘 뭘 느끼는지" 보이는 소셜 레이어 역할
- **SORI 본질(솔직한 30초 소리)과 직결**되는 UX

---

### 2-6. 빈 상태 아이콘 숨쉬기 애니메이션

unison-kappa의 빈 상태(empty state) 아이콘은 **4초 주기 숨쉬기 애니**를 사용합니다.

```css
/* unison-kappa */
@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50%       { transform: scale(1.06); opacity: 0.6; }
}
.empty-icon {
  animation: breathe 4s ease-in-out infinite;
}
```

sori-bice의 빈 상태는 정적입니다. 이 미세한 생동감이
"아직 소리가 없는 빈 공간도 살아있다"는 느낌을 줍니다.

---

### 2-7. 콜랩 수(Collabs) 지표 분리

unison-kappa 프로필 통계: **12 Pieces · 3 Jams · 5 Collabs**
sori-bice: Pieces · Jams · ActiveJams · CompletedJams

"Collabs"는 내가 타인의 잼에 레이어를 기여한 횟수로 Jams와 구분됩니다.
이 지표가 없으면 **"나는 만들기만 하고 협업은 안 한다"** 는 유저 행동 패턴이 생깁니다.

```sql
-- Collabs = 내가 creator가 아닌 jam_layers 수
SELECT COUNT(*) FROM jam_layers
WHERE user_id = $userId
AND jam_id NOT IN (SELECT id FROM jams WHERE creator_id = $userId);
```

---

## 3. sori-bice 신규 기획안

### 기획 A — 공명(Like) 기능 완성

현재 UI에서 '공명'이라는 단어를 쓰지만 DB에 카운트 필드가 없습니다.

**구현 명세:**
```sql
-- pieces 테이블 추가
ALTER TABLE pieces ADD COLUMN resonance_count INT NOT NULL DEFAULT 0;

-- 신규 테이블
CREATE TABLE piece_resonances (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  piece_id   UUID REFERENCES pieces(id) ON DELETE CASCADE,
  user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(piece_id, user_id)
);

-- RLS: 본인 공명 읽기/쓰기, 전체 카운트 공개
```

```
API: POST /api/pieces/[id]/resonate   — 공명 토글
API: GET  /api/pieces/[id]/resonances — 공명한 유저 목록
```

**UI:**
- FeedCard에 파형 아래 공명 버튼 (공명 파동 아이콘 + 카운트)
- 공명 시 brief ripple 애니메이션 (indigo → cyan → fade)
- 프로필에서 "공명받은 횟수" 통계 추가

---

### 기획 B — 조각 단위 한마디(댓글) 기능

현재 `chat_messages`는 잼 한정입니다.
조각 하나에 "이 소리, 새벽 감성이네요" 같은 짧은 반응을 남기는 기능이 없습니다.

**구현 명세:**
```sql
CREATE TABLE piece_comments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  piece_id    UUID REFERENCES pieces(id) ON DELETE CASCADE,
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
  message     TEXT NOT NULL CHECK(char_length(message) <= 140),
  created_at  TIMESTAMPTZ DEFAULT now()
);
```

- 글자 수 제한 140자 (SORI 세계관: "한마디"이므로 짧게)
- FeedCard에서 작은 말풍선 아이콘으로 접근
- Realtime 구독으로 실시간 반응 표시

---

### 기획 C — 조각 자동 BPM/키 감지

현재 사용자가 BPM과 키를 수동 입력하므로 오류 시 매칭 품질 저하.

**구현 명세 (단계적):**

**1단계 — Gemini multimodal (권장):**
```typescript
// 업로드 완료 후 백그라운드 분석
POST /api/pieces/[id]/analyze
→ Gemini audio inline + prompt: "이 오디오의 BPM, 키, 장르, 분위기를 JSON으로 반환해줘"
→ 결과를 pieces 테이블에 auto-fill
→ 사용자에게 "AI가 분석한 결과입니다. 수정할 수 있어요." 알림
```

**2단계 — 클라이언트 사이드 (essentia.js / aubio.js):**
```typescript
// 브라우저에서 직접 분석 (서버 비용 0)
import Essentia from 'essentia.js';
const essentia = new Essentia(EssentiaWASM);
const { bpm, key } = await essentia.analyzeAudio(audioBuffer);
```

**데이터 신뢰도 표시:**
- 사용자 수동 입력: 🎹 (피아노 아이콘)
- AI 자동 분석: ✨ (스파클 아이콘)
- 두 값 불일치 시: ⚠️ (경고 아이콘)

---

### 기획 D — B2B 조각 라이선싱 구조

현재 조각 재활용에 제한이 없어 B2B 수익 모델 구축 불가.

**DB 스키마 확장:**
```sql
ALTER TABLE pieces ADD COLUMN license_type    TEXT DEFAULT 'free';
  -- 'free'     : 무제한 재사용 (현재)
  -- 'limited'  : max_uses 횟수 제한
  -- 'exclusive': 1개 잼에만 사용 가능
  -- 'paid'     : price_per_use 과금

ALTER TABLE pieces ADD COLUMN max_uses       INT;
ALTER TABLE pieces ADD COLUMN usage_count    INT NOT NULL DEFAULT 0;
ALTER TABLE pieces ADD COLUMN price_per_use  NUMERIC(10,2);
```

**잼 레이어 추가 시 검증:**
```typescript
// POST /api/jams/[id]/layers
if (piece.license_type === 'limited' && piece.usage_count >= piece.max_uses) {
  return 403, { error: '이 조각의 사용 횟수가 초과됐습니다.' }
}
if (piece.license_type === 'exclusive') {
  const existing = await checkPieceInOtherJams(pieceId);
  if (existing) return 409, { error: '이 조각은 이미 다른 잼에서 사용 중입니다.' }
}
```

**B2B 수익 흐름:**
```
뮤지션이 조각을 'limited(20회)' 또는 'paid(₩500/회)' 로 등록
→ 기업 파트너(광고, 영상, 게임 회사)가 SORI에서 조각 라이선싱
→ SORI는 거래 중개 수수료(20%) 수취
→ 뮤지션은 조각 재사용 수익 수령
```

---

### 기획 E — 울림(완성 잼) 렌더링 파이프라인

현재 완성된 잼은 브라우저에서 여러 트랙을 동시 재생하는 수준입니다.
단일 오디오 파일로 내보내는 렌더링이 없습니다.

**구현 명세:**
```typescript
// POST /api/jams/[id]/render
// 1. 각 레이어의 audio_url에서 파일 다운로드
// 2. FFmpeg WebAssembly로 서버리스 믹싱
// 3. volume_balance 값 적용해 믹스
// 4. 결과 mp3를 Supabase Storage에 저장
// 5. jams 테이블에 rendered_url 업데이트

// 필요 컬럼 추가
ALTER TABLE jams ADD COLUMN rendered_url TEXT;
ALTER TABLE jams ADD COLUMN rendered_at  TIMESTAMPTZ;
```

**렌더링 상태 UI:**
```
완성 전: [Layer 1] [Layer 2] [Layer 3] → 각각 재생만 가능
렌더링 중: ⏳ "소리를 하나로 합치는 중이에요..." (30-60초)
렌더링 완료: ▶ 전체 재생 + 다운로드 + 공유 링크 생성
```

---

### 기획 F — SORI Station 로드맵 구체화

양 사이트 모두 "SORI Station" 오프라인 확장 티저가 있습니다.
현재는 "준비 중" 텍스트만 존재합니다.

**온라인 → 오프라인 연결 기획:**

```
[온라인] 조각 업로드 → 공명 매칭 → 울림 완성
           ↓
[SORI Station] 실물 공간에서:
  - QR 코드로 자신의 조각 재생
  - 다른 방문자 조각과 현장 잼
  - 실시간 레이어 추가 (터치스크린)
  - 완성된 울림을 공간에 설치
```

**DB에 이미 준비된 필드:**
- `availability_schedule`: 오프라인 이벤트 참가 가능 시간 등록 가능
- `gear_closet`: 오프라인 공간에 가져올 장비 표시 가능
- `privacy_mode`: 오프라인 방문자 공개/비공개 제어

---

## 4. 구현 우선순위 로드맵

### Phase 1 — 즉시 (1주 이내)

| 항목 | 난이도 | 임팩트 | 설명 |
|------|--------|--------|------|
| 필름 그레인 오버레이 복원 | ⭐ 낮음 | ⭐⭐⭐ 높음 | CSS + SVG, 코드 10줄 미만 |
| 빈 상태 숨쉬기 애니 추가 | ⭐ 낮음 | ⭐⭐ 중간 | CSS keyframe 추가 |
| Today's Line 에디터블 UI | ⭐⭐ 중간 | ⭐⭐⭐ 높음 | bio_one_liner 이미 DB에 존재 |
| 공명(Like) DB + API 구현 | ⭐⭐ 중간 | ⭐⭐⭐ 높음 | 테이블 추가 + toggle API |

### Phase 2 — 단기 (2–4주)

| 항목 | 난이도 | 임팩트 | 설명 |
|------|--------|--------|------|
| 프로필 Gear 탭 UI | ⭐⭐ 중간 | ⭐⭐⭐ 높음 | gear_closet 컬럼 이미 존재 |
| 프로필 Availability 탭 | ⭐⭐ 중간 | ⭐⭐⭐ 높음 | availability_schedule 이미 존재 |
| 조각 단위 한마디(댓글) | ⭐⭐ 중간 | ⭐⭐ 중간 | 신규 테이블 + API |
| Collabs 지표 분리 | ⭐ 낮음 | ⭐⭐ 중간 | 쿼리 추가만으로 구현 가능 |
| "Tracks Made Together" 탭 | ⭐⭐ 중간 | ⭐⭐ 중간 | jam_layers 쿼리 활용 |

### Phase 3 — 중기 (1–2개월)

| 항목 | 난이도 | 임팩트 | 설명 |
|------|--------|--------|------|
| 조각 자동 BPM/키 감지 | ⭐⭐⭐ 높음 | ⭐⭐⭐⭐ 핵심 | Gemini 또는 essentia.js |
| B2B 라이선싱 스키마 | ⭐⭐⭐ 높음 | ⭐⭐⭐⭐ 핵심 | 수익 모델 기반 |
| 울림 렌더링 파이프라인 | ⭐⭐⭐⭐ 매우 높음 | ⭐⭐⭐⭐ 핵심 | FFmpeg WebAssembly |

### Phase 4 — 장기 (3–6개월)

| 항목 | 난이도 | 임팩트 |
|------|--------|--------|
| Gemini 오디오 분석 완전 연동 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| SORI Station 오프라인 기획 구체화 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| B2B 파트너십 결제 시스템 (Stripe) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 5. SORI 본질과의 정합성 검토

```
SORI 핵심 철학:
"완성되지 않아도 괜찮아요. 겹치면, 곡이 된다."
"30초면 충분합니다."
```

| 기획안 | 본질 정합성 | 이유 |
|--------|------------|------|
| 필름 그레인 복원 | ✅ | 미완성의 질감, 인화지 느낌 |
| Today's Line | ✅ | 오늘 이 순간의 솔직한 소리 |
| 공명(Like) 완성 | ✅ | 서로 연결되는 핵심 행위 |
| 자동 BPM 분석 | ✅ | 이론 몰라도 OK → 더 낮아지는 진입 장벽 |
| Gear 탭 | ⚠️ | 도구 과시로 흐를 수 있음, 톤 조절 필요 |
| B2B 라이선싱 | ⚠️ | 상업화 vs 인디 철학 긴장 — 투명한 정책 필수 |
| 울림 렌더링 | ✅ | 겹쳐진 소리를 하나로 → 완성의 의미 구현 |

---

## 6. 종합 결론

**unison-kappa는 테스트 서버이지만, 다음 5가지는 반드시 sori-bice에 복원·이식해야 합니다:**

1. **필름 그레인 오버레이** — 10줄 CSS로 서비스 질감이 크게 올라감
2. **Today's Line** — 가장 SORI다운 마이크로 기능, DB도 이미 준비됨
3. **Gear + Availability 탭** — DB 컬럼 존재, UI만 없음 — 즉시 복원 가능
4. **빈 상태 숨쉬기 애니** — 서비스 초기 빈 상태가 많을 때 생동감 필수
5. **Collabs 지표** — 협업 플랫폼의 핵심 지표가 빠져있음

**sori-bice의 우위는 유지하면서 unison-kappa의 디테일을 레이어로 더하는 전략을 권장합니다.**

---

*분석 도구: Claude Sonnet 4.6 + WebFetch(unison-kappa.vercel.app, sori-bice.vercel.app)*
