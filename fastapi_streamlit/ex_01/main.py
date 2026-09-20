# 모듈 인스톨 pip install "fastapi[standard]"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import Optional

app = FastAPI()

class User(BaseModel):
    name: str
    age:float
    gender: str

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

fake_db = [{'item_name':'Foo'}, {'item_name':'Dev'}, {'item_name':'Dao'}]

# http://127.0.0.1:8000/
@app.get("/")  # 요청을 보내는 경로
def read_root():
    return {"Hello": "World"} # 실행되는 경로

#http://127.0.0.1:8000/users/me 
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user me"}

# GET 요청: 경로 매개변수(user_id) + 쿼리 매개변수(q)
# GET 메서드는 Body를 가질 수 없으므로 User 모델 대신 쿼리 파라미터 q를 설정합니다.
@app.get("/users/{user_id}")
async def read_user(user_id: int, q: Optional[str] = None):
    return {"user_id": user_id, "q": q}

# POST 요청: Request Body(User) 수신
# 유저 생성/수정 등 Body 데이터 전달이 필요할 때는 POST 메서드를 사용합니다.
# --- POST 요청 (신규 생성) ---
@app.post("/users/{user_id}", status_code=201)
async def create_user(user_id: int, user: User):
    if user_id in fake_db:
        raise HTTPException(status_code=400, detail="User ID already exists")
    
    # DB에 저장
    fake_db[user_id] = user.model_dump()
    return {"message": "User created successfully", "user_id": user_id, "data": fake_db[user_id]}


# --- PUT 요청 (전체 수정/교체) ---
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    """
    기존 사용자 데이터를 전달받은 Request Body(User) 내용으로 완전히 교체합니다.
    """
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. 이전 데이터 백업 (응답 확인용)
    previous_data = fake_db[user_id]
    
    # 2. 데이터 업데이트
    fake_db[user_id] = user.model_dump()
    
    return {
        "message": "User updated successfully",
        "user_id": user_id,
        "previous_data": previous_data,
        "updated_data": fake_db[user_id]
    }

# Enum을 활용한 경로 매개변수
#http://127.0.0.1:8000/users/{model_name}
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/items/")
async def  read_item(skip: int = 0, limit: int = 10):
    return fake_db[0:2]   # fake_items_db[skip:skip + limit] 인덱스 슬라이싱 역할

# http://127.0.0.1:8000/items02/test
# http://127.0.0.1:8000/items02/test?q=None
@app.get("/items02/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

"""
다음과 같은 API를 생성했습니다:

- 및 경로 에서 HTTP 요청을 수신합니다 .//users/{user_id}
- 두 경로 모두 GET 작업 (HTTP 메서드 라고도 함 ) 을 수행합니다 .
- 경로에는 . 이어야 하는 경로 매개변수가/users/{user_id} 있습니다 . user_idint
- 해당 경로는 /users/{user_id} 선택적 str 쿼리 매개변수를 q 포함합니다 .

실행 코드: 
fastapi dev main.py
또는
uvicorn main:app --reload
"""