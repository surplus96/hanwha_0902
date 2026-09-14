# AI 에이전트 서비스 구축 교육 가이드
### 한화시스템 교육 커리큘럼 7단계 정합 버전

> 실습 베이스: Phase 1에서 처음부터 직접 구축하는 Streamlit + FastAPI + Gemini 스트리밍 챗봇 → 이후 전 Phase에서 같은 프로젝트를 계속 확장
> 각 Phase는 "이전 단계의 한계를 직접 겪은 뒤 → 새 개념/도구로 해결"하는 순서로 설계되어 있습니다. 프레임워크를 먼저 배우고 적용하는 대신, 문제를 먼저 만나게 하는 것이 목적입니다.

---

## 전체 로드맵

| Phase | 주제 | 핵심 산출물 |
|---|---|---|
| 1 | AI 서비스 백엔드 프로그래밍 실무 | 견고한 FastAPI+Streamlit 챗봇 (Python 기초 포함) |
| 2 | AI-Native 아키텍처 및 테스트 공학 | Harness 계층 설계 + 출력 검증 파이프라인 |
| 3 | LLM 오케스트레이션 및 파이프라인 구축 | LCEL 기반 RAG 파이프라인 v1 |
| 4 | 실무형 RAG 시스템 구축 및 최적화 | Advanced RAG (하이브리드 검색 + 정량 평가 포함) |
| 5 | AI 에이전트 기획 및 툴 연동 실무 | Function Calling 에이전트 + 5대 워크플로 패턴 실습 |
| 6 | 멀티 에이전트 제어 및 파이프라인 자동화 | LangGraph 멀티에이전트 + MCP 연동 |
| 7 | 엔터프라이즈 AI 에이전트 배포 및 상용화 | TDD + Clean Architecture로 리팩토링된 배포 가능 서비스 |

---

## Phase 1. AI 서비스 백엔드 프로그래밍 실무

> 이 Phase는 **완전히 처음부터** 진행합니다. 아직 FastAPI도, Streamlit도, LLM 연동 코드도 없는 빈 폴더에서 출발해, 이 Phase의 마지막에 "세션 기반 스트리밍 챗봇"을 직접 완성하는 것이 목표입니다. 각 절은 이전 절에서 만든 결과물 위에 쌓아 올라갑니다.

### 1-1. 파이썬 심화 문법 (클래스 · 데코레이터 · 예외 처리 · 로깅)
프레임워크를 붙이기 전에, 아래 4가지를 **작은 독립 스크립트**로 먼저 손에 익힙니다.
- **클래스**: 간단한 데이터 클래스(예: `Message`, `Config`)를 정의해보고, 속성·메서드·`__init__`을 다뤄봅니다.
- **데코레이터**: 함수 실행 시간을 재는 `@timeit` 데코레이터를 직접 만들어보며 "함수를 감싸는 함수"의 동작 원리를 체득합니다. (이후 FastAPI의 `@app.post(...)`가 사실 같은 원리라는 것을 1-4에서 연결합니다.)
- **예외 처리**: `try/except`로 사용자 정의 예외 클래스(`class InvalidInputError(Exception)`)를 만들고 잡아보는 연습.
- **로깅**: `print` 대신 `logging` 모듈로 레벨(INFO/WARNING/ERROR)을 구분해 출력하는 습관을 처음부터 들입니다.

### 1-2. async/await 및 asyncio
- 아직 웹 서버 없이, 순수 Python 스크립트로 동기 함수와 `async def` 함수의 차이를 실험합니다. 예: `time.sleep(2)`를 쓰는 동기 함수 2개를 순차 실행했을 때와, `asyncio.sleep(2)`를 쓰는 비동기 함수 2개를 `asyncio.gather`로 동시 실행했을 때 걸리는 시간을 직접 비교합니다.
- 자가 점검: 왜 비동기 버전이 더 빠른가? "이벤트 루프가 블로킹되지 않는다"는 것이 정확히 무슨 의미인가?

### 1-3. Pydantic BaseModel 데이터 검증
- 아직 API 없이, `BaseModel`을 상속한 클래스(예: `ChatMessage(role: str, content: str)`)를 직접 정의해보고, 잘못된 타입을 넣었을 때 `ValidationError`가 나는 것을 확인합니다.
- Optional 필드(`session_id: str | None = None`)와 커스텀 validator(`@field_validator`)를 추가해, "코드가 아니라 스키마로 규칙을 강제한다"는 감각을 익힙니다.

### 1-4. FastAPI RESTful API 설계
지금까지 익힌 문법을 처음으로 FastAPI 위에 올립니다.
1. `GET /health` 하나만 있는 최소 FastAPI 앱 실행 → `uvicorn`으로 띄우고 브라우저/curl로 확인
2. 1-3에서 만든 Pydantic 모델을 요청/응답 스키마로 사용하는 `POST /session` 엔드포인트 추가 (세션 ID 발급)
3. REST 설계 원칙 적용: 리소스 중심 경로(`/session`, `/chat`) 설계, 적절한 상태 코드와 에러 응답 규격화, 1-1에서 만든 커스텀 예외를 FastAPI exception handler로 연결

### 1-5. FastAPI 심화 기능 및 Streamlit UI 연동
1. LLM API(Gemini 등) 클라이언트를 연동해 `POST /chat` 엔드포인트 완성 — 세션 ID를 키로 대화 히스토리를 메모리(dict)에 저장하는 구조를 직접 설계
2. `StreamingResponse`로 `/chat/stream` 엔드포인트를 추가하며 스트리밍 응답의 동작 원리를 익힘
3. Streamlit로 별도 프론트엔드를 새로 작성: `st.chat_input`으로 입력받고, `st.session_state`로 세션 ID를 보관하고, `st.write_stream`으로 `/chat/stream` 응답을 실시간 렌더링
4. 완성 후 자가 점검: 세션 dict는 서버를 재시작하면 어떻게 되는가? 동기 방식(`/chat`)과 스트리밍 방식(`/chat/stream`)은 사용자 체감상 무엇이 다른가?

### Phase 1 실습 체크리스트
- [ ] 클래스·데코레이터·예외처리·로깅 각각 독립 스크립트로 실습
- [ ] 동기 vs 비동기 실행 시간 비교 스크립트 작성 및 결과 확인
- [ ] Pydantic 모델 + 커스텀 validator로 데이터 검증 실습
- [ ] `GET /health` → `POST /session` → `POST /chat` 순서로 FastAPI 앱 처음부터 구축
- [ ] `/chat/stream`(`StreamingResponse`) 엔드포인트 추가
- [ ] Streamlit 프론트엔드를 새로 작성해 백엔드와 연동, 전체 챗봇 완성

---

## Phase 2. AI-Native 아키텍처 및 테스트 공학

### 왜 필요한가
일반 소프트웨어는 같은 입력에 같은 출력을 내는 결정론적 시스템입니다. LLM 애플리케이션은 **같은 입력에도 다른 출력**이 나올 수 있는 비결정론적 컴포넌트를 핵심에 품고 있습니다. 2026년 업계에서는 이 비결정성을 다루는 별도 엔지니어링 체계를 "Harness Engineering"이라 부르며, Prompt Engineering → Context Engineering → **Harness Engineering**으로 이어지는 계보로 설명합니다.

### 2-1. AI-Native 아키텍처 설계 원칙
- 핵심 원칙: **"반드시 지켜야 하는 결정론적 규칙은 코드/런타임으로 강제하고, LLM에게는 판단이 필요한 부분만 맡긴다."** 예를 들어 "출력은 반드시 유효한 JSON이어야 한다"는 것을 프롬프트로 부탁하는 대신, 구조화 출력(JSON Schema 강제) + 파싱 실패 시 재시도 로직으로 코드가 강제합니다.
- 도메인 로직과 LLM 호출 로직을 분리하는 설계 — Phase 7의 Clean Architecture로 이어지는 예고편입니다.

### 2-2. Prompt 설계
- 시스템 프롬프트를 역할·규칙·출력 형식·금지사항 섹션으로 구조화하고, few-shot 예시를 배치하는 전략을 다룹니다.

### 2-3. Context 구성 (Context Engineering)
- "AI 엔지니어링에서 진짜 중요한 스킬은 프롬프팅이 아니라 컨텍스트 엔지니어링"이라는 인식이 업계에 정착되어 있습니다. 컨텍스트 엔지니어링은 "모델이 각 시점에 정확히 무엇을 보는지"를 설계하는 일 — 대화 히스토리 압축, 검색 결과 주입 순서, 도구 정의 배치 등을 포함합니다.
- 실전 원칙: 메모리/기록 파일은 짧게 유지하고 세부 내용은 링크로 분리하며, 원문 로그를 매번 프롬프트에 통째로 넣지 않고 검색 가능한 저장소에 둡니다. 이 프로젝트에서는 세션 대화 이력을 Redis 같은 외부 저장소로 옮기는 실습이 이 원칙의 실전 적용 대상이 됩니다.

### 2-4. Harness 엔지니어링
- 정의: **모델을 감싸는 결정론적 런타임 레이어** — 모델이 제안한 모든 행동을 검증(validate)·인가(authorize)·실행(execute)·기록(log)하는 계층입니다. "모델은 행동을 제안하고, 하네스가 그것을 통제한다"는 역할 분리가 핵심입니다.
- 검증 방식 2종류:
  - **Computational checks**: 린터, 유닛테스트, 스키마 검증처럼 결정론적으로 판정 가능한 검사
  - **Inferential checks**: LLM-as-judge처럼 또 다른 LLM 호출로 품질을 판정하는 검사
- 이 프로젝트에서의 최소 실습 범위: 지금의 `/chat/stream` 엔드포인트에 (1) 입력 길이/형식 검증(computational), (2) 출력이 금지어를 포함하는지 간단 필터(computational), (3) 선택적으로 응답 품질을 LLM 한 번 더 호출해 채점(inferential) — 이 세 겹을 하네스 계층으로 명시적으로 분리해서 구현합니다.

### 2-5. LLM 출력 검증
- 구조화 출력 강제(Pydantic 스키마 + 구조화 출력 API), 파싱 실패 시 재시도(retry-with-feedback) 패턴을 다룹니다.
- LLM-as-judge를 이용한 자동 채점 — Phase 4의 RAG 평가(RAGAS)와 Phase 7의 TDD형 에이전트 테스트로 자연스럽게 연결됩니다.

### Phase 2 실습 체크리스트
- [ ] 시스템 프롬프트를 역할/규칙/출력형식 섹션으로 구조화해 별도 파일로 관리
- [ ] 구조화 출력(JSON Schema) 강제 + 파싱 실패 시 재시도 로직 구현
- [ ] "제안(모델) → 검증(하네스) → 실행" 3단계로 최소 1개 엔드포인트 리팩토링
- [ ] Computational check 1개 + Inferential check(LLM-as-judge) 1개 구현

---

## Phase 3. LLM 오케스트레이션 및 파이프라인 구축

### 3-1. LangChain LCEL 기본 오케스트레이션 체인
- `Runnable`/`|` 파이프 문법으로 "검색 → 프롬프트 조립 → LLM 호출"을 체이닝하는 방식을 다룹니다. `AgentExecutor`는 레거시 API(2026년 12월까지 유지보수 모드로만 남음)이므로 신규 학습에서는 배제하고, `create_agent()` 또는 LangGraph `StateGraph` 기준으로 진행합니다.
- 패키지 구조: `langchain-core`(모델/프롬프트/`Runnable` 등 기초 추상화), `langchain`(`create_agent` 등 고수준 API), `langgraph`(상태 기반 그래프 실행 엔진, Phase 6에서 본격 학습).

### 3-2. 임베딩 모델 선택 · 차원 · 성능 비교

| 기준 | 설명 |
|---|---|
| 차원(dimension) | 차원이 클수록 표현력↑이지만 저장 공간·검색 속도 비용↑. 1536차원(OpenAI 계열)이 흔한 기본값이지만, 필요 시 차원을 잘라 쓰는 모델도 등장하고 있습니다. |
| 언어 지원 | 한국/미국 증시 리서치처럼 한국어·영어를 함께 다루는 도메인은 **한국어 성능이 검증된 임베딩 모델**이 필수입니다 — 다국어 임베딩(BGE-M3, multilingual-e5 등)과 영어 전용 모델을 비교 실습합니다. |
| 벤치마크 | MTEB(Massive Text Embedding Benchmark) 리더보드로 검색(retrieval) 태스크 점수를 확인합니다. |
| 비용/지연 | API 호출형 vs 로컬 오픈소스 모델의 트레이드오프를 비교합니다. |

### 3-3. Chunking 전략

| 전략 | 설명 | 장점 | 단점 | 적합한 경우 |
|---|---|---|---|---|
| Fixed-size | 고정 길이로 단순 분할 | 구현 간단, 예측 가능 | 문맥·의미 경계 무시 | 로그 등 정형 데이터 |
| Overlapping | 인접 청크 간 일부 중복 | 문맥 보존, 검색 포괄성↑ | 저장 공간 증가 | 문서 검색 일반 |
| Recursive | 문맥 단위가 너무 크면 재귀적으로 재분할 | 의미 단위 보존 | 구현 복잡도↑ | 구조화된 문서(마크다운 등) |
| Semantic | 문장 임베딩 유사도로 경계 결정 | 의미적으로 응집된 청크 | 임베딩 비용 추가 | 품질 우선 시나리오 |

### 3-4. Chroma · FAISS 벡터DB 임베딩 적재 및 RAG 파이프라인 통합
- 로컬에서 다루기 쉬운 Chroma 또는 FAISS로 시작해, 이후 pgvector 등으로 교체 가능하도록 추상화된 구조로 설계합니다. 인덱스 알고리즘은 대부분의 경우 **HNSW**가 기본 권장값입니다(recall과 속도의 균형이 좋음).

### Phase 3 실습 체크리스트
- [ ] 임베딩 모델 2종(예: 다국어 vs 영어전용) 비교 실습 — 동일 한국어 질의로 검색 품질 차이 확인
- [ ] Overlapping 청킹 + 임베딩 파이프라인 구현
- [ ] Chroma/FAISS 적재 및 top-K 검색 구현
- [ ] LCEL로 RAG 체인 1차 완성본 구성

---

## Phase 4. 실무형 RAG 시스템 구축 및 최적화

### 왜 필요한가
Phase 3에서 만든 RAG는 "질문 임베딩 → top-K 검색 → 그대로 프롬프트에 주입"하는 Naive RAG입니다. 실무에서는 이 단계에서 발생하는 구체적 실패 유형(모호한 질문의 낮은 재현율, 키워드 매칭 실패, 문맥 부족)을 진단하고 기법별로 해결합니다.

### 4-1. Advanced RAG 검색 품질 진단
- 실패 유형별 원인 분류: 검색 실패(retrieval failure, 관련 문서를 못 찾음) vs 생성 실패(generation failure, 찾았는데 답을 못 만듦)를 구분하는 진단 습관을 먼저 들입니다.

### 4-2. Multi-Query / Query Rewriting
- 하나의 질문을 여러 관점으로 재작성해 각각 검색 후 결과를 합치는 기법(LangChain `MultiQueryRetriever`). 모호하거나 정보가 부족한 질문에서 재현율(recall)을 끌어올리는 데 효과적입니다.
- 알려진 한계: 재작성된 질의들이 서로 "거의 동일하고 다양성이 부족"해지는 경우가 흔합니다 — 다양성을 명시적으로 유도하는 재작성 전략(예: 정보량이 다른 여러 버전 생성)이 실무 개선 포인트로 다뤄집니다.

### 4-3. 하이브리드 검색
- Dense(임베딩 기반 의미 검색) + Sparse(BM25 기반 키워드 검색)를 함께 사용하고, 가중치 파라미터로 두 방식의 비중을 조절합니다. 고유명사·종목코드·법령 조항 번호처럼 "의미보다 정확한 키워드 매칭이 중요한 질의"에서 Dense 검색만으로는 놓치는 경우를 실습으로 재현한 뒤 하이브리드로 해결하는 순서로 진행하면 효과적입니다.

### 4-4. Parent Document Retriever (Small-to-Big)
- 작은 단위(문장/소청크)로 정밀하게 검색하되, 실제 LLM에게는 그 문장을 포함하는 더 큰 부모 청크(또는 원문 문서)를 통째로 넘겨 문맥을 보존하는 기법입니다. "검색 단위"와 "생성에 필요한 문맥 단위"가 다르다는 문제를 해결합니다. Sentence-window retrieval도 같은 계열의 기법입니다.

### 4-5. Self-RAG
- 모델이 스스로 판단하도록 만드는 반성(reflection) 개념을 도입합니다 — "이 질문에 검색이 필요한가?", "검색된 문서가 실제로 관련 있는가?", "생성한 답변이 검색 근거에 의해 뒷받침되는가?"를 매 단계 모델 자신이 판정합니다. Phase 2의 출력 검증, Phase 6의 LangGraph 분기 개념과 자연스럽게 이어지는 대목입니다.

### 4-6. RAG 품질 평가
업계 표준 4대 지표(RAGAS 프레임워크 기준):

| 지표 | 의미 |
|---|---|
| Faithfulness(충실성) | 생성된 답변이 검색된 근거에서 실제로 뒷받침되는가 |
| Answer Relevancy(답변 관련성) | 답변이 질문에 실제로 부합하는가 |
| Context Precision(문맥 정밀도) | 검색된 청크들이 실제로 관련 있는가 |
| Context Recall(문맥 재현율) | 정답에 필요한 정보가 검색된 문맥에 실제로 포함되어 있는가 |

- 실습: 10~20개 질의로 구성된 골든 데이터셋을 직접 만들고, RAGAS로 4개 지표를 채점합니다. Phase 4-2~4-4에서 만든 기법 적용 전/후 점수를 비교해 "어떤 기법이 어떤 지표를 개선했는지" 정량적으로 확인합니다.

### Phase 4 실습 체크리스트
- [ ] Naive RAG의 실패 사례 3개 이상 직접 수집(검색 실패/생성 실패 구분)
- [ ] Multi-Query Retriever 적용 및 재현율 변화 확인
- [ ] 하이브리드 검색(BM25+Dense) 구현 및 키워드 매칭 케이스 개선 확인
- [ ] Parent Document Retriever로 문맥 보존 개선 확인
- [ ] 골든 데이터셋 기반 RAGAS 4대 지표 측정 및 리포트 작성

---

## Phase 5. AI 에이전트 기획 및 툴 연동 실무

### 왜 이 순서인가
LangChain/LangGraph 같은 프레임워크를 심화 학습하기 전에, **프레임워크 없이 에이전트의 최소 동작 원리**를 먼저 만져보는 단계입니다. 프레임워크는 이 원리를 코드로 편하게 감싸주는 도구일 뿐이라는 걸 먼저 체감해야, Phase 6에서 LangGraph를 "왜" 쓰는지 이해가 빨라집니다.

### 5-1. 에이전트 관찰 → 판단 → 행동 루프
에이전트의 본질은 화려한 자율성이 아니라 **환경 피드백을 근거로 삼아 루프 안에서 도구를 쓰는 LLM**입니다.

```
1. 사람이 목표를 준다 (또는 대화로 범위를 좁힌다)
2. LLM이 계획하고 도구를 호출한다
3. 환경이 결과를 돌려준다 = 그라운드 트루스(ground truth)
4. 그 결과를 보고 다시 판단한다 (반복 또는 종료)
```
- 실습: 프레임워크 없이 순수 Python `while` 루프 + LLM API 호출만으로 이 4단계를 직접 구현합니다 — "에이전트"라는 것이 특별한 마법이 아님을 확인하는 것이 목표입니다.

### 5-2. Function Calling으로 Tool 정의 · 연동 구현
- LLM 제공사 API의 네이티브 function calling 스펙으로 도구 1~2개(계산기, 날씨 조회 등)를 정의하고, 모델이 스스로 호출 여부와 인자를 결정하는 과정을 직접 관찰합니다.
- 이 경험이 Phase 6에서 LangChain의 Tool 추상화, MCP Tool을 이해하는 기초가 됩니다.

### 5-3. MCP(Model Context Protocol)로 도구·데이터 소스 표준 연결 — 개념 소개
- 이 단계에서는 "왜 도구 연동을 표준화해야 하는가"(하나의 서버를 여러 에이전트·프레임워크가 재사용하는 N×M 문제 해결)만 개념적으로 소개하고, 실제 서버 구축·연동 실습은 Phase 6에서 진행합니다.

### 5-4. Agent Pattern — 5가지 워크플로 패턴 구현
실무에서 반복적으로 쓰이는 에이전트 설계 패턴 5가지를 각각 최소 실습으로 구현합니다. 다섯은 서로 배타적이지 않으며, 실무 시스템은 대개 이들을 겹쳐서 씁니다(예: 라우팅 뒤에 프롬프트 체이닝을 두는 식).

| 패턴 | 개념 | 적합한 경우 |
|---|---|---|
| **프롬프트 체이닝** | 작업을 순차 단계로 쪼개 각 LLM 호출이 이전 단계 출력을 입력으로 받음 | 마케팅 카피 생성 후 번역, 개요 작성 후 기준 검증 후 본문 작성 등 |
| **라우팅** | 입력을 분류한 뒤 그 결과에 따라 적합한 후속 작업으로 연결 | 고객 문의를 일반/환불/기술지원 등으로 분기 |
| **병렬화** | 여러 하위 작업을 동시에 처리 후 결과를 합침 | 여러 문서를 동시에 요약, 여러 관점에서 동시 평가 |
| **오케스트레이터-워커** | 중앙 오케스트레이터가 작업을 하위 워커에게 동적으로 분배·집계 | 작업 범위가 사전에 고정되지 않는 복잡한 과업 |
| **평가자-최적화자** | 한 LLM이 생성하고 다른 LLM(또는 같은 모델)이 비평·개선을 반복 | 엄격한 품질 기준이 있는 창작/코드 생성 |

- 이 5가지는 Phase 6의 LangGraph StateGraph로 옮겨가면 각각 "노드+조건부 엣지"로 자연스럽게 표현됩니다 — 미리 개념을 익혀두면 Phase 6의 그래프 설계가 훨씬 쉬워집니다.

### Phase 5 실습 체크리스트
- [ ] 프레임워크 없이 순수 루프로 최소 에이전트 구현 (관찰-판단-행동)
- [ ] Function Calling으로 도구 1~2개 연동
- [ ] 5가지 패턴 중 최소 3개(프롬프트 체이닝, 라우팅, 병렬화)를 실제 코드로 구현
- [ ] (선택) 평가자-최적화자 패턴으로 Phase 2의 LLM-as-judge와 결합 실습

---

## Phase 6. 멀티 에이전트 제어 및 파이프라인 자동화

### 6-1. LangGraph State · Node · Edge로 그래프 기반 워크플로우 설계
- **StateGraph**: 노드(작업 단위)와 엣지(흐름/조건 분기)로 구성된 상태 기반 그래프. Chain이 "파이프라인"이라면 StateGraph는 "흐름도(flowchart)"에 가깝습니다.
- **State Schema**: 그래프 전체에서 공유되는 상태를 Pydantic 스키마로 명시적으로 정의합니다. 업계 보고서에 따르면 프로덕션 에이전트 장애의 60% 이상이 상태 관리 문제에서 비롯되므로, State Schema 설계를 신중히 다루는 것이 이 Phase의 핵심 학습 목표입니다.
- **Reducer**: 여러 노드가 동시에 같은 상태 필드를 갱신할 때 병합 규칙을 정의하는 함수(예: 메시지 리스트에 append).
- **Checkpointer**: 그래프 실행 상태를 Postgres/Redis 등에 영속화합니다. Phase 2에서 만든 세션 저장소를 이 시점에 LangGraph의 공식 체크포인터로 교체·연동하면, "Time-Travel Debugging"(과거 상태로 되돌려 재실행)도 가능해집니다.
- Phase 5에서 익힌 5가지 패턴이 이제 그래프의 노드/분기로 그대로 옮겨집니다: 라우팅 패턴 → 조건부 엣지, 병렬화 패턴 → 병렬 노드 실행 후 집계, 오케스트레이터-워커 → Supervisor 노드 구조.

### 6-2. 조건 분기와 순환(Cyclic) 그래프로 제어 흐름 구축
- 선형 체인의 한계(재시도·순환 불가)를 LangGraph의 순환 그래프로 해결하는 실습을 진행합니다.

### 6-3. MCP(Model Context Protocol)로 도구·데이터 소스 표준 연결 — 심화
- 2026년 7월 28일 발표된 MCP 2026-07-28 스펙 핵심: 완전 무상태(stateless) 프로토콜 코어 전환, `Mcp-Session-Id` 헤더 및 initialize 핸드셰이크 제거, Extensions 프레임워크(Tasks, MCP Apps), Multi Round-Trip Requests, OAuth 2.0/OIDC 정렬 인가 강화.
- **거버넌스 변화**: 2025년 12월, Anthropic이 MCP를 Linux Foundation 산하 신설 재단인 **AAIF(Agentic AI Foundation)**에 기부했습니다. OpenAI·Block과 공동 설립했으며 Google·Microsoft·AWS·Cloudflare·Bloomberg 등이 참여합니다. 이제 MCP는 특정 회사의 프로토콜이 아니라 **업계 공용 인프라**로 자리잡았습니다 — Kubernetes가 CNCF로 이관된 것과 유사한 흐름입니다.
- 실습용 MCP 서버 선택은 부록 A를 참고합니다.

### 6-4. Human-in-the-Loop(HITL) 구현 및 멀티 에이전트 그래프 설계 · 구현
- 특정 노드 실행 전 그래프를 일시 정지시키고 사람의 승인을 기다렸다가 재개하는 패턴 — 엔터프라이즈 요구사항(컴플라이언스, 위험한 액션 승인)에 필수적인 기능입니다.
- 실습 시나리오(Supervisor-Worker 골격):

```
사용자 질문
   │
   ▼
[라우터 노드] ── 이 질문의 성격은?
   │
   ├─▶ "일반 대화" → [대화 노드] → 응답
   ├─▶ "문서 검색 필요" → [RAG 노드] → 응답
   └─▶ "도구 호출 필요" → [Tool 노드] → (승인 필요 시 HITL 정지) → 응답
```

### Phase 6 실습 체크리스트
- [ ] Pydantic 기반 State Schema 설계 + Redis/Postgres Checkpointer 연동
- [ ] Phase 5의 라우팅·병렬화 패턴을 StateGraph 노드/엣지로 재구현
- [ ] 부록 A의 실습용 MCP 서버 중 최소 2개를 LangGraph Tool 노드에 연결
- [ ] HITL 체크포인트 1개 이상 구현 (승인 대기 → 재개)
- [ ] (최종) PM-MCP를 실제 도구로 연동한 통합 데모 완성

---

## Phase 7. 엔터프라이즈 AI 에이전트 배포 및 상용화

### 왜 필요한가
지금까지 만든 것은 "동작하는 프로토타입"입니다. 실제 조직에서 상용화하려면 협업 가능한 코드 구조, 테스트, 그리고 AI 시대에 맞는 개발 방법론이 필요합니다.

### 7-1. GitHub 협업 버전 관리 워크플로우
- 브랜치 전략(feature branch → PR → 리뷰 → merge), 커밋 컨벤션을 이 프로젝트 저장소에 실제로 적용합니다.

### 7-2. 클린 아키텍처 원칙으로 AI 모듈 설계
- 핵심 원칙: **도메인 로직(비즈니스 규칙)은 프레임워크·DB·LLM 제공사로부터 독립적이어야 하며, 모든 의존성은 도메인을 향해 안쪽으로 향한다(Dependency Inversion).**
- AI 프로젝트 적용 실전 원칙: LLM 호출부를 포트-어댑터로 감싸서, 테스트 시 실제 API 대신 목(mock)으로 교체 가능하게 만듭니다. "Gemini를 호출하는 서비스"와 "그 결과를 가공하는 도메인 로직"을 분리해두면, Gemini를 Claude로 교체하거나 테스트에서 가짜 응답으로 대체하는 일이 코드 한 곳만 바꾸면 되도록 설계할 수 있습니다.
- 이 프로젝트 적용 실습: 지금 `main.py`에 섞여 있는 "Gemini 클라이언트 생성/호출", "세션 관리", "HTTP 라우팅"을 계층별 모듈(예: `domain/`, `infrastructure/`, `api/`)로 분리합니다.

### 7-3. TDD(테스트 주도 개발) 실습
- AI 에이전트 코드에서 TDD를 적용하는 방식은 일반 코드와 다릅니다: **결정론적 부분(파싱, 검증, 라우팅 로직)은 일반 유닛테스트**로, **LLM 출력이 관여하는 부분은 Phase 2의 하네스 검증/LLM-as-judge를 테스트 조건으로** 사용합니다.
- 참고 원칙: 테스트 설계 위반의 상당수는 사실 DRY 원칙, 의존성 역전, 모듈 결합도 같은 일반 소프트웨어 설계 원칙 위반이기도 합니다 — AI 에이전트 코드라고 해서 TDD·클린 아키텍처의 근본 원칙이 달라지지 않습니다.

### 7-4. SDD(스킬 주도 개발) 방법론 실습 및 AI 모듈 설계
- **중요한 용어 구분**: "SDD"라는 약자는 업계에서 두 가지 다른 개념을 동시에 가리키고 있어 혼동하기 쉽습니다.
  - **Spec-Driven Development**(명세 주도 개발): 자연어 명세서를 코드보다 우선하는 원본 아티팩트로 삼는 방법론(GitHub Spec-Kit, AWS Kiro 등이 대표적 도구). 다만 2026년 현재 "과도한 문서화, 대규모 코드베이스에서 효율 저하" 등 한계도 함께 지적되고 있습니다.
  - **Skill-Driven Development**(스킬 주도 개발) — **본 커리큘럼이 다루는 개념**: 에이전트가 스스로 발견·조합할 수 있는 "스킬"을 설계의 출발점으로 삼는 방법론입니다. 각 스킬은 엄격한 계약(입출력 스키마), 의미론적 설명, 사전/사후 조건, 실패 모드, 조합 규칙을 명시적으로 정의한 자기 서술적(self-describing) 단위입니다. TDD·BDD·DDD를 대체하는 게 아니라, "에이전트가 자율적으로 능력을 찾아 쓰는" 상황에 특화된 보완적 방법론입니다.
- **연결 실습 제안**: 이미 운영 중인 skill 자산(예: 음악/영상 제작 파이프라인의 SKILL.md 체계, PM-MCP의 개별 도구들)이 사실상 Skill-Driven Development의 실전 사례에 해당합니다. 이번 실습은 그 경험을 "방법론으로서 명시화"하는 데 초점을 맞추면 습득이 훨씬 빠릅니다 — 예를 들어 도구 하나를 골라 입력 스키마·사전조건·실패 모드를 명시한 "스킬 계약" 형식으로 재문서화하는 실습을 진행합니다.

### Phase 7 실습 체크리스트
- [ ] GitHub 저장소에 브랜치 전략 적용 + PR 리뷰 1회 이상 실습
- [ ] `main.py`를 domain/infrastructure/api 계층으로 리팩토링
- [ ] 결정론적 로직에 대한 유닛테스트 + LLM 관여 로직에 대한 하네스 기반 테스트 작성
- [ ] 기존 도구 1개를 "스킬 계약" 형식으로 명시적으로 재문서화

---

## 부록 A. 실습용 MCP 서버

### A-1. 공식 레퍼런스 서버 현황 (2026년 9월 기준)

2025년, Anthropic이 유지하던 20종의 레퍼런스 MCP 서버 중 13종이 아카이브되고 **7종만 공식 유지보수**로 남았습니다(나머지는 GitHub·Slack·Postgres 등 각 벤더가 직접 유지보수하는 방식으로 이관). 오래된 블로그 글이 안내하는 "Anthropic의 GitHub/Slack MCP 서버"는 더 이상 최신이 아니므로 주의가 필요합니다.

| 서버 | 기능 | 교육 포인트 | 난이도 |
|---|---|---|---|
| **Time** | 시간/타임존 변환 | 가장 단순한 MCP 왕복(handshake, `tools/call`) 최소 경험용 | 최하 |
| **Fetch** | 웹 콘텐츠 수집·정제(HTML→Markdown) | "에이전트가 인터넷을 읽는다"는 개념, 커스텀 스크래퍼 없이 처리 | 하 |
| **Filesystem** | 파일 읽기/쓰기/검색(접근 제어 설정 가능) | 권한(access control) 경계 설계 개념과 함께 실습하기 좋음 | 하~중 |
| **Sequential Thinking** | 구조화된 단계별 사고 과정 지원 | Phase 5의 평가자-최적화자 패턴, 반성(reflection) 개념과 직결 | 중 |
| **Git** | Git 저장소 읽기/검색/조작 | Phase 7의 GitHub 워크플로우와 자연스럽게 연결(에이전트가 커밋 로그 분석 후 액션 제안) | 중 |
| **Memory** | 지식 그래프 기반 영속 메모리 | PM-MCP의 Obsidian vault 연동과 개념적으로 비교하기 좋음 | 중 |
| **Everything** | 프로토콜의 모든 기능(도구+리소스+프롬프트)을 한번에 노출하는 테스트/레퍼런스 서버 | MCP 스펙 전체를 조망하는 심화 마무리용 | 중~상 |

### A-2. 교육 진행 추천 순서

```
Time/Fetch  →  Filesystem  →  Sequential Thinking  →  Git  →  Memory  →  Everything  →  PM-MCP(캡스톤)
(왕복 경험)    (권한 개념)     (에이전트 패턴 연결)     (Phase7 연결)  (메모리 비교)  (스펙 총정리)   (실전 도메인)
```

- Phase 6 실습에서는 위 목록 중 최소 2개(예: Filesystem + Sequential Thinking)를 LangGraph Tool 노드에 연결해보고, Phase 6 마지막에 PM-MCP를 실제 캡스톤으로 연동합니다.
- **비용 참고**: MCP 서버 하나를 연결할 때마다 도구 스키마 주입으로 약 2,000~5,000 토큰이 소모됩니다. 여러 서버를 동시에 연결하는 실습에서는 이 비용을 실측해보는 것도 좋은 실습 포인트입니다(불필요한 서버는 연결 해제).

### A-3. 거버넌스 변화가 주는 시사점
- 2025년 12월, MCP는 **Linux Foundation 산하 AAIF(Agentic AI Foundation)**로 이관되었습니다(Anthropic·OpenAI·Block 공동 설립, Google·Microsoft·AWS·Cloudflare·Bloomberg 등 참여). 즉 특정 회사에 종속된 프로토콜이 아니라 업계 표준 인프라로 자리잡았다는 뜻이며, 교육에서는 "MCP는 이제 특정 벤더 기술이 아니라 웹의 REST처럼 범용 표준"이라는 관점으로 소개하는 것이 적절합니다.

---

## 부록 B. Phase 간 개념 연결 지도

```
Phase 2 하네스 검증(computational/inferential)  ──▶  Phase 4 RAGAS 평가, Phase 7 TDD 테스트 조건으로 재사용
Phase 2 Context Engineering(세션 압축)          ──▶  Phase 6 LangGraph Checkpointer 상태 관리로 발전
Phase 3 벡터 검색 로직                          ──▶  Phase 4 Advanced RAG 기법으로 정교화
Phase 5 Function Calling                        ──▶  Phase 6 Tool 노드 ──▶ MCP 도구로 대체/확장
Phase 5 5대 워크플로 패턴                       ──▶  Phase 6 StateGraph 노드/엣지 구조로 이식
Phase 6 MCP 실습(레퍼런스 서버)                 ──▶  Phase 7 스킬 계약 문서화 실습 대상
```

---

## 부록 C. 참고 리서치 출처 (2026년 기준)

- LangChain/LangGraph v1.0 LTS 및 `AgentExecutor` 폐지 동향 — DigitalApplied "LangChain vs LangGraph Comparison 2026", AYAutomate "LangGraph vs LangChain"
- LangGraph 상태 관리·Checkpointer·프로덕션 장애 통계 — Easton Dev "LangGraph State: Checkpoints, Threads, and Recovery"
- MCP 2026-07-28 스펙 및 AAIF 거버넌스 이관 — MCP 공식 블로그, RockB "Linux Foundation Agentic AI Foundation", ChatForest "The Agentic AI Foundation", mcp.directory
- 공식 레퍼런스 MCP 서버 현황(7종 유지/13종 아카이브) — TECHSY "15 Best MCP Servers 2026", modelcontextprotocol.io/examples
- RAG 청킹·벡터DB 선택 기준 — velog "벡터 DB(8) 원천 데이터 청킹 전략", wikidocs "1.6.3 벡터 데이터베이스"
- Advanced RAG 기법(Multi-Query, Parent-Child Chunking) — Atlan "12 Advanced RAG Techniques 2026", DMQR-RAG 논문(arXiv:2411.13154)
- RAG 평가 프레임워크(RAGAS 4대 지표) — Future AGI, QASkills.sh "Ragas Evaluation Complete Guide 2026", benchmarkingagents.com
- Harness Engineering 개념 — Martin Fowler "Harness Engineering for coding agent users"(Birgitta Böckeler), AddyOsmani.com "Agent Harness Engineering"
- Context Engineering 계보 — Philipp Schmid "The New Skill in AI is Context Engineering", Sarthak AI "Harness, Graph, and Loop Engineering"
- Agent 워크플로 패턴 5가지 — Anthropic "Building Effective Agents" 한국어 번역본(blogbyash.com)
- Skill-Driven Development 방법론 — Jean-Christophe Jamet, "Skill-Driven Development (SDD): Designing Software for the Age of Agents"
- Clean Architecture for AI — JAVAPRO International "AI without spaghetti", decodingai.com "How to Design Python AI Projects That Don't Fall Apart"
- FastAPI SSE 프로덕션 패턴·Redis 세션 이중화 — DevOpsBoys "LLM Streaming Responses with FastAPI and Anthropic SDK", Charles Sieg "Building an Enterprise Chatbot"

---

## 부록 D. 교육 진행 시 권장 순서

각 Phase는 다음 순서로 진행하는 것을 권장합니다.

1. 본 가이드의 해당 Phase 섹션 함께 읽기 (개념 선행)
2. 자가 점검 질문/한계 직접 겪어보기 (이전 Phase 코드로 문제 재현)
3. 실습 체크리스트 기준으로 코드 확장
4. 다음 Phase로 넘어가기 전, "이번 Phase에서 해결한 문제"와 "아직 남은 한계"를 정리

바로 다음 실습은 **Phase 1의 1-1(파이썬 심화 문법 독립 실습)**부터 시작해, 순서대로 1-5(Streamlit 연동)까지 완성한 뒤 **Phase 2(하네스 계층 설계)**로 넘어가면 됩니다.
