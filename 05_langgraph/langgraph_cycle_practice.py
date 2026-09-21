"""
6-2. 조건 분기와 순환(cyclic) 그래프: Phase 5의 평가자-최적화자 재시도 루프를
그래프의 사이클로 재구현한다. "실패하면 다시 생성 노드로 돌아간다"가 순환의 핵심. 
"""


import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.",
}



class WorkOrderState(BaseModel):
    diagnosis: str
    equipment: str
    error_code: str
    original_cause: str
    draft: str = ""
    feedback: str = ""
    passed: bool = False
    attempt: int = 0
    max_attempts: int = 3


class WorkOrderEvaluation(BaseModel):
    passed: bool
    reason: str


def generate_node(state: WorkOrderState) -> dict:
    user_content = state.diagnosis if not state.feedback else (
        f"{state.diagnosis}\n\n[이전 시도 피드백] {state.feedback}\n위 피드백을 반영해서 다시 작성하세요."
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "아래 진단 내용을 바탕으로 정비팀에 전달할 정식 작업지시서를 작성해주세요. "
                                            "형식: [설비명] / [오류코드] / [긴급도(긴급·일반)] / [진단 요약] / [요청 조치]"},
            {"role": "user", "content": user_content},
        ],
    )

    draft = completion.choices[0].message.content
    print(f"\n--- 생성 시도 {state.attempt + 1} ---\n{draft}")
    return {"draft": draft, "attempt": state.attempt + 1}


def evaluate_node(state: WorkOrderState) -> dict:
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "당신은 작업지시서 검수 담당자입니다. 아래 기준을 모두 만족해야 통과(pass: true)입니다.\n"
                f"1. [설비명]에 정확히 '{state.equipment}'가 들어가야 한다.\n"
                f"2. [오류코드]에 정확히 '{state.error_code}'가 들어가야 한다.\n"
                "3. 5개 필드가 모두 존재해야 한다.\n"
                "4. [원문]의 전문용어가 오타 없이 반영되어야 한다."
            )},
            {"role": "user", "content": f"[원문]\n{state.original_cause}\n\n[작업지시서 초안]\n{state.draft}"},
        ],
        response_format=WorkOrderEvaluation,
    )
    evaluation = completion.choices[0].message.parsed
    print(f"평가: pass={evaluation.passed}, reason={evaluation.reason}")
    return {"passed": evaluation.passed, "feedback": evaluation.reason}

def should_retry(state: WorkOrderState) -> str:
    """조건부 엣지: 통과했거나 최대 시도 도달 -> 종료, 아니면 -> 다시 생성(순환)."""
    if state.passed or state.attempt >= state.max_attempts:
        return "end"
    return "retry"

graph = StateGraph(WorkOrderState)
graph.add_node("generate", generate_node)
graph.add_node("evaluate", evaluate_node)

graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges("evaluate", should_retry, {
    "retry": "generate", # <- 순환: evaluate에서 다시 generate로 되돌아감
    "end": END,
})


app = graph.compile()


initial_state = WorkOrderState(
    diagnosis="HS-CNC-450X의 주측 모터가 과부하 상태입니다. 즉시 가공을 냉각 시스템을 점검하세요.",
    equipment="HS-CNC-450X",
    error_code="E-204",
    original_cause=ERROR_CODES[("HS-CNC-450X", "E-204")],
)


final_state = app.invoke(initial_state)
print(f"\n[최종 작업지시서 - {final_state['attempt']}번째 시도에서 확정]\n{final_state['draft']}")