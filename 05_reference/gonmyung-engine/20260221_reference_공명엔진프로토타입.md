---
날짜: 2026-02-21
작성자: BRUCE
관련기능: 공명(GONMYUNG) AI 음악 엔진 / Guided-Auto 파이프라인
우선순위: 높음
상태: 완료
---

# 공명 엔진 프로토타입 — GONMYUNG AI Music Engine

## 구성 파일
```
gonmyung-engine/
├── app.py              ← Flask 백엔드 (파이프라인 API)
├── presets.json        ← 20개 장르별 마스터링 프리셋 DB
├── requirements.txt    ← 의존성 (flask)
└── static/
    └── index.html      ← 프론트엔드 UI + 로딩 애니메이션
```

## 실행 방법
```bash
cd gonmyung-engine
pip install -r requirements.txt
python app.py
# → http://localhost:5001 접속
```

## 파이프라인 구조 (Guided-Auto)
1. **MusicGen** (Meta 오픈소스) — 장르 기반 음악 생성 *[현재: 시뮬레이션]*
2. **마스터링 프리셋** — 20개 장르 DB 자동 적용
3. **Demucs** — 드럼 · 베이스 · 멜로디 스템 자동 분리 *[현재: 시뮬레이션]*
4. **패키징** — Full Mix + Stems 파일 출력

## 로딩 화면
> "흩어진 조각들을 모아서 공명의 주파수를 맞추는 중입니다."

파티클이 흩어진 상태 → 궤도 수렴 → 공명 완료 3단계 캔버스 애니메이션

## 실제 MusicGen 연결 시
`app.py` 내 `generate_sine_wave()` 함수를 MusicGen API 호출로 교체하면 됨:
```python
# from audiocraft.models import MusicGen
# model = MusicGen.get_pretrained('small')
# model.set_generation_params(duration=duration)
# wav = model.generate([f"{genre} music, {mood}"])
```

## 출처
내부 개발 프로토타입 (SORI 프로젝트 공명 엔진 기획 기반)
