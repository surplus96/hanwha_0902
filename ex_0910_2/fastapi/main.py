"""
FastAPI 백엔드 스켈레톤

Streamlit 프론트엔드(streamlit_app.py)와 분리된 백엔드 서버.
Gemini API 호출 로직을 여기로 옮기고, Streamlit은 이 서버에 HTTP 요청만 보내는 구조.

실행 방법:
    uvicorn main:app --reload --port 8000

필요 패키지:
    pip install fastapi uvicorn python-dotenv google-genai pydantic
"""

import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai
from pydantic import BaseModel

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY가 .env에 설정되어 있지 않습니다.")

# 서버 전역에서 재사용할 Gemini 클라이언트 (요청마다 새로 만들지 않음)
client = genai.Client(api_key=GEMINI_API_KEY)

# 세션별 채팅 히스토리를 메모리에 보관 (재시작하면 초기화됨 -> 추후 Redis/DB 등으로 교체 가능)
chat_sessions: dict[str, "genai.chats.Chat"] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행할 초기화 로직 (필요시 여기에 추가)
    yield
    # 서버 종료 시 정리 로직 (필요시 여기에 추가)
    chat_sessions.clear()


app = FastAPI(title="Gemini Chat Backend", lifespan=lifespan)

# Streamlit(로컬 개발 시 기본 8501 포트)에서의 요청을 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 요청/응답 스키마 ----------

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # 없으면 새 세션 생성
    model: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class NewSessionResponse(BaseModel):
    session_id: str


# ---------- 유틸 ----------

def get_or_create_session(session_id: str | None, model: str | None) -> tuple[str, "genai.chats.Chat"]:
    """session_id가 없거나 존재하지 않으면 새 채팅 세션을 만들어 반환."""
    if session_id and session_id in chat_sessions:
        return session_id, chat_sessions[session_id]

    new_id = session_id or str(uuid.uuid4())
    chat_sessions[new_id] = client.chats.create(model=model or DEFAULT_MODEL)
    return new_id, chat_sessions[new_id]


# ---------- 라우트 ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/session", response_model=NewSessionResponse)
def create_session(model: str | None = None):
    """새 채팅 세션을 생성하고 session_id를 반환."""
    session_id, _ = get_or_create_session(None, model)
    return NewSessionResponse(session_id=session_id)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """세션에 메시지를 보내고 전체 응답을 한 번에 받는다 (스트리밍 아님)."""
    session_id, chat_session = get_or_create_session(req.session_id, req.model)

    try:
        response = chat_session.send_message(req.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API 호출 실패: {e}")

    return ChatResponse(session_id=session_id, reply=response.text)


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """세션에 메시지를 보내고 스트리밍으로 응답을 받는다 (Streamlit st.write_stream과 호환)."""
    session_id, chat_session = get_or_create_session(req.session_id, req.model)

    def event_generator():
        try:
            for chunk in chat_session.send_message_stream(req.message):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[오류] Gemini API 호출 실패: {e}"

    return StreamingResponse(event_generator(), media_type="text/plain")


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """세션 삭제 (대화 초기화)."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    del chat_sessions[session_id]
    return {"status": "deleted", "session_id": session_id}