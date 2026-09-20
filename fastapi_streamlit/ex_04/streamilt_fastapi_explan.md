## Streamlit 단일 구조 vs FastAPI + Streamlit 복합 구조

**기존 (Streamlit 단독)**
```
[브라우저] ↔ [Streamlit 프로세스]
                  └─ genai.Client 직접 호출 (API 키도 여기서 사용)
```
Streamlit 스크립트 안에서 Gemini API를 직접 호출합니다. UI 렌더링, 상태 관리, API 호출, 비즈니스 로직이 전부 한 프로세스, 한 파일 안에 섞여 있습니다.

**FastAPI + Streamlit (복합)**
```
[브라우저] ↔ [Streamlit 프로세스] ↔ HTTP ↔ [FastAPI 프로세스] ↔ [Gemini API]
                (UI만 담당)              (API 키 보관 + 비즈니스 로직)
```
Streamlit은 화면 렌더링과 사용자 입력만 담당하고, 실제 API 호출/세션 관리/비즈니스 로직은 별도 프로세스(FastAPI)가 담당합니다. 둘은 HTTP로만 통신합니다.

---

## 장단점 비교

| | Streamlit 단독 | FastAPI + Streamlit |
|---|---|---|
| **개발 속도** | 빠름 — 파일 하나로 끝 | 느림 — 서버 2개 관리, API 스펙 설계 필요 |
| **API 키 보안** | Streamlit 프로세스 안에 노출 (Streamlit Cloud 배포 시 secrets로 어느정도 보호되지만, 프론트/백 로직이 안 나뉨) | 백엔드에만 키 존재 — 프론트는 키를 전혀 모름. 나중에 웹/모바일 등 다른 프론트를 붙여도 키 재사용 가능 |
| **확장성** | 사용자 늘어나면 Streamlit 프로세스 자체가 병목. 로직을 다른 프론트(React, 모바일 앱 등)와 공유 불가 | 백엔드를 독립적으로 스케일링 가능. 같은 API를 여러 프론트엔드(웹, 모바일, Slack 봇 등)가 재사용 가능 |
| **배포 복잡도** | 서버 1개만 배포 | 서버 2개 배포 + CORS 설정 + 서버 간 네트워크 관리 필요 |
| **재사용성** | 로직이 Streamlit에 종속 (다른 데서 못 씀) | 비즈니스 로직이 API로 분리되어 다른 클라이언트에서도 호출 가능 |
| **디버깅** | 한 곳만 보면 됨 | 두 프로세스 로그를 따로 봐야 함 — 에러가 어느 쪽 문제인지 구분 필요 |
| **동시성/부하 처리** | Streamlit은 세션당 스레드 기반이라 대규모 동시 사용자 처리에 약함 | FastAPI(비동기 지원)는 API 서버로서 부하 처리, 캐싱, 큐잉 등을 붙이기 쉬움 |
| **테스트** | UI와 로직이 섞여 있어 로직만 따로 테스트하기 어려움 | API만 별도로 unit test / API test 가능 (pytest + httpx 등) |
| **버전 관리/팀 협업** | 프론트/백엔드 담당자가 같은 파일을 수정해야 해서 충돌 가능 | 프론트엔드 팀과 백엔드 팀이 API 스펙만 맞추면 독립적으로 작업 가능 |

## 언제 뭘 써야 하나

- **빠른 프로토타입, 개인 프로젝트, 내부 데모용 도구** → Streamlit 단독으로 충분합니다. 지금처럼 채팅 앱 하나 정도면 굳이 나눌 필요 없이 훨씬 빠르게 만들 수 있습니다.
- **실제 서비스로 키우거나, 여러 프론트엔드가 같은 로직을 써야 하거나, API 키/로직을 프론트에서 완전히 숨겨야 하거나, 트래픽이 늘어날 걸 대비해야 할 때** → FastAPI로 분리하는 게 맞습니다.

# FastAPI + Streamlit 복합 구조 개념 정리

## 1. 왜 나누는가

Streamlit은 **UI + 로직이 한 프로세스**에서 스크립트 형태로 동작하는 도구입니다.
사용자가 상호작용할 때마다 스크립트 전체가 **위에서 아래로 재실행**된다는 특징이 있습니다.

이 구조는 빠른 프로토타입에는 좋지만, 다음과 같은 상황에서 한계가 생깁니다.

- API 키/비즈니스 로직을 프론트엔드와 분리하고 싶을 때
- 여러 프론트엔드(웹, 모바일, 챗봇 등)가 같은 백엔드 로직을 공유해야 할 때
- 트래픽이 늘어나 백엔드만 별도로 확장(스케일링)해야 할 때
- 프론트/백엔드 팀이 독립적으로 작업해야 할 때

→ 그래서 **UI(Streamlit)** 와 **API 서버(FastAPI)** 를 분리하고, 둘을 HTTP로 통신시키는 구조를 씁니다.

---

## 2. 전체 아키텍처

```
[사용자 브라우저]
      ↓
[Streamlit 프로세스]  ← UI 렌더링, 사용자 입력 처리만 담당
      ↓  (HTTP 요청 — requests 라이브러리)
[FastAPI 프로세스]    ← 비즈니스 로직, API 키 보관, 외부 API 호출 담당
      ↓
[외부 API (Gemini 등)]
```

- 두 프로세스는 **완전히 독립적으로 실행**됩니다 (포트도 다름: Streamlit 기본 8501, FastAPI 8000).
- 서로의 존재를 몰라도 되고, HTTP 프로토콜(JSON 요청/응답)로만 대화합니다.
- 즉, FastAPI는 "누가 요청하는지"(Streamlit인지, 모바일 앱인지) 신경 쓸 필요가 없습니다.

---

## 3. 핵심 개념 정리

### 3-1. 클라이언트-서버 분리 (Frontend / Backend)

| 구분 | Streamlit (Frontend) | FastAPI (Backend) |
|---|---|---|
| 역할 | 화면, 입력창, 대화 표시 | API 키 보관, 세션 관리, 외부 API 호출 |
| 상태 관리 | `st.session_state` (브라우저 세션 단위) | 서버 메모리 or DB (모든 사용자 공용) |
| 재실행 방식 | 상호작용마다 스크립트 전체 재실행 | 요청(request)마다 함수만 실행, 프로세스는 계속 유지 |
| 키 노출 여부 | 노출 X (요청만 보냄) | 서버 내부에만 보관 |

### 3-2. REST API란

FastAPI가 제공하는 것은 결국 **URL + HTTP 메서드로 호출하는 함수**입니다.

```
POST /session        → 새 대화 세션 생성
POST /chat           → 메시지 보내고 답변 받기 (한 번에)
POST /chat/stream     → 메시지 보내고 답변을 스트리밍으로 받기
DELETE /session/{id}  → 세션 삭제
```

Streamlit은 이 URL들을 `requests.post(...)`로 호출할 뿐, 내부에서 Gemini가 어떻게 동작하는지는 전혀 몰라도 됩니다. → **관심사의 분리(Separation of Concerns)**

### 3-3. 세션(Session) 관리 — 왜 필요한가

Gemini 같은 대화형 API는 "이전 대화 맥락"을 기억해야 자연스러운 답변이 나옵니다.

- **Streamlit 단독일 때**: `st.session_state.chat_session`에 대화 객체를 저장 → 브라우저 탭(세션) 하나당 하나씩 유지
- **FastAPI 분리 후**: FastAPI는 매 요청마다 상태가 없는(stateless) 함수 호출이므로, 서버 쪽 메모리(`dict`)에 `session_id`를 key로 대화 객체를 저장해서 흉내냄

```python
chat_sessions: dict[str, Chat] = {}
```

Streamlit은 최초 1회 `/session`을 호출해 `session_id`를 발급받고, 이후 모든 요청에 그 id를 실어 보내서 "같은 대화"임을 서버에 알려줍니다.

> ⚠️ 메모리(`dict`) 기반 세션은 서버 재시작 시 사라지고, 여러 서버 인스턴스로 확장 시 공유되지 않습니다. 실서비스에서는 Redis 등 외부 저장소로 교체합니다.

### 3-4. 환경변수 / 시크릿 관리

| 방식 | 사용처 | 특징 |
|---|---|---|
| `.env` + `python-dotenv` | 일반 Python 스크립트, FastAPI | `os.getenv("KEY")`로 접근, `.gitignore` 필수 |
| `.streamlit/secrets.toml` | Streamlit 전용 | `st.secrets["KEY"]`로 접근, TOML 문법(따옴표 필수) |

이번 구조에서는 **Gemini API 키를 FastAPI 쪽 `.env`에만 두고**, Streamlit은 아예 키를 모르게 만드는 것이 핵심입니다. (프론트엔드에 시크릿을 두지 않는 것이 보안 원칙)

### 3-5. CORS (Cross-Origin Resource Sharing)

브라우저는 기본적으로 "다른 출처(포트/도메인)로의 요청"을 차단합니다.
Streamlit(8501)이 브라우저를 통해 FastAPI(8000)로 요청을 보내려면, FastAPI가 명시적으로 허용해줘야 합니다.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    ...
)
```

### 3-6. 스트리밍 응답

ChatGPT/Gemini 스타일의 "타이핑되듯 나오는" 응답은 **스트리밍**으로 구현됩니다.

- FastAPI: `StreamingResponse` + 제너레이터(`yield`)로 청크 단위 전송
- Streamlit: `requests.post(..., stream=True)` + `res.iter_content(...)`로 청크 수신 → `st.write_stream()`에 전달

세 계층(Gemini API → FastAPI → Streamlit) 모두 스트리밍을 "릴레이"해야 실제로 끊김없이 흘러나옵니다.

### 3-7. 클라이언트(Client) 객체 재사용

- **Streamlit**: 스크립트가 매번 재실행되므로, `genai.Client(...)`를 그냥 최상단에 두면 매번 새로 생성됨 → `@st.cache_resource`로 캐싱 필요
- **FastAPI**: 프로세스가 계속 살아있으므로 모듈 최상단에서 한 번만 생성하면 이후 모든 요청이 재사용 (별도 캐싱 데코레이터 불필요)

이 차이를 이해하지 못하면 "client가 닫혔다"는 식의 에러(`RuntimeError: Cannot send a request, as the client has been closed.`)를 만나게 됩니다.

---

## 4. 실전에서 자주 만나는 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| `StreamlitSecretNotFoundError` | `secrets.toml` 파일 자체가 없음 | `.streamlit/secrets.toml` 생성 |
| `ImportError: cannot import name 'genai' from 'google'` | `google-genai` 미설치 또는 네임스페이스 충돌 | `pip install google-genai`, 충돌 시 `pip uninstall google` |
| `AttributeError: 'Client' object has no attribute 'chat'` | OpenAI 문법과 google-genai 문법 혼동 | `client.models.generate_content()` / `client.chats.create()` 사용 |
| `RuntimeError: Cannot send a request, as the client has been closed.` | Streamlit 재실행마다 client가 새로 생성·소멸되는데 세션은 예전 client를 참조 | `@st.cache_resource`로 client 캐싱 |
| `ModuleNotFoundError: No module named 'google'` (설치했는데도) | `pip install google`로 **엉뚱한 패키지**(3.0.0, 스크래핑용) 설치함 | `pip uninstall google` 후 `pip install google-genai` |

---

## 5. 체크리스트 (배포/개발 전 확인)

- [ ] FastAPI `.env`에만 `GEMINI_API_KEY` 존재, Streamlit에는 없음
- [ ] `.env`, `secrets.toml` 모두 `.gitignore`에 등록
- [ ] FastAPI `client`는 모듈 전역에서 한 번만 생성
- [ ] Streamlit `client`(있다면) `@st.cache_resource`로 캐싱
- [ ] `session_id`를 Streamlit → FastAPI 요청마다 함께 전송
- [ ] CORS `allow_origins`에 Streamlit 주소 등록
- [ ] `pip list | findstr google`로 네임스페이스 충돌 패키지(`google` 단독) 없는지 확인
- [ ] 두 서버를 각각 다른 터미널에서 실행 (`uvicorn main:app --reload --port 8000` / `streamlit run streamlit_app.py`)

---

## 6. 한 줄 요약

> **Streamlit은 "보여주는 창구", FastAPI는 "일하는 두뇌"** — 이 둘을 HTTP라는 공통 언어로만 연결하면, 각자 독립적으로 교체·확장·재사용이 가능한 구조가 된다.