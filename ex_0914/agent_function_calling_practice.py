"""
5-2. Function Calling: OpenAI 네이티브 함수 호출 API로 도구 3개를 연동.
5-1에서 텍스트로 손수 파싱하던 것을, 구조화된 JSON 스키마로 모델이 직접
"어떤 함수를, 어떤 인자로 부를지" 결정하게 한다.
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

from manufacturing_data import SPARE_PARTS_INVENTORY, MAINTENANCE_SCHEDULE

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.",
    ("HS-CNC-450X", "E-207"): "냉각수 수위 부족 경고. 보충 후 30분 이내 재발하면 냉각 펌프 점검이 필요합니다.",
    ("HS-ROBOT-A7", "E-108"): "서보 드라이버 통신 이상. 컨트롤러 재부팅 후에도 반복되면 케이블 커넥터를 점검해야 합니다.",
    ("HS-ROBOT-A7", "E-115"): "관절 각도 허용 범위 초과. 수동 모드로 전환해 원점을 재설정해야 합니다.",
    ("HS-CONV-200", "E-315"): "벨트 슬립(미끄러짐) 감지. 텐셔너를 재조정하면 대부분 해결됩니다.",
    ("HS-PRESS-800", "E-501"): "유압 압력 이상(긴급). 즉시 중단하고 유압 라인 누유를 점검해야 합니다.",
    ("HS-WELD-12", "E-620"): "아크 불안정. 접지 상태와 와이어 공급 장력을 점검해야 합니다.",
}


def lookup_error_code(model: str, code: str) -> str:
    return ERROR_CODES.get((model, code), "해당 오류코드 정보를 찾을 수 없습니다.")


def check_parts_stock(part_name: str) -> dict:
    info = SPARE_PARTS_INVENTORY.get(part_name)
    return info if info else {"error": f"'{part_name}' 부품 정보를 찾을 수 없습니다."}


def check_maintenance_schedule(equipment: str) -> dict:
    info = MAINTENANCE_SCHEDULE.get(equipment)
    return info if info else {"error": f"'{equipment}' 정비 일정 정보를 찾을 수 없습니다."}


# 모델이 호출할 함수 이름 -> 실제 파이썬 함수
AVAILABLE_TOOLS = {
    "lookup_error_code": lookup_error_code,
    "check_parts_stock": check_parts_stock,
    "check_maintenance_schedule": check_maintenance_schedule,
}

# 모델에게 "이런 도구들이 있다"고 알려주는 스키마 (JSON Schema 형식)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "lookup_error_code",
            "description": "설비의 오류코드에 대한 원인과 조치 방법을 조회한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {"type": "string", "description": "설비 모델명, 예: HS-CNC-450X"},
                    "code": {"type": "string", "description": "오류코드, 예: E-204"},
                },
                "required": ["model", "code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_parts_stock",
            "description": "특정 부품의 현재 재고 수량과, 재고가 없을 경우 리드타임을 조회한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "part_name": {"type": "string", "description": "부품명, 예: 스핀들 베어링"},
                },
                "required": ["part_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_maintenance_schedule",
            "description": "특정 설비의 다음 정기점검 예정일과 담당 기술자를 조회한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "equipment": {"type": "string", "description": "설비 모델명, 예: HS-CNC-450X"},
                },
                "required": ["equipment"],
            },
        },
    },
]

messages = [
    {"role": "system", "content": "당신은 제조 설비 문제해결 에이전트입니다. 필요하면 도구를 사용해 정확한 정보를 확인한 뒤 답하세요."},
    {"role": "user", "content": "HS-CNC-450X에서 E-204 오류가 떴어. 수리에 필요한 스핀들 베어링 재고 있어? 그리고 다음 정기점검은 언제야?"},
]

for turn in range(6):
    print(f"\n--- Turn {turn + 1} ---")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS_SCHEMA,
    )
    message = response.choices[0].message
    messages.append(message.model_dump())

    if not message.tool_calls:
        print(f"=== 최종 답변 ===\n{message.content}")
        break

    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        print(f"모델이 요청한 도구 호출: {func_name}({func_args})")

        result = AVAILABLE_TOOLS[func_name](**func_args)
        print(f"도구 실행 결과: {result}")

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else str(result),
        })
else:
    print("최대 턴 수에 도달했습니다.")
