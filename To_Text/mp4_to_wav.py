import os
import subprocess
from pathlib import Path

RAW_DIR = "/home/gaeun0112/sooho_work/data/raw_data/mp4"
WAV_DIR = "/home/gaeun0112/sooho_work/data/raw_data/wav"

def convert_to_whisper_wav(input_path: str) -> str:
    input_file = Path(input_path)
    output_path = Path(WAV_DIR) / f"{input_file.stem}.wav"
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vn",  # 비디오 제거
        "-ac", "1",  # 모노
        "-ar", "16000",  # 16kHz (Whisper 표준)
        "-acodec", "pcm_s16le",  # 16-bit PCM
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",  # 음량 정규화
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True)
    print(f"변환 완료: {output_path.name}")
    return str(output_path)

def get_media_files(directory: str) -> list:
    extensions = {'.mp4', '.avi', '.mov', '.mkv', '.mp3', '.m4a', '.wav', '.flac'}
    files = []
    
    for file_path in Path(directory).iterdir():
        if file_path.suffix.lower() in extensions:
            files.append(file_path)
    
    return sorted(files)

def batch_convert_for_whisper():
    os.makedirs(WAV_DIR, exist_ok=True)
    media_files = get_media_files(RAW_DIR)
    if not media_files:
        print(f"'{RAW_DIR}'에 미디어 파일이 없습니다.")
        return
    print(f"{len(media_files)}개 변환")
    
    success_count = 0
    for i, file_path in enumerate(media_files, 1):
        try:
            output_name = f"{file_path.stem}.wav"
            if (Path(WAV_DIR) / output_name).exists():
                print(f"이미 존재: {output_name} ({i}/{len(media_files)})")
                success_count += 1
                continue
            print(f"변환 중: {file_path.name} ({i}/{len(media_files)})")
            convert_to_whisper_wav(str(file_path))
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"변환 실패: {file_path.name} - {e}")
        except Exception as e:
            print(f"오류: {file_path.name} - {e}")
    
    print(f"\n 변환 완료: {success_count}/{len(media_files)}개")

if __name__ == "__main__":
    batch_convert_for_whisper()





