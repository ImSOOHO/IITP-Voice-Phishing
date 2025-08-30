import pandas as pd

df_mp4 = pd.read_csv('/home/gaeun0112/sooho_work/Embedding/mp4_to_chunk.csv', encoding = 'utf-8-sig')
df_others = pd.read_csv('/home/gaeun0112/sooho_work/Embedding/others_to_chunk.csv', encoding = 'utf-8-sig')

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "3"

import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def build_vector_db(df_mp4, df_others):
    """
    벡터 데이터베이스를 구축하는 함수
    
    Args:
        df_mp4 (pd.DataFrame): MP4 파일에서 추출된 데이터프레임
        df_others (pd.DataFrame): 기타 파일에서 추출된 데이터프레임
    """
    # 모델 로드
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # MP4 임베딩
    mp4_texts = df_mp4['text_chunk'].fillna('').astype(str).tolist()
    mp4_embeddings = model.encode(mp4_texts, batch_size=32, show_progress_bar=True)
    # mp4_embeddings = normalize(np.array(mp4_embeddings).astype('float32')) -> 코사인 유사도 사용시 변경
    
    # Others 임베딩
    others_texts = df_others['text_chunk'].fillna('').astype(str).tolist()
    others_embeddings = model.encode(others_texts, batch_size=32, show_progress_bar=True)
    # others_embeddings = normalize(np.array(others_embeddings).astype('float32')) -> 코사인 유사도 사용시 변경
    
    # FAISS 인덱스 구축 (GPU 사용)
    dimension = 384
    res = faiss.StandardGpuResources()
    
    # MP4 인덱스
    mp4_gpu_index = faiss.GpuIndexFlatL2(res, dimension)
    # mp4_gpu_index = faiss.GpuIndexFlatIP(res, dimension) -> 코사인 유사도 사용시 변경
    mp4_embeddings = np.array(mp4_embeddings).astype('float32')
    mp4_gpu_index.add(mp4_embeddings)
    mp4_cpu_index = faiss.index_gpu_to_cpu(mp4_gpu_index)
    faiss.write_index(mp4_cpu_index, "mp4_vector_db.index")
    
    # Others 인덱스
    others_gpu_index = faiss.GpuIndexFlatL2(res, dimension)
    # others_gpu_index = faiss.GpuIndexFlatIP(res, dimension) -> 코사인 유사도 사용시 변경
    others_embeddings = np.array(others_embeddings).astype('float32')
    others_gpu_index.add(others_embeddings)
    others_cpu_index = faiss.index_gpu_to_cpu(others_gpu_index)
    faiss.write_index(others_cpu_index, "others_vector_db.index")
    
    # 메타데이터 저장
    df_mp4['embedding'] = mp4_embeddings.tolist()
    df_others['embedding'] = others_embeddings.tolist()
    
    df_mp4.to_parquet('mp4_vector_db_metadata.parquet')
    df_others.to_parquet('others_vector_db_metadata.parquet')
    return mp4_cpu_index, others_cpu_index, df_mp4, df_others

if __name__ == "__main__":
    df_mp4 = pd.read_csv('/home/gaeun0112/sooho_work/Embedding/mp4_to_chunk.csv', encoding='utf-8-sig')
    df_others = pd.read_csv('/home/gaeun0112/sooho_work/Embedding/others_to_chunk.csv', encoding='utf-8-sig')
    
    mp4_index, others_index, df_mp4, df_others = build_vector_db(df_mp4, df_others)
