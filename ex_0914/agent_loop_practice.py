"""
5-1. 에이전트 관찰->판단->행동 루프: 프레임워크 없이 순수 while 루프로 구현.
"""

import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.",
    ("HS-ROBOT-A7", "E-108"): "서보 드라이버 통신 이상. 컨트롤러 재부팅 후에도 반복되면 케이블 커넥터를 점검해야 합니다.",
    ("HS-CONV-200", "E-315"): "벨트 슬립(미끄러짐) 감지. 텐셔너를 재조정하면 대부분 해결됩니다.",
}

def lookup_error_code(model: str, code: str) -> str:
    return ERROR_CODES.get((model, code), "해당 오류코드 정보를 찾을 수 없습니다.")

SYSTEM_PROMPT = """\
당신은 제조 설비 문제해결 에이전트입니다. 아래 두 가지 형식 중 하나로만 답하세요.

1) 정보가 더 필요하면:
TOOL_CALL: lookup_error_code(model="설비명", code="오류코드")

2) 이미 충분한 정보를 알고 있으면:
FINAL_ANSWER: 최종 답변 내용

한 턴에 하나의 형식만, 다른 설명 없이 출력하세요.
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "HS-CNC-450X에서 E-204 오류가 떴어. 어떻게 해야 해?"},
]

TOOL_CALL_PATTERN = re.compile(r'TOOL_CALL:\s*lookup_error_code\(model="([^"]+)",\s*code="([^"]+)"\)')

for turn in range(5):
    print(f"\n--- Turn {turn + 1}: 판단 ---")
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content
    print(f"모델 출력: {reply}")
    messages.append({"role": "assistant", "content": reply})

    if reply.startswith("FINAL_ANSWER:"):
        print(f"\n=== 최종 답변 ===\n{reply.removeprefix('FINAL_ANSWER:').strip()}")
        break

    match = TOOL_CALL_PATTERN.search(reply)
    if match:
        model_name, code = match.groups()
        print(f"--- Turn {turn + 1}: 행동 (도구 실행) ---")
        result = lookup_error_code(model_name, code)
        print(f"환경(도구) 결과: {result}")
        messages.append({"role": "user", "content": f"TOOL_RESULT: {result}"})
    else:
        print("형식을 인식하지 못했습니다. 종료합니다.")
        break
else:
    print("최대 턴 수에 도달했습니다.")
