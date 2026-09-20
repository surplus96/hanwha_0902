"""
5-4-3. 병렬화: 여러 하위 작업(관점)을 동시에 처리한 뒤 결과를 합친다.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INCIDENT = "HS-CNC-450X에서 오류코드 E-204(주축 모터 과부하)가 발생했습니다. 현재 생산 라인이 가동 중단된 상태입니다."

PERSPECTIVES = {
    "안전": "당신은 현장 안전 담당자입니다. 아래 사고 상황의 안전 위험도를 평가하세요.",
    "생산": "당신은 생산 관리자입니다. 아래 사고 상황이 생산 일정에 미치는 영향을 평가하세요.",
    "정비": "당신은 정비 기술자입니다. 아래 사고 상황의 수리 난이도와 예상 소요 시간을 평가하세요.",
}

def evaluate_from_perspective(role: str, system_prompt: str) -> tuple[str, str]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt + " 3문장 이내로 답하세요."},
            {"role": "user", "content": INCIDENT},
        ],
    )
    return role, response.choices[0].message.content


start = time.time()

#병렬 실행: 3개 관점 평가를 동시에 요청 (순차 호출이었다면 3번의 API 왕복 시간이 그대로 합산됐을 것)
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(evaluate_from_perspective, role, prompt) for role, prompt in PERSPECTIVES.items()]
    results = dict(f.result() for f in futures)

print(f"3개 관점 병렬 평가 소요 시간: {time.time() - start:.2f}초\n")


for role, opinion in results.items():
    print(f"[{role} 관점]\n{opinion}\n")

# 취합(aggregate): 세 관점을 총합해 하나의 최종 의사결정으로 합침
synthesis_prompt = "\n\n".join(f"[{role} 관점]\n{opinion}" for role, opinion in results.items())


final = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "아래 세관점의 평가를 총합해서, 이 사고에 대한 최종 대응 우선순위와 권고사항을 정리하세요."},
        {"role": "user", "content": synthesis_prompt},
    ],
)
print(f"=== 총합 결론 ===\n{final.choices[0].message.content}")