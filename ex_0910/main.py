import json
import os
from enum import Enum
from typing import Annotated, Optional
from fastapi import FastAPI, HTTPException, Path, Query, Body, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="타이타닉 승객 장부 기록 시스템 API",
    description="JSON DB 기반의 타이타닉 승객 데이터 CRUD API",
    version="1.0.0"
)

# JSON DB 파일 경로 설정
DB_FILE_PATH = "db.json"


# --- 1. JSON 파일 입출력 헬퍼 함수 ---
def load_db() -> dict:
    """JSON 파일에서 데이터를 읽어옵니다. 파일이 없으면 초기 구조를 생성합니다."""
    if not os.path.exists(DB_FILE_PATH):
        initial_data = {"passengers": {}}
        save_db(initial_data)
        return initial_data
    
    with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data: dict) -> None:
    """데이터를 JSON 파일에 저장합니다."""
    with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- 2. Enum 및 Pydantic 모델 정의 ---
class SexEnum(str, Enum):
    male = "male"
    female = "female"

class EmbarkedEnum(str, Enum):
    C = "C"  # Cherbourg
    Q = "Q"  # Queenstown
    S = "S"  # Southampton

class Passenger(BaseModel):
    pclass: int = Field(..., ge=1, le=3, description="티켓 등급 (1, 2, 3)")
    name: str = Field(..., description="승객 이름")
    sex: SexEnum = Field(..., description="성별 (male/female)")
    age: Optional[float] = Field(None, ge=0, description="나이")
    sibsp: int = Field(0, ge=0, description="동승한 형제자매/배우자 수")
    parch: int = Field(0, ge=0, description="동승한 부모/자녀 수")
    ticket: str = Field(..., description="티켓 번호")
    fare: float = Field(..., ge=0.0, description="운임 요금")
    cabin: Optional[str] = Field(None, description="객실 번호")
    embarked: Optional[EmbarkedEnum] = Field(None, description="탑승 항구 (C, Q, S)")
    survived: Optional[int] = Field(None, ge=0, le=1, description="생존 여부 (0: 사망, 1: 생존)")

# Path 및 Query 검증 타입 정의
ValidPassengerId = Annotated[int, Path(gt=0, description="양의 정수 승객 ID (PassengerId)")]
SearchQuery = Annotated[Optional[str], Query(max_length=20, description="검색어 (이름 검색용, 최대 20자)")]


# --- 3. 엔드포인트 구현 ---

@app.get("/")
def read_root():
    return {"message": "타이타닉 승객 장부 기록 시스템 API에 오신 것을 환영합니다."}

# [GET] 승객 전체/검색 조회
@app.get("/passengers/")
async def get_passengers(q: SearchQuery = None):
    db = load_db()
    passengers = db["passengers"]

    # 검색어가 들어온 경우 이름(name) 기준 필터링
    if q:
        filtered_passengers = {
            pid: data for pid, data in passengers.items()
            if q.lower() in data.get("name", "").lower()
        }
        return {
            "message": f"'{q}' 검색 결과 조회 완료",
            "total_count": len(filtered_passengers),
            "data": filtered_passengers
        }

    return {
        "message": "전체 승객 목록 조회 완료",
        "total_count": len(passengers),
        "data": passengers
    }

# [GET] 단일 승객 조회
@app.get("/passengers/{passenger_id}")
async def read_passenger(passenger_id: ValidPassengerId):
    db = load_db()
    str_id = str(passenger_id)

    if str_id not in db["passengers"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger with ID {passenger_id} not found"
        )

    return {
        "passenger_id": passenger_id,
        "data": db["passengers"][str_id]
    }

# [POST] 승객 등록
@app.post("/passengers/{passenger_id}", status_code=status.HTTP_201_CREATED)
async def create_passenger(
    passenger_id: ValidPassengerId,
    passenger: Annotated[Passenger, Body(description="생성할 승객 데이터")]
):
    db = load_db()
    str_id = str(passenger_id)

    if str_id in db["passengers"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Passenger ID {passenger_id} already exists"
        )

    db["passengers"][str_id] = passenger.model_dump()
    save_db(db)

    return {
        "message": "Passenger registered successfully",
        "passenger_id": passenger_id,
        "data": db["passengers"][str_id]
    }

# [PUT] 승객 정보 수정
@app.put("/passengers/{passenger_id}")
async def update_passenger(
    passenger_id: ValidPassengerId,
    passenger: Annotated[Passenger, Body(description="수정할 승객 정보")]
):
    db = load_db()
    str_id = str(passenger_id)

    if str_id not in db["passengers"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger ID {passenger_id} not found"
        )

    previous_data = db["passengers"][str_id]
    db["passengers"][str_id] = passenger.model_dump()
    save_db(db)

    return {
        "message": "Passenger information updated successfully",
        "passenger_id": passenger_id,
        "previous_data": previous_data,
        "updated_data": db["passengers"][str_id]
    }

# [DELETE] 승객 기록 삭제
@app.delete("/passengers/{passenger_id}")
async def delete_passenger(passenger_id: ValidPassengerId):
    db = load_db()
    str_id = str(passenger_id)

    if str_id not in db["passengers"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger ID {passenger_id} not found"
        )

    deleted_passenger = db["passengers"].pop(str_id)
    save_db(db)

    return {
        "message": f"Passenger ID {passenger_id} deleted successfully",
        "deleted_passenger_id": passenger_id,
        "deleted_data": deleted_passenger
    }