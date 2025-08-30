import re
import pandas as pd
from transformers import AutoTokenizer

TOKENIZER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_CHUNK_TOKENS = 240  
OVERLAP_TOKENS = 20     
tok = AutoTokenizer.from_pretrained(TOKENIZER_MODEL, use_fast=True)


def _date_from_id(s: str) -> str:
    # ID에서 날짜 추출
    m = re.search(r"(\d{8})$", str(s))
    return m.group(1) if m else ""


def _clean_spaces(s: str) -> str:
    # 공백과 개행 정리
    s = ("" if s is None else str(s)).replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _chunk_by_offsets(text: str,
                      max_len: int = MAX_CHUNK_TOKENS,
                      overlap: int = OVERLAP_TOKENS):
    # WordPiece 기준 슬라이싱
    assert overlap < max_len
    t = "" if text is None else str(text)

    enc = tok(t, add_special_tokens=False, return_offsets_mapping=True)
    offs = enc["offset_mapping"]
    n = len(offs)

    if n == 0:
        return [dict(chunk_idx=1, wp_tokens=0, text_chunk="")]

    chunks, start, idx = [], 0, 1
    while start < n:
        end = min(start + max_len, n)
        s_off, e_off = offs[start][0], offs[end-1][1]
        chunks.append(dict(
            chunk_idx=idx,
            wp_tokens=end - start,
            text_chunk=t[s_off:e_off],
        ))
        if end == n:
            break
        start = end - overlap
        idx += 1
    return chunks


def _split_cases_from_trim(trim_text: str):
    # 사례로 분할
    t = _clean_spaces(trim_text)
    it = list(re.finditer(r"사례\s*\d*\s*:", t))
    cases = []
    if it:
        for i, m in enumerate(it):
            start = m.end()
            end = it[i+1].start() if i+1 < len(it) else len(t)
            body = t[start:end].strip()
            cases.append(f"사례: {body}")  
    else:
        cases.append(re.sub(r"사례\s*\d*\s*:", "사례: ", t).strip())
    return cases


def build_mp4_cases_then_chunks(df_mp4: pd.DataFrame,
                                id_col="id", 
                                trim_col="trim") -> pd.DataFrame:
    # MP4 사례 분할 및 청크 분할
    rows = []
    for _, r in df_mp4.iterrows():
        base_id = str(r[id_col])
        full = r.get(trim_col, "")

        case_texts = _split_cases_from_trim(full)  # 사례 분할

        for ci, case_text in enumerate(case_texts, start=1):
            case_id = f"{base_id}_{ci}"
            chunks = _chunk_by_offsets(case_text)  # 청크 분할

            for ch in chunks:
                rows.append({
                    "id": f"{case_id}_c{ch['chunk_idx']}",
                    "case_idx": ci,
                    "chunk_idx": ch["chunk_idx"],
                    "wp_tokens": ch["wp_tokens"],
                    "text": case_text,
                    "text_chunk": ch["text_chunk"],
                    "type": "scenario",
                    "kind": "mp4",
                    "date": _date_from_id(base_id),
                    "source": "금융감독원",
                    "embedding": [],
                })

    cols = ["id", "case_idx", "chunk_idx", "wp_tokens", "text", "text_chunk",
            "type", "kind", "date", "source", "embedding"]
    return pd.DataFrame(rows, columns=cols).reset_index(drop=True)


# TEXT/HWP/HWPX/PDF 파일 처리 
METHOD_PAT = re.compile(r"(?:사기\s*수법|수법)\s*[:：﹕∶]\s*", flags=re.IGNORECASE)
CASE_PAT = re.compile(r"사례\s*\d*\s*[:：﹕∶]\s*", flags=re.IGNORECASE)


def _normalize_labels(text: str) -> str:
    # 라벨과 공백/개행을 정규화
    if text is None:
        return ""
    s = str(text)

    # 라벨의 콜론 변형 표준화
    s = re.sub(r"(?:사기\s*수법|수법)\s*[:：﹕∶]\s*", "사기수법: ", s, flags=re.IGNORECASE)
    s = re.sub(r"(사례)\s*(\d*)\s*[:：﹕∶]\s*", r"사례\2: ", s, flags=re.IGNORECASE)

    # 개행 제거
    s = s.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    s = re.sub(r"(\\n)+", " ", s)

    # 공백 정리
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s


def _split_methods_and_cases(text: str):
    t = _normalize_labels(text)
    m_iter = list(METHOD_PAT.finditer(t))
    out = []

    if not m_iter:
        # 수법 라벨이 없으면 사례만 분리
        c_iter = list(CASE_PAT.finditer(t))
        if not c_iter:
            out.append(dict(method=None, case=t.strip(), method_idx=1, case_idx=1))
            return out
        for ci, cm in enumerate(c_iter):
            cs = cm.end()
            ce = c_iter[ci+1].start() if ci+1 < len(c_iter) else len(t)
            out.append(dict(method=None, case=t[cs:ce].strip(), method_idx=1, case_idx=ci+1))
        return out

    # 각 수법 블록 파싱
    for mi, m in enumerate(m_iter):
        seg_start = m.end()
        seg_end = m_iter[mi+1].start() if mi+1 < len(m_iter) else len(t)
        seg = t[seg_start:seg_end].strip()

        # 수법 설명 추출
        hm = re.match(r"(.*?)(?=사례\s*\d*\s*:\s*|$)", seg, flags=re.IGNORECASE|re.DOTALL)
        method_val = (hm.group(1) if hm else "").strip()
        rest = seg[hm.end():].strip() if hm else ""

        # 사례 분리
        c_iter = list(CASE_PAT.finditer(rest))
        if not c_iter:
            out.append(dict(method=method_val, case=rest.strip(), method_idx=mi+1, case_idx=1))
        else:
            for ci, cm in enumerate(c_iter):
                cs = cm.end()
                ce = c_iter[ci+1].start() if ci+1 < len(c_iter) else len(rest)
                out.append(dict(method=method_val,
                              case=rest[cs:ce].strip(),
                              method_idx=mi+1, 
                              case_idx=ci+1))
    return out


def case_split(df: pd.DataFrame,
               id_col: str = "id",
               text_col: str = "text",
               keep_cols=("type", "kind", "date", "source")) -> pd.DataFrame:
    # 각 행을 수법×사례 단위로 분해
    rows = []
    for _, row in df.iterrows():
        base_id = str(row[id_col])
        parts = _split_methods_and_cases(row[text_col])

        for j, p in enumerate(parts, start=1):
            rec = {k: row[k] for k in keep_cols if k in row.index}
            rec["parent_id"] = base_id
            rec["method_idx"] = p["method_idx"]
            rec["case_idx"] = p["case_idx"]
            rec[id_col] = f"{base_id}_{j}"

            method_line = f"사기수법: {p['method']}".strip() if p["method"] else "사기수법: "
            text_norm = f"{method_line} 사례: {p['case']}".strip()
            rec[text_col] = text_norm

            rows.append(rec)

    out = pd.DataFrame(rows).reset_index(drop=True)
    return out


def apply_chunk_df(df: pd.DataFrame,
                   id_col: str = "id",
                   text_col: str = "text",
                   max_len: int = MAX_CHUNK_TOKENS,
                   overlap: int = OVERLAP_TOKENS) -> pd.DataFrame:
    # 입력 DF를 청크 단위로 확장
    rows = []
    for _, row in df.iterrows():
        base_id = str(row[id_col])
        full_text = row[text_col] if row[text_col] is not None else ""
        chunks = _chunk_by_offsets(full_text, max_len=max_len, overlap=overlap)

        for ch in chunks:
            rec = {
                "id": f"{base_id}_c{ch['chunk_idx']}",
                "text": str(full_text),
                "text_chunk": ch["text_chunk"],
                "type": row.get("type", ""),
                "kind": row.get("kind", ""),
                "date": row.get("date", ""),
                "source": row.get("source", ""),
                "embedding": [],
            }
            rows.append(rec)

    out = pd.DataFrame(rows, columns=[
        "id", "text", "text_chunk", "type", "kind", "date", "source", "embedding"
    ])
    return out.reset_index(drop=True)


# 실행
if __name__ == "__main__":
    # MP4 파일 처리
    df_mp4 = pd.read_csv('/content/drive/MyDrive/IITP_voicefishing/df_scored_fixed.csv', 
                         encoding='UTF-8-SIG')
    df_mp4 = df_mp4[['id', 'raw', 'trim']]
    df_mp4_chunks = build_mp4_cases_then_chunks(df_mp4, id_col="id", trim_col="trim")
    
    # TEXT/HWP/HWPX/PDF 파일 처리
    df_all = pd.read_csv('/home/gaeun0112/sooho_work/preprocessing/preprocessed_merged_output_V3.csv', 
                         encoding='UTF-8-SIG')
    df_others = df_all[df_all["kind"] != "mp4"]
    df_others_split = case_split(df_others)
    df_others_split_chunk = apply_chunk_df(df_others_split)
    
    # 저장
    df_mp4_chunks.to_csv('mp4_to_chunk.csv', encoding='utf-8-sig', index=False)
    df_others_split_chunk.to_csv('others_to_chunk.csv', encoding='utf-8-sig', index=False)
