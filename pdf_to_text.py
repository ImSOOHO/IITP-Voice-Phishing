import json
from pathlib import Path
import pdfplumber

# 경로 설정
INPUT_DIR   = Path(r"C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\attachments\pdf")
OUTPUT_PATH = Path(r"C:\Users\ben76\Desktop\HLI 연구실\보이스피싱 연구\크롤링 코드\json_file\pdf_to_text.json")

items = []

# 폴더 내 PDF 순회
for pdf_path in sorted(INPUT_DIR.glob("*.pdf")):
    fname = pdf_path.stem  # e.g. text_065_20150420_서민금융지원국
    parts = fname.split("_", 3)

    # id, date, source 파싱
    _id     = fname
    date    = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else None
    source  = parts[3]    if len(parts) >= 4 else ""

    # pdfplumber로 텍스트 추출
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            full_text.append(txt.strip())
    text = "\n\n".join(full_text).strip()

    # JSON format
    items.append({
        "id": _id,
        "text": text,
        "type": "scenario",
        "meta": {
            "date": date,
            "source": source
        },
        "embedding": []
    })

# JSON 저장
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)










