import os
import glob
import re
import soundfile as sf
import numpy as np

# 설정
WAV_DIR = "/home/gaeun0112/sooho_work/data/raw_data/wav"
OUT_DIR = "/home/gaeun0112/sooho_work/data/experiment/TRIM_WAV"
os.makedirs(OUT_DIR, exist_ok=True)

def get_trim_front(idx: int) -> int:
    # 인트로 자르기(초)
    if 1 <= idx <= 12:
        return 4
    elif 13 <= idx <= 29:
        return 12
    elif 30 <= idx <= 46:
        return 16
    elif 47 <= idx <= 63:
        return 18
    elif 64 <= idx <= 69:
        return 16
    elif 70 <= idx <= 77:
        return 12
    elif 78 <= idx <= 86:
        return 15
    elif 87 <= idx <= 89:
        return 9
    elif 90 <= idx <= 94:
        return 10
    else:
        return 0  # 매핑 외 구간은 자르지 않음

def get_trim_back(idx: int) -> int:
    # 아웃트로 자르기(초)
    if 92 <= idx <= 94:
        return 24
    elif 87 <= idx <= 91:
        return 10
    elif 47 <= idx <= 86:
        return 13
    elif 30 <= idx <= 46:
        return 10
    elif 13 <= idx <= 29:
        return 8
    elif 1 <= idx <= 12:
        return 7
    else:
        return 0  # 매핑 외 구간은 자르지 않음

for path in sorted(glob.glob(os.path.join(WAV_DIR, "*.wav"))):
    fn = os.path.basename(path)
    base, _ = os.path.splitext(fn)
    m = re.match(r'.*_(\d+)$', base)
    if not m:
        print(f"[SKIP] 번호 추출 실패: {fn}")
        continue
    idx = int(m.group(1))

    # 파일 읽기 (16kHz mono int16 권장)
    audio, sr = sf.read(path, dtype='int16')
    if audio.ndim > 1:
        audio = audio.mean(axis=1).astype('int16')

    # 앞뒤 자르기
    trim_front = get_trim_front(idx)
    trim_back  = get_trim_back(idx)

    start = int(trim_front * sr)
    end   = len(audio) - int(trim_back * sr)
    if start >= end:
        print(f"[SKIP] 잘라낼 범위가 너무 큼: {fn} (start={start}, end={end})")
        continue

    cropped = audio[start:end]

    # 저장 (예: 20150828_92_trim.wav)
    out_fn = f"{base}_trim.wav"
    sf.write(os.path.join(OUT_DIR, out_fn), cropped, sr)
    print(f"[DONE] {fn} → {out_fn} (front {trim_front}s, back {trim_back}s)")
