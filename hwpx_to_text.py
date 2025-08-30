import os
import json
import tempfile
import win32com.client as win32
import zipfile
import re

def extract_hwpx_text(path):
    
    # COM 방식 시도 
    try:
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.Open(path, "HWP", "forceopen:true")
        tmp = os.path.join(tempfile.gettempdir(), "dump.txt")
        hwp.SaveAs(tmp, "TEXT")
        hwp.Run("FileClose")
        hwp.Run("FileClose")
        hwp.Quit()
        with open(tmp, 'r', encoding='cp949', errors='ignore') as f:
            text = f.read().strip()
        os.remove(tmp)
        if text:
            return text
    except:
        pass  

    # ZIP+XML 파싱 방식 폴백
    texts = []
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            if not name.lower().endswith('.xml'):
                continue
            data = z.read(name).decode('utf-8', errors='ignore')
            # XML 태그 제거
            plain = re.sub(r'<[^>]+>', '', data)
            texts.append(plain)
    # 반환
    return '\n'.join(texts).strip()


def extract_text_from_hwpx_files(hwpx_folder_path, output_json_path):
    hwpx_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(hwpx_folder_path)
        for f in files if f.lower().endswith('.hwpx')
    ]
    print(f"발견된 HWPX 파일 수: {len(hwpx_files)}")

    items = []
    for i, path in enumerate(hwpx_files, 1):
        name = os.path.basename(path)
        print(f"({i}/{len(hwpx_files)}) 처리 중: {name}")
        text = extract_hwpx_text(path)

        # id, date, source 파싱
        base, _ = os.path.splitext(name)
        parts  = base.split('_', 3)
        idx    = parts[1] if len(parts)>1 else ""
        date   = int(parts[2]) if len(parts)>2 and parts[2].isdigit() else None
        source = parts[3] if len(parts)>3 else ""
        uid    = f"text_{idx}_{date}" if date else base

        items.append({
            "id":        uid,
            "text":      text,
            "type":      "scenario",
            "meta":      {"date": date, "source": source},
            "embedding": []
        })

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print("추출 완료:", output_json_path)


if __name__ == "__main__":
    hwpx_folder = r"C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\attachments\hwpx"
    out_json    = r"C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\json_file\hwpx_to_text.json"
    extract_text_from_hwpx_files(hwpx_folder, out_json)



