"""
Chunking 전략 비교: Fixed-size vs Overalapping
같은 텍스트를 두 방식으로 잘라서, 청크 경계에서 문맥이 얼마나 보존되는지 직접 확인.
"""

sample_text = (
    "인공지능은 컴퓨터가 인간처럼 학습하고 추론하는 기술이다."
    "머신러닝은 인공지능의 한 분야로, 데이터를 통해 스스로 패턴을 찾아낸다."
    "딥러닝은 머신러닝의 한 갈래로, 인공신경망을 여러 층으로 쌓아 복잡한 패턴을 학습한다. "
    "이러한 기술들은 이미지 인식, 자연어 처리, 추천 시스템 등 다양한 분야에 활용된다."
)


def fixed_size_chunk(text: str, chunk_size: int) -> list[str]:
    """단순히 chunk_size 글자마다 자른다. 곂치는 부분 없음."""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

def overlapping_chunk(text: str, chunk_size: int, overlap: int) -> list[str]:
    """chunk_size 글자마다 자르되, overlap 글자만큼 앞 청크와 곂치게 한다."""

    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunks.append(text[i:i + chunk_size])
    return chunks

print("=== Fixed-size (chunk_size=40) ===")
for idx, chunk in enumerate(fixed_size_chunk(sample_text, 40)):   # 인자 2개만
    print(f"[{idx}] {chunk}")

print("\n=== Overlapping (chunk_size=40, overlap=10) ===")
for idx, chunk in enumerate(overlapping_chunk(sample_text, 40, 10)):
    print(f"[{idx}] {chunk}")