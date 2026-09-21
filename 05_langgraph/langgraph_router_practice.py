"""
6-1. LangGraph State/Node/Edge 기본 구조.
Phase 5-4의 라우팅 패턴(classify() + if/else)을 StateGraph의 조건부 엣지로 재구현한다.
"""

import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

from manufacturing_data import MAINTENANCE_SCHEDULE


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.",  
}


# ---------- State Schema (Pydantic) ----------
class AgentState(BaseModel):
    user_message: str
    category: str | None = None
    result: str | None = None


class RouteDecision(BaseModel):
    category: Literal["오류_진단", "정비_일정", "일반_문의"]
    reason: str



# ---------- 노드 함수들 ----------


def route_node(state: AgentState) -> dict:
    """5-4의 classify()를 그래프 노드로 재구현 (few-shot 그대로 재사용)."""
    completion  = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "사용자 문의를 아래 세 카테고리 중 하나로 분류하세요.\n"
                "- 오류_진단: 특정 설비의 오류코드/증상에 대한 원인·조치 문의\n"
                "- 정비_일정: 다음 점검일/담당자 문의\n"
                "- 일반_문의: 그 외 일반적인 질문"
            )},
            {"role": "user", "content": "HS-ROBOT-A7에서 E-108 오류 났는데 뭐가 문제야?"},
            {"role": "assistant", "content": '{"category": "오류_진단", "reason": "특정 설비명과 오류코드를 언급하며 원인을 묻고 있음"}'},
            {"role": "user", "content": "HS-CONV-200 다음 점검일이 언제로 잡혀있어?"},
            {"role": "assistant", "content": '{"category": "정비_일정", "reason": "특정 설비의 다음 점검일을 묻고 있음"}'},
            {"role": "user", "content": state.user_message},
        ],
        response_format=RouteDecision,
    )
    decision = completion.choices[0].message.parsed
    print(f"[라우터] 분류: {decision.category} ({decision.reason})")
    return {"category": decision.category}



def diagnosis_node(state: AgentState) -> dict:
    """진단 에이전트 노드."""
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"알려진 오류코드 정보: {ERROR_CODES}\n이 정보를 바탕으로 답하세요."},
            {"role": "user", "content": state.user_message},            
        ],
    )
    return {"result": completion.choices[0].message.content}

def schedule_node(state: AgentState) -> dict:
    """정비 일정 에이전트 노드."""
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"정비 일정 데이터: {MAINTENANCE_SCHEDULE}\n이 정보를 바탕으로 답하세요."},
            {"role": "user", "content": state.user_message},
        ],
    )
    return {"result": completion.choices[0].message.content}

def general_node(state: AgentState) -> dict:
    """일반 문의 노드"""
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "제조 설비 관련 일반적인 질문에 간단히 답하세요."},
            {"role": "user", "content": state.user_message}
        ],
    )
    return {"result": completion.choices[0].message.content}

def route_condition(state: AgentState) -> str:
    """조건부 엣지: category 값을 보고 다음 노드 이름을 반환한다."""
    return {"오류_진단": "diagnosis", "정비_일정": "schedule", "일반_문의": "general"}[state.category]



# ---------- 그래프 조립 ----------
graph = StateGraph(AgentState)
graph.add_node("route", route_node)
graph.add_node("diagnosis", diagnosis_node)
graph.add_node("schedule", schedule_node)
graph.add_node("general", general_node)
graph.add_edge(START, "route")
graph.add_conditional_edges("route", route_condition, {
    "diagnosis": "diagnosis",
    "schedule": "schedule",
    "general": "general",
})
graph.add_edge("diagnosis", END)
graph.add_edge("schedule", END)
graph.add_edge("general", END)

app = graph.compile()


# ---------- 실행 ----------
for question in [
    "HS-CNC-450X에서 E-204 오류 뜨는데 뭐가 문제야?",
    "HS-ROBOT-A7 다음 점검은 언제로 잡혀있어?",
    "설비 점검은 보통 왜 주기적으로 하는거야?",
]:
    print(f"\n질문: {question}")
    final_state = app.invoke(AgentState(user_message=question))
    print(f"답변: {final_state['result']}")
