import os
import json
import whisper

WAV_DIR = "/home/gaeun0112/sooho_work/data/raw_data/wav"
OUT_DIR = "/home/gaeun0112/sooho_work/data/json_data"
os.makedirs(OUT_DIR, exist_ok=True)

model = whisper.load_model("large", device="cuda:3")

wav_files = sorted(f for f in os.listdir(WAV_DIR) if f.lower().endswith(".wav"))[:3]
if not wav_files:
    raise RuntimeError(f"No WAV files found in {WAV_DIR}")

for wav_fname in wav_files:
    wav_path = os.path.join(WAV_DIR, wav_fname)
    print(f"[DEBUG] Processing: {wav_path}")

    # 음성 인식 
    result = model.transcribe(
        wav_path,
        language="ko",
        no_speech_threshold=0.2,
        logprob_threshold=-1.0
    )
    text = result.get("text", "").strip()

    # JSON 엔트리 생성
    base = os.path.splitext(wav_fname)[0]
    date_part, uid = base.split("_", 1)

    entry = {
        "id":      f"mp4_{uid}_{date_part}",
        "text":    text,
        "type":    "scenario",
        "meta": {
            "source": "금융감독원",
            "date":   int(date_part)
        },
        "embedding": []
    }

    # 결과 저장
    out_fname = f"{base}.json"
    out_path  = os.path.join(OUT_DIR, out_fname)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved: {out_path}")



