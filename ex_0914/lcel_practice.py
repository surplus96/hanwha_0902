"""
LCEL(LangChain Expression Language) 파이프 문법 최소 실습.
main.py의 무관한 독립 스크립트 -> 'python lcel_practice.py' 로 직접 실행.
"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# 1. 모델 (Runnable)'
model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


# 2. 프롬프트 템플릿 (Runnable) - {topic}은 나중에 invoke()에서 채워질 변수
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 개념을 한 문장으로 아주 쉽게 설명하는 선생님입니다."),
    ("user", "{topic}이 뭔지 한 문장으로 설명해줘."),
])

# 3. 출력 파서 (Runnable) - 모델의 복잡한 응답 객체를 순수 문자열로 변환
output_parser = StrOutputParser()

# 파이프로 연결: 프롬프트 -> 모델 -> 파서
chain = prompt | model | output_parser

# 체인 실행
result = chain.invoke({"topic": "하네스 엔지니어링"})
print(result)