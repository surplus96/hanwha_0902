"""
RAGAS 정량 평가: 골든 데이터셋으로 Faithfulness, Answer Relevancy,
Context Precision, Context Recall 4대 지표를 측정한다.
실제 서비스와 동일한 rag_service.answer_with_context()를 그대로 재사용한다.
"""

import os
from dotenv import load_dotenv
import openai
from langchain_openai import ChatOpenAI

from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from langchain_openai import OpenAIEmbeddings as LangchainOpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithReference,
    LLMContextRecall,
)

import rag_service

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 1. 실제 서비스와 동일한 RAG 파이프라인 초기화
rag_service.initialize_rag(OPENAI_API_KEY, DEFAULT_MODEL)

# 2. 골든 데이터셋 - sample.txt / manufacturing.txt 양쪽에서 질문 + 정답(reference) 구성
golden_qa = [
    {"question": "딥러닝이 뭐야?",
     "reference": "딥러닝은 머신러닝의 한 갈래로, 인공신경망을 여러 층으로 쌓아 복잡한 패턴을 학습하는 기술이다."},
    {"question": "머신러닝과 인공지능의 관계는?",
     "reference": "머신러닝은 인공지능의 한 분야로, 데이터를 통해 스스로 패턴을 찾아낸다."},
    {"question": "HS-ROBOT-A7의 반복 위치 정밀도는?",
     "reference": "HS-ROBOT-A7의 반복 위치 정밀도는 ±0.02mm이다."},
    {"question": "HS-CNC-450X에서 오류코드 E-204가 뜨면 어떻게 해야 해?",
     "reference": "주축 모터 과부하를 의미하며, 즉시 가공을 중단하고 냉각 시스템을 점검해야 한다."},
    {"question": "HS-CONV-200의 시간당 최대 이송 개수는?",
     "reference": "시간당 최대 1200개의 부품을 이송할 수 있다."},
    {"question": "HS-VISION-9는 표면 결함을 몇 mm 단위까지 검출할 수 있어?",
     "reference": "0.1mm 단위까지 검출할 수 있다."},
]

# 3. 실제 파이프라인으로 각 질문에 답변 + 문맥 수집
dataset = []
for item in golden_qa:
    context, answer = rag_service.answer_with_context(item["question"])
    dataset.append({
        "user_input": item["question"],
        "retrieved_contexts": [context],
        "response": answer,
        "reference": item["reference"],
    })
    print(f"완료: {item['question']}")

evaluation_dataset = EvaluationDataset.from_list(dataset)

# 4. RAGAS 채점용 LLM/임베딩
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=DEFAULT_MODEL, api_key=OPENAI_API_KEY))
evaluator_embeddings = LangchainEmbeddingsWrapper(LangchainOpenAIEmbeddings(api_key=OPENAI_API_KEY))

# 5. 4대 지표 평가
result = evaluate(
    dataset=evaluation_dataset,
    metrics=[
        Faithfulness(),
        ResponseRelevancy(),
        LLMContextPrecisionWithReference(),
        LLMContextRecall(),
    ],
    llm=evaluator_llm,
    embeddings=evaluator_embeddings,
)

print("\n=== RAGAS 평가 결과 (전체 평균) ===")
print(result)

df = result.to_pandas()
print("\n=== 질문별 상세 결과 ===")
print(df)
