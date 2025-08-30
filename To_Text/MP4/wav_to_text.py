import os
import glob
import json
import librosa
import whisper

# ====== Path ======
TRIM_DIR                = "/home/gaeun0112/sooho_work/data/experiment/TRIM_WAV"
TRIM_OUT_JSON           = "/home/gaeun0112/sooho_work/data/experiment/new_treansform_data/trim_test.json"
# TRIM_NOBEEP_DIR         = "/home/gaeun0112/sooho_work/data/experiment/NO_BEEP_WAV"
# TRIM_NOBEEP_OUT_JSON    = "/home/gaeun0112/sooho_work/data/experiment/new_treansform_data/trim_nobeep_test.json"

# ===== Whisper ======
model = whisper.load_model("large", device="cuda:3")

def transcribe_dir(dir_path: str, out_json_path: str):
    records = []

    wav_list = sorted(glob.glob(os.path.join(dir_path, "*.wav")))
    print(f"\n▶ Start: {dir_path}  (files: {len(wav_list)})")

    for idx, wav_path in enumerate(wav_list, 1):
        basename = os.path.basename(wav_path)                  
        name_wo_ext = os.path.splitext(basename)[0]            
        file_id = f"mp4_{name_wo_ext}"                        
        date_str = basename.split("_")[0]                      

        print(f"  [{idx}/{len(wav_list)}] {basename}")

        try:
            # 오디오 로드 (16k, mono)
            y, sr = librosa.load(wav_path, sr=16000, mono=True)

            # Whisper 전사
            result = model.transcribe(
                y,
                language="ko",
                task="transcribe",
                condition_on_previous_text=False,
                no_speech_threshold=0.2,
                beam_size=5,
                best_of=5,
                verbose=1,
            )
            final_text = (result.get("text") or "").strip()

            records.append({
                "id": file_id,
                "text": final_text,
                "type": "scenario",
                "meta": {
                    "source": "금융감독원",
                    "date": int(date_str)
                },
                "embedding": []
            })

        except Exception as e:
            print(f"Error: {basename} -> {e}")

    os.makedirs(os.path.dirname(out_json_path), exist_ok=True)
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(records)} records to {out_json_path}")

if __name__ == "__main__":
    transcribe_dir(TRIM_DIR, TRIM_OUT_JSON)
    # transcribe_dir(TRIM_NOBEEP_DIR, TRIM_NOBEEP_OUT_JSON)




