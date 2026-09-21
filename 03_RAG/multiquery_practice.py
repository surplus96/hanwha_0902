from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# (기존 vectorstore, retriever는 rag_practice.py에서 그대로 가져온다고 가정)

llm_for_rewrite = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=llm_for_rewrite,
)

# 동의어/다른 표현으로 일부러 어렵게 질문
query = "심층학습이 뭐야?"  # "딥러닝"의 동의어, 원본 문서엔 "딥러닝"이라고만 적혀있음

print("=== 기본 retriever (재작성 없음) ===")
for doc in retriever.invoke(query):
    print(f"- {doc.page_content[:50]}...")

print("\n=== MultiQueryRetriever (재작성 적용) ===")
for doc in multi_query_retriever.invoke(query):
    print(f"- {doc.page_content[:50]}...")
