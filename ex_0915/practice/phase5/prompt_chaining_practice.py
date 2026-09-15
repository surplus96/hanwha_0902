"""
5-4-1. 프롬프트 체이닝: 작업을 순차 단계로 쪼개, 각 LLM 호출이 이전 단계의 출력을 입력으로 받는다.
시나리오: 자유 텍스트 오류 신고 -> 구조화 파싱 -> 진단 요약 -> 작업지시서 초안 생성.
"""


import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부화. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다."
}

# ---------- 1단계: 자유 텍스트 신고 -> 구조화 파싱 ----------
class IncidentReport(BaseModel):
    equipment: str
    error_code: str
    symptom_summary: str

raw_report = "CNC 기계에서 빨간 경고등 들어오고 이상한 소리가 나요. 화면에 E-204라고 떠 있어요. 설비는 HS-CNC-450X입니다."

step1 = client.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "사용자의 자유 텍스트 오류 신고에서 설비명, 오류코드, 증상 요약을 추출하세요."},
        {"role": "user", "content": raw_report},
    ],
    response_format=IncidentReport,
)
incident = step1.choices[0].message.parsed
print(f"[1단계: 구조화 파싱]\n{incident}\n")


# ---------- 2단계: 구조화 정보로 진단 요약 ----------
raw_cause = ERROR_CODES.get((incident.equipment, incident.error_code), "등록된 정보 없음")

step2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "아래 원인 정보를 바탕으로, 현장 작업자가 이해하기 쉬운 진단 요약을 2문장으로 작성하세요."},
        {"role": "user", "content": f"설비: {incident.equipment}\n오류코드: {incident.error_code}\n"
                                    f"등록된 원인/조치: {raw_cause}\n신고된 증상: {incident.symptom_summary}"},
    ],
)
diagnosis = step2.choices[0].message.content
print(f"[2단계: 진단 요약]\n{diagnosis}\n")


# ---------- 3단계: 진단 요약 -> 정식 작업지시서 초안 ----------
class WorkOrderEvaluation(BaseModel):
    passed: bool
    reason: str


def evaluate_work_order(equipment: str, error_code: str, original_cause: str, draft: str) -> WorkOrderEvaluation:
    """작업지시서 초안이 형식/내용 기준을 모두 만족하는지 채점한다."""
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (
                "당신은 작업지시서 검수 담당자입니다. 아래 기준을 모두 만족해야 통과(pass: true)입니다. "
                "하나라도 위반하면 반드시 실패(pass: false)로 판정하고, reason에 어떤 기준을 왜 위반했는지 "
                "구체적으로 적으세요. 통과한 경우에도 reason에 어떤 기준을 어떻게 만족했는지 한 줄로 적으세요.\n\n"
                "# 검수 기준\n"
                f"1. [설비명] 필드에는 정확히 설비 모델명 '{equipment}'이 들어가야 한다 (부품명이나 다른 표현으로 대체되면 안 됨).\n"
                f"2. [오류코드] 필드에는 정확히 오류코드 '{error_code}'가 들어가야 한다 (증상 설명이 아니라 코드 자체여야 함).\n"
                "3. [설비명]/[오류코드]/[긴급도]/[진단 요약]/[요청 조치] 5개 필드가 모두 빠짐없이 존재해야 한다.\n"
                "4. [원문]에 있는 전문용어(부품명 등)가 [작업지시서 초안]에 오타 없이 정확히 반영되어야 한다 "
                "(예: '주축'을 '추축'으로 쓰면 위반).\n"
                "5. [긴급도]가 '긴급'이면 [진단 요약]이나 [요청 조치]에 그 근거(안전 위험, 즉시 중단 필요 등)가 드러나야 한다."
            )},
            {"role": "user", "content": f"[원문]\n{original_cause}\n\n[작업지시서 초안]\n{draft}"},
        ],
        response_format=WorkOrderEvaluation,
    )
    return completion.choices[0].message.parsed


def generate_work_order_with_optimization(
    diagnosis: str, original_cause: str, equipment: str, error_code: str, max_attempts: int = 3
) -> str:
    """생성 -> 평가 -> (실패 시) 피드백과 함께 재생성을 최대 max_attempts번 반복한다."""
    feedback = ""
    draft = ""
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- 생성 시도 {attempt} ---")
        user_content = diagnosis if not feedback else (
            f"{diagnosis}\n\n[이전 시도 피드백] {feedback}\n위 피드백을 반영해서 다시 작성하세요."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "아래 진단 내용을 바탕으로 정비팀에 전달할 정식 작업지시서를 작성하세요. "
                                                "형식: [설비명] / [오류코드] / [긴급도(긴급·일반)] / [진단 요약] / [요청 조치]"},
                {"role": "user", "content": user_content},  # <- 이 줄이 빠져 있었습니다
            ],
        )

        draft = response.choices[0].message.content
        print(f"생성된 초안:\n{draft}")

        evaluation = evaluate_work_order(equipment, error_code, original_cause, draft)
        print(f"평가 결과: pass={evaluation.passed}, reason={evaluation.reason}")

        if evaluation.passed:
            return draft

        feedback = evaluation.reason

    print("최대 시도 횟수 도달 - 마지막 결과를 그대로 반환합니다 (fail-poen).")
    return draft

work_order = generate_work_order_with_optimization(diagnosis, raw_cause, incident.equipment, incident.error_code)
print(f"\n[최종 작업지시서]\n{work_order}")

