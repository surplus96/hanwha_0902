import json
import os
from enum import Enum
from typing import Annotated, Optional
from fastapi import FastAPI, HTTPException, Path, Query, Body, status
from pydantic import BaseModel

app = FastAPI(title="JSON File DB 기반 FastAPI 예제")

# JSON DB 파일 경로 설정
DB_FILE_PATH = "db.json"

# --- 1. JSON 파일 입출력 헬퍼 함수 ---
def load_db() -> dict:
    """JSON 파일에서 데이터를 읽어옵니다. 파일이 없으면 초기 구조를 생성합니다."""
    if not os.path.exists(DB_FILE_PATH):
        initial_data = {"users": {}, "items": {}}
        save_db(initial_data)
        return initial_data
    
    with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data: dict) -> None:
    """데이터를 JSON 파일에 저장합니다."""
    with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --- 2. Pydantic 모델 및 타입 별칭 정의 ---
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class User(BaseModel):
    name: str
    age: float
    gender: str

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

ValidUserId = Annotated[int, Path(gt=0, description="양의 정수 사용자 ID")]
ValidItemId = Annotated[int, Path(gt=0, description="양의 정수 아이템 ID")]
SearchQuery = Annotated[Optional[str], Query(max_length=20, description="검색어 (최대 20자)")]


# --- 3. 엔드포인트 구현 ---

@app.get("/")
def read_root():
    return {"Hello": "World"}

# 조회(전체) - read
@app.get("/database/")
async def get_all_items():
    db = load_db()
    return {"message": "전체 목록 조회 완료", "data": list(db.values())}


# ==================== USER API ====================

# [GET] 사용자 조회
@app.get("/users/{user_id}")
async def read_user(user_id: ValidUserId, q: SearchQuery = None):
    db = load_db()
    str_user_id = str(user_id)  # JSON 키는 문자열로 관리됨

    if str_user_id not in db["users"]:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    return {
        "user_id": user_id,
        "q": q,
        "data": db["users"][str_user_id]
    }

# [POST] 사용자 생성
@app.post("/users/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_id: ValidUserId, 
    user: Annotated[User, Body(description="생성할 유저 객체")]
):
    db = load_db()
    str_user_id = str(user_id)

    if str_user_id in db["users"]:
        raise HTTPException(status_code=400, detail="User ID already exists")

    db["users"][str_user_id] = user.model_dump()
    save_db(db)

    return {"message": "User created successfully", "user_id": user_id, "data": db["users"][str_user_id]}

# [PUT] 사용자 수정
@app.put("/users/{user_id}")
async def update_user(
    user_id: ValidUserId, 
    user: Annotated[User, Body(description="수정할 유저 객체")]
):
    db = load_db()
    str_user_id = str(user_id)

    if str_user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    previous_data = db["users"][str_user_id]
    db["users"][str_user_id] = user.model_dump()
    save_db(db)

    return {
        "message": "User updated successfully",
        "user_id": user_id,
        "previous_data": previous_data,
        "updated_data": db["users"][str_user_id]
    }

# [DELETE] 사용자 삭제
@app.delete("/users/{user_id}")
async def delete_user(user_id: ValidUserId):
    db = load_db()
    str_user_id = str(user_id)

    if str_user_id not in db["users"]:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found")

    del_user = db["users"].pop(str_user_id)
    save_db(db)

    return {
        "message": f"User ID {user_id} deleted successfully",
        "deleted_user_id": user_id,
        "deleted_data": del_user
    }


# ==================== ITEM API ====================

# [GET] 아이템 조회
@app.get("/items/{item_id}")
async def read_item(item_id: ValidItemId, q: SearchQuery = None):
    db = load_db()
    str_item_id = str(item_id)

    if str_item_id not in db["items"]:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

    return {
        "item_id": item_id,
        "q": q,
        "data": db["items"][str_item_id]
    }

# [POST] 아이템 생성
@app.post("/items/{item_id}", status_code=status.HTTP_201_CREATED)
async def create_item(
    item_id: ValidItemId, 
    item: Annotated[Item, Body(description="생성할 아이템 객체")]
):
    db = load_db()
    str_item_id = str(item_id)

    if str_item_id in db["items"]:
        raise HTTPException(status_code=400, detail="Item ID already exists")

    db["items"][str_item_id] = item.model_dump()
    save_db(db)

    return {"message": "Item created successfully", "item_id": item_id, "data": db["items"][str_item_id]}

# [PUT] 아이템 수정
@app.put("/items/{item_id}")
async def update_item(
    item_id: ValidItemId, 
    item: Annotated[Item, Body(description="수정할 아이템 객체")]
):
    db = load_db()
    str_item_id = str(item_id)

    if str_item_id not in db["items"]:
        raise HTTPException(status_code=404, detail="Item not found")

    previous_data = db["items"][str_item_id]
    db["items"][str_item_id] = item.model_dump()
    save_db(db)

    return {
        "message": "Item updated successfully",
        "item_id": item_id,
        "previous_data": previous_data,
        "updated_data": db["items"][str_item_id]
    }

# [DELETE] 아이템 삭제
@app.delete("/items/{item_id}")
async def delete_item(item_id: ValidItemId):
    db = load_db()
    str_item_id = str(item_id)

    if str_item_id not in db["items"]:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    del_item = db["items"].pop(str_item_id)
    save_db(db)

    return {
        "message": f"Item ID {item_id} deleted successfully",
        "deleted_item_id": item_id,
        "deleted_data": del_item
    }


# ==================== OTHERS ====================

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}