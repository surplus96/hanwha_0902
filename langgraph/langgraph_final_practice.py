"""
6-4. HITL + 멀티에이전트 그래프 최종 통합.
6-1(라우팅) 구조에, "긴급" 등급 진단에는 사람의 승인을 기다리는 HITL 체크포인트를 추가한다.
"""

import os
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import operator
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

from manufacturing_data import MAINTENANCE_SCHEDULE

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 심각도 정보를 포함한 오류코드 DB (docs/manufacturing.txt의 "긴급/일반" 구분 반영)
ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): {"cause": "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.", "severity": "일반"},
    ("HS-PRESS-800", "E-501"): {"cause": "유압 압력 이상. 즉시 중단하고 유압 라인 누유를 점검해야 합니다.", "severity": "긴급"},
}


class SupervisorState(BaseModel):
    user_message: str
    category: str | None = None
    equipment: str | None = None
    error_code: str | None = None
    severity: str | None = None
    diagnosis: str | None = None
    perspectives: Annotated[list[str], operator.add] = []  # <- 추가: 병렬 노드들이 각자 append
    approved: bool | None = None
    result: str | None = None



class RouteDecision(BaseModel):
    category: Literal["오류_진단", "정비_일정", "일반_문의"]
    reason: str


class IncidentExtraction(BaseModel):
    equipment: str
    error_code: str


def route_node(state: SupervisorState) -> dict:
    completion = client.chat.completions.parse(
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
    print(f"[라우터] {decision.category}")
    return {"category": decision.category}


def diagnosis_node(state: SupervisorState) -> dict:
    """오류코드를 추출하고, DB에서 원인/심각도를 조회한다."""
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "사용자 문의에서 설비명과 오류코드를 추출하세요."},
            {"role": "user", "content": state.user_message},
        ],
        response_format=IncidentExtraction,
    )
    extracted = completion.choices[0].message.parsed
    info = ERROR_CODES.get((extracted.equipment, extracted.error_code), {"cause": "등록된 정보 없음", "severity": "일반"})
    print(f"[진단] {extracted.equipment}/{extracted.error_code} -> {info['severity']}")
    return {
        "equipment": extracted.equipment,
        "error_code": extracted.error_code,
        "diagnosis": info["cause"],
        "severity": info["severity"],
    }


def schedule_node(state: SupervisorState) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"정비 일정 데이터: {MAINTENANCE_SCHEDULE}\n이 정보를 바탕으로 답하세요."},
            {"role": "user", "content": state.user_message},
        ],
    )
    return {"result": completion.choices[0].message.content}


def general_node(state: SupervisorState) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "제조 설비 관련 일반적인 질문에 간단히 답하세요."},
            {"role": "user", "content": state.user_message},
        ],
    )
    return {"result": completion.choices[0].message.content}

def safety_perspective_node(state: SupervisorState) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 현장 안전 담당자입니다. 아래 사고 상황의 안전 위험도를 2문장 이내로 평가하세요."},
            {"role": "user", "content": state.diagnosis},
        ],
    )
    return {"perspectives": [f"[안전] {completion.choices[0].message.content}"]}


def production_perspective_node(state: SupervisorState) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 생산 관리자입니다. 아래 사고 상황이 생산에 미치는 영향을 2문장 이내로 평가하세요."},
            {"role": "user", "content": state.diagnosis},
        ],
    )
    return {"perspectives": [f"[생산] {completion.choices[0].message.content}"]}


def maintenance_perspective_node(state: SupervisorState) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 정비 기술자입니다. 아래 사고 상황의 수리 난이도를 2문장 이내로 평가하세요."},
            {"role": "user", "content": state.diagnosis},
        ],
    )
    return {"perspectives": [f"[정비] {completion.choices[0].message.content}"]}


def approval_node(state: SupervisorState) -> dict:
    """HITL 체크포인트: 병렬로 모인 3개 관점을 같이 보여주고 승인을 기다린다."""
    perspectives_text = "\n".join(state.perspectives)
    decision = interrupt({
        "message": f"[승인 필요] {state.equipment}에서 {state.error_code}(긴급) 발생.\n\n{perspectives_text}\n\n"
                   f"현장 책임자에게 즉시 보고를 진행할까요?",
        "diagnosis": state.diagnosis,
    })
    print(f"[승인 재개] 사람의 결정: {decision}")
    return {"approved": decision}



def finalize_node(state: SupervisorState) -> dict:
    if state.severity == "긴급":
        if state.approved:
            result = f"[긴급 승인됨] {state.equipment} {state.error_code}: {state.diagnosis} -> 현장 책임자에게 즉시 보고되었습니다."
        else:
            result = f"[긴급 반려됨] {state.equipment} {state.error_code}: {state.diagnosis} -> 보고가 보류되었습니다."
    else:
        result = f"{state.equipment} {state.error_code}: {state.diagnosis}"
    return {"result": result}


def route_condition(state: SupervisorState) -> str:
    return {"오류_진단": "diagnosis", "정비_일정": "schedule", "일반_문의": "general"}[state.category]


def severity_condition(state: SupervisorState) -> list[str]:
    """긴급이면 3개 관점 평가로 팬아웃, 아니면 바로 finalize."""
    return ["safety", "production", "maintenance"] if state.severity == "긴급" else ["finalize"]


graph = StateGraph(SupervisorState)
graph.add_node("route", route_node)
graph.add_node("diagnosis", diagnosis_node)
graph.add_node("schedule", schedule_node)
graph.add_node("general", general_node)
graph.add_node("approval", approval_node)
graph.add_node("finalize", finalize_node)

graph.add_edge(START, "route")
graph.add_conditional_edges("route", route_condition, {
    "diagnosis": "diagnosis", "schedule": "schedule", "general": "general",
})
graph.add_node("safety", safety_perspective_node)
graph.add_node("production", production_perspective_node)
graph.add_node("maintenance", maintenance_perspective_node)
graph.add_node("merge_perspectives", lambda state: {})  # 팬인 지점 - 아무것도 안 하고 병합만 기다림

graph.add_conditional_edges("diagnosis", severity_condition, {
    "safety": "safety", "production": "production", "maintenance": "maintenance", "finalize": "finalize",
})
graph.add_edge("safety", "merge_perspectives")
graph.add_edge("production", "merge_perspectives")
graph.add_edge("maintenance", "merge_perspectives")
graph.add_edge("merge_perspectives", "approval")

graph.add_edge("approval", "finalize")
graph.add_edge("finalize", END)
graph.add_edge("schedule", END)
graph.add_edge("general", END)

# HITL(interrupt)이 동작하려면 반드시 checkpointer가 필요하다 - 정지된 상태를 저장해둬야
# 나중에 재개(resume)할 수 있기 때문이다.
app = graph.compile(checkpointer=InMemorySaver())


# ---------- 실행: 긴급 케이스로 HITL 테스트 ----------
config = {"configurable": {"thread_id": "demo-1"}}

result = app.invoke(
    SupervisorState(user_message="HS-PRESS-800에서 E-501 오류 떴어, 이거 뭐야?"),
    config=config,
)

if "__interrupt__" in result:
    interrupt_info = result["__interrupt__"][0].value
    print(f"\n*** 그래프 일시 정지 ***\n{interrupt_info['message']}\n")

    human_decision = True  # 사람이 승인한다고 가정
    final_result = app.invoke(Command(resume=human_decision), config=config)
    print(f"\n[최종 결과]\n{final_result['result']}")
else:
    print(f"\n[최종 결과]\n{result['result']}")
