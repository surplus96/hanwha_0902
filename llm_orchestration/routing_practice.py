"""
5-4-2. 라우팅: 입력을 분류한 뒤, 그 결과에 따라 적합한 후속 작업으로 연결한다.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

from manufacturing_data import MAINTENANCE_SCHEDULE

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.",    
}

class RouteDecision(BaseModel):
    category: Literal["오류_진단", "정비_일정", "일반_문의"]
    reason: str



def classify(user_message: str) -> RouteDecision:
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "사용자 문의를 아래 세 카테고리 중 하나로 분류하세요.\n"
                "- 오류_진단: 특정 설비의 오류코드/증상에 대한 원인·조치 문의\n"
                "- 정비_일정: 다음 점검일/담당자 문의\n"
                "- 일반_문의: 그 외 일반적인 질문"
            )},
            # --- few-shot 예시 1: 오류_진단 ---
            {"role": "user", "content": "HS-ROBOT-A7에서 E-108 오류 났는데 뭐가 문제야?"},
            {"role": "assistant", "content": '{"category": "오류_진단", "reason": "특정 설비명과 오류코드를 언급하며 원인을 묻고 있음"}'},
            # --- few-shot 예시 2: 정비_일정 ---
            {"role": "user", "content": "HS-CONV-200 다음 점검일이 언제로 잡혀있어?"},
            {"role": "assistant", "content": '{"category": "정비_일정", "reason": "특정 설비의 다음 점검일을 묻고 있음"}'},
            # --- 실제 질문 ---
            {"role": "user", "content": user_message},
        ],
        response_format=RouteDecision,
    )
    return completion.choices[0].message.parsed


def handle_error_diagnosis(user_message: str) -> str:
    # 실제로는 여기서 5-2의 lookup_error_code 도구를 쓰지만, 라우팅 자체에 집중하기 위해 단순화
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"알려진 오류코드 정보: {ERROR_CODES}\n이 정보를 바탕으로 답하세요."},
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content

def handle_maintanance_schedule(user_message: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"정비 일정 데이터: {MAINTENANCE_SCHEDULE}\n이 정보를 바탕으로 답하세요."},
            {"role": "user", "content": user_message},
        ],  
    )
    return completion.choices[0].message.content

def handle_general(user_message: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "제조 설비 관련 일반적인 질문에 간단히 답하세요."},
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content


ROUTES = {
    "오류_진단": handle_error_diagnosis,
    "정비_일정": handle_maintanance_schedule,
    "일반_문의": handle_general,
    }

test_messages = [
    "HS-CNC-450X에서 E-204 오류 뜨는데 뭐가 문제야?",
    "HS-ROBOT-A7 다음 점검은 언제로 잡혀있어?",
    "설비 점검은 보통 왜 주기적으로 하는거야?",
]


for msg in test_messages:
    decision = classify(msg)
    print(f"\n질문: {msg}")
    print(f"분류: {decision.category} ({decision.reason})")
    handler = ROUTES[decision.category]
    print(f"답변: {handler(msg)}")





