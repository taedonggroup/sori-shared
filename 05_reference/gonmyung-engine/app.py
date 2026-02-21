"""
공명(GONMYUNG) AI 음악 엔진 — 테스트 서버
파이프라인: MusicGen → 마스터링 프리셋 → Demucs 스템 분리
"""

from flask import Flask, request, jsonify, send_file, Response
import json, os, math, struct, wave, time, random, threading

app = Flask(__name__, static_folder='static', static_url_path='')

with open('presets.json', encoding='utf-8') as f:
    PRESETS = json.load(f)['presets']

os.makedirs('output', exist_ok=True)

# ── 오디오 생성 유틸 ──────────────────────────────────────────────
SAMPLE_RATE = 44100

def sine_wave(freq, duration, amplitude=0.3, harmonics=1):
    """배음이 포함된 사인파 생성 (더 풍부한 소리)"""
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        val = 0
        for h in range(1, harmonics + 1):
            val += (amplitude / h) * math.sin(2 * math.pi * freq * h * t)
        # 페이드 인/아웃
        fade = min(i / (SAMPLE_RATE * 0.05), 1, (n - i) / (SAMPLE_RATE * 0.05))
        samples.append(int(val * 32767 * fade))
    return samples

def write_wav(path, samples):
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(struct.pack(f'<{len(samples)}h', *samples))

# ── 라우트 ────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/presets')
def get_presets():
    return jsonify(PRESETS)

@app.route('/api/generate', methods=['POST'])
def generate():
    data       = request.json
    genre      = data.get('genre', 'ambient')
    duration   = max(5, min(int(data.get('duration', 10)), 30))
    mood       = data.get('mood', '공명')

    preset = next((p for p in PRESETS if p['genre'] == genre), PRESETS[4])
    freq   = preset['base_frequency']

    # ── 파이프라인 시뮬레이션 ──
    steps = [
        {"step": "init",       "message": "흩어진 조각들을 수집하는 중..."},
        {"step": "frequency",  "message": "공명의 주파수를 맞추는 중입니다..."},
        {"step": "musicgen",   "message": f"[MusicGen] {genre} 장르 음악 생성 중..."},
        {"step": "preset",     "message": f"[마스터링] '{preset['name']}' 프리셋 적용 중..."},
        {"step": "demucs",     "message": "[Demucs] 드럼 · 베이스 · 멜로디 스템 분리 중..."},
        {"step": "packaging",  "message": "최종 패키징 완료 — 공명이 울립니다."},
    ]

    # ── 오디오 파일 생성 ──
    write_wav('output/full_mix.wav',    sine_wave(freq,       duration, harmonics=4))
    write_wav('output/stem_drums.wav',  sine_wave(60,         duration, amplitude=0.4, harmonics=2))
    write_wav('output/stem_bass.wav',   sine_wave(freq * 0.5, duration, amplitude=0.35, harmonics=3))
    write_wav('output/stem_melody.wav', sine_wave(freq * 2,   duration, amplitude=0.25, harmonics=5))

    return jsonify({
        "success":        True,
        "genre":          genre,
        "mood":           mood,
        "duration":       duration,
        "preset_applied": preset['name'],
        "preset_eq":      preset['eq'],
        "preset_reverb":  preset['reverb'],
        "steps":          steps,
        "outputs": {
            "full_mix": "/api/audio/full_mix",
            "stems": {
                "drums":   "/api/audio/stem_drums",
                "bass":    "/api/audio/stem_bass",
                "melody":  "/api/audio/stem_melody"
            }
        }
    })

@app.route('/api/audio/<name>')
def serve_audio(name):
    path = f'output/{name}.wav'
    if os.path.exists(path):
        return send_file(path, mimetype='audio/wav')
    return jsonify({"error": "파일 없음"}), 404

if __name__ == '__main__':
    print("\n[GONMYUNG] 공명 엔진 시작 -> http://localhost:5001\n")
    app.run(debug=True, port=5001)
