"""
RAG 파이프라인 1단계: Overlapping 청킹 + 다국어 임베딩 + Chroma 벡터DB 적재 + 검색.
아직 LLM 생성은 붙이지 않고, "검색이 잘 되는지"만 먼저 확인한다.
"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


load_dotenv()

# 3-3에서 만든 Overlapping 청킹 함수 재사용
def overlapping_chunk(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunks.append(text[i:i + chunk_size])

    return chunks

sample_text = (
    "인공지능은 컴퓨터가 인간처럼 학습하고 추론하는 기술이다. "
    "머신러닝은 인공지능의 한 분야로, 데이터를 통해 스스로 패턴을 찾아낸다. "
    "딥러닝은 머신러닝의 한 갈래로, 인공신경망을 여러 층으로 쌓아 복잡한 패턴을 학습한다. "
    "이러한 기술들은 이미지 인식, 자연어 처리, 추천 시스템 등 다양한 분야에 활용된다."
)

# 1. 청킹 -> LangChain의 Document 객체로 변환
chunks = overlapping_chunk(sample_text, 80, 20)
documents = [Document(page_content=c) for c in chunks]
print(f"총 정크 개수: {len(documents)}")

# 2. 임베딩 모델 (3-2에서 성능 검증된 다국어 모델 재사용)
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")

# 3. 벡터DB에 적재
vectorstore = Chroma.from_documents(documents, embeddings)

# 4. 검색기(retriever) 생성 -> 질문과 가장 유사한 상위 k개 정크를 반환
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 5. 검색 테스트
query = "딥러닝이 뭐야"
results = retriever.invoke(query)

print(f"\n질문: {query}")
print("검색된 청크:")
for i, doc in enumerate(results):
    print(f"[{i}] {doc.page_content}")


# -------------- 생성 단계 추가 -----------------

# 6. 검색된 Document 리스트 -> 프롬프트에 넣을 하나의 문자열로 합치기
def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


# 7. 생성 모델 + 프롬프트
model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

rag_prompt = ChatPromptTemplate.from_messages({
    ("system", "당신은 주어진 [문맥]만 근거로 답하는 어시스턴트입니다. "
              "문맥에 없는 내용은 모른다고 답하세요.\n\n[문맥]\n{context}"),
    ("user", "{question}"),
})

# 8. LCEL로 전체 RAG 체인 조립
#   - retriever가 문서를 찾고 -> format_docs가 문자열로 합치고 -> "context"에 채움
#   - RunnablePassthrough()는 입력(question)을 그대로 통과시켜 "question"에 채움
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)

# 9. 실행
answer = rag_chain.invoke(query)
print(f"\n[RAG 답변]\n{answer}")