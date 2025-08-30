import pandas as pd
import json

# 경로
EXCEL_CSV = "/home/gaeun0112/sooho_work/preprocessing/preprocessed_merged_output.csv"
JSON_PATH = "/home/gaeun0112/sooho_work/data/json_data/wav_to_text_real.json"
OUT_CSV    = "/home/gaeun0112/sooho_work/preprocessing/preprocessed_merged_output_V2.csv"

# 1) 기존 엑셀(CSV) 읽기
df = pd.read_csv(EXCEL_CSV, encoding="utf-8-sig")\
       .set_index("id")

# 2) JSON 읽어서 펼치고 컬럼명 맞추기
with open(JSON_PATH, "r", encoding="utf-8") as f:
    records = json.load(f)
df_json = (pd.json_normalize(records)
             .rename(columns={"meta.date": "date",
                              "meta.source": "source"}))
# JSON에 kind 채우고, 필요한 컬럼만 골라서 인덱스 설정
df_json["kind"] = "mp4"
df_json = df_json.set_index("id")[["text","type","kind","date","source","embedding"]]

# 3) 같은 id, 같은 컬럼만 덮어쓰기
df.update(df_json)

# 4) 결과 저장
df.reset_index().to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

print("Merged CSV written to", OUT_CSV)



