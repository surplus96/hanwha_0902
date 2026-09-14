"""
Parent Document Retriever 실습: 작은 단위(child)로 정밀 검색하되,
실제 생성에는 그 문장을 포함하는 더 큰 부모 문서(parent)를 통째로 넘긴다.
"""

from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_core.stores import InMemoryStore
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# manufacturing.txt 전체를 "부모 문서" 하나로 취급
with open("docs/manufacturing.txt", "r", encoding="utf-8") as f:
    text = f.read()
parent_doc = Document(page_content=text, metadata={"source": "manufacturing.txt"})

# child_splitter: 검색 정밀도를 위해 아주 작은 단위(약 문장 하나 수준)로 쪼갠다
child_splitter = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=0)

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-small")
vectorstore = Chroma(embedding_function=embeddings, collection_name="parent_doc_practice")
docstore = InMemoryStore()  # 부모 문서 원문을 통째로 저장해두는 곳

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,   # child 청크의 임베딩이 저장되는 곳 (검색은 여기서)
    docstore=docstore,         # parent 문서 원문이 저장되는 곳 (실제로 반환되는 건 여기서)
    child_splitter=child_splitter,
)
retriever.add_documents([parent_doc])

query = "E-108 오류의 원인이 뭐야?"
results = retriever.invoke(query)

print(f"검색된 결과 개수: {len(results)}")
for i, doc in enumerate(results):
    print(f"[{i}] 반환된 길이: {len(doc.page_content)}자 (전체 원문: {len(text)}자)")
