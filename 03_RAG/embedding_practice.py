"""
임베딩 모델 비교: 다국어 모델 vs 영어 전용 모델.
동일한 한국어 질의로 검색 품질(코사인 유사도) 차이를 직접 확인한다.
"""

from sentence_transformers import SentenceTransformer
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

query = "AI 기술에 대해 설명하는 문서를 찾아줘"
documents = [
    "인공지능은 컴퓨터가 인간처럼 학습하고 추론하는 기술이다.", # 질의와 관련 있는 문서
    "아이스크림은 여름에 인기가 많은 디저트이다.", # 질의와 무관한 문서
]


models = {
    "다국어 (multilingual-e5-small)": "intfloat/multilingual-e5-small",
    "영어 전용 (all-MiniLM-L6-v2)" : "sentence-transformers/all-MiniLM-L6-v2",
}


for name, model_name in models.items():
    print(f"\n== {name} ===")
    model = SentenceTransformer(model_name)


    query_vec = model.encode(query)
    print(f"임베딩 차원: {len(query_vec)}")

    for doc in documents:
        doc_vec = model.encode(doc)
        sim = cosine_similarity(query_vec, doc_vec)
        print(f"유사도 {sim:.4F} <- {doc}")