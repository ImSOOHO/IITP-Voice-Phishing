import os
import json
import tempfile
import win32com.client as win32
from datetime import datetime
import re

def extract_text_from_hwp_files(hwp_folder_path, output_json_path):
    # HWP 파일
    hwp_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(hwp_folder_path)
        for f in files if f.lower().endswith('.hwp')
    ]
    print(f"발견된 HWP 파일 수: {len(hwp_files)}")

    # 한글 COM 객체 생성
    try:
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
    except Exception as e:
        print("한글 연결 실패:", e)
        return

    items = []
    for i, path in enumerate(hwp_files, 1):
        name = os.path.basename(path)
        print(f"({i}/{len(hwp_files)}) 처리 중: {name}")
        try:
            # 파일 열기
            hwp.Open(path, "HWP", "forceopen:true")

            # SaveAs로 텍스트 덤프
            tmp = os.path.join(tempfile.gettempdir(), name + ".txt")
            hwp.SaveAs(tmp, "TEXT")
            with open(tmp, 'r', encoding='cp949', errors='ignore') as f:
                text = f.read().strip()
            os.remove(tmp)

            # id, date, source 추출
            base, _ = os.path.splitext(name)
            parts = base.split('_', 3)
            idx    = parts[1] if len(parts) > 1 else ""
            date   = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
            source = parts[3] if len(parts) > 3 else ""

            # JSON format
            items.append({
                "id":   f"text_{idx}_{date}" if date else base,
                "text": text,
                "type": "scenario",
                "meta": {"date": date, "source": source},
                "embedding": []
            })

            # 문서 닫기
            hwp.Run("FileClose")
            hwp.Run("FileClose")

        except Exception as e:
            print("오류 발생:", name, e)
            # 재시작
            try:
                hwp.Quit()
                hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
            except:
                pass

    # 한글 종료
    try:
        hwp.Quit()
    except:
        pass

    # JSON 파일 저장
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("추출 완료:", output_json_path)


if __name__ == "__main__":
    # 처리할 폴더와 저장할 JSON 경로만 바꿔서 실행하세요.
    hwp_folder    = r"C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\attachments\hwp"
    output_json   = r"C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\attachments\hwp_to_text.json"
    extract_text_from_hwp_files(hwp_folder, output_json)
