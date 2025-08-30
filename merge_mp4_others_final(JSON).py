import os
import csv
import json

INPUT_CSV    = '/home/gaeun0112/sooho_work/preprocessing/preprocessed_merged_output_V3.csv'
OUTPUT_DIR   = '/home/gaeun0112/sooho_work/data/json_data'
OUTPUT_JSON  = os.path.join(OUTPUT_DIR, 'json_final.json')

os.makedirs(OUTPUT_DIR, exist_ok=True)

records = []
with open(INPUT_CSV, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    reader.fieldnames = [name.strip() for name in reader.fieldnames]
    for row in reader:
        emb = row.get('embedding', '').strip()
        try:
            embedding = json.loads(emb) if emb else []
        except json.JSONDecodeError:
            embedding = []
        date = row.get('date', '')
        date_val = int(date) if date.isdigit() else date

        records.append({
            "id":        row.get("id", ""),
            "text":      row.get("text", ""),
            "type":      row.get("type", ""),
            "meta": {
                "source": row.get("source", ""),
                "date":   date_val
            },
            "embedding": embedding
        })
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)


