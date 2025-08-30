import pandas as pd
import json

# 1) 경로 설정
json_path  = "/home/gaeun0112/sooho_work/data/json_data/wav_to_text_real.json"
csv_out    = "/home/gaeun0112/sooho_work/preprocessing/wav_to_text_real.csv"

# 2) JSON 읽기
with open(json_path, "r", encoding="utf-8") as f:
    records = json.load(f)

# 3) normalize & meta 펼치기
df = pd.json_normalize(records)
df = df.rename(columns={
    "meta.date":   "date",
    "meta.source": "source"
})

# 4) kind 칼럼 추가
df["kind"] = "mp4"

# 5) 엑셀 포맷에 맞게 컬럼 순서 재정렬
df = df[["id", "text", "type", "kind", "date", "source", "embedding"]]

# 6) CSV로 저장 (utf-8-sig: Excel 한글 깨짐 방지)
df.to_csv(csv_out, index=False, encoding="utf-8-sig")

df1 = pd.read_csv("/home/gaeun0112/sooho_work/preprocessing/preprocessed_merged_output.csv", encoding="utf-8-sig")
df2 = pd.read_csv("/home/gaeun0112/sooho_work/preprocessing/wav_to_text_real.csv", encoding="utf-8-sig")
df_all = pd.concat([df1, df2], ignore_index=True)
df_all.to_csv("/home/gaeun0112/sooho_work/preprocessing/preprocessed_merged_output_V2.csv", index=False, encoding="utf-8-sig")
