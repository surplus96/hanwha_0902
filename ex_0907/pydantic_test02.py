"""
Pydantic은 파이썬의 Type Hint(타입 힌트)를 활용해 데이터 유효성 검사(Data Validation) 및 데이터 변환(Parsing/Serialization)을 수행하는 대표적인 라이브러리입니다.  

Pydantic 주요 사용 범위:
    - 웹 API 개발 (FastAPI 등): 클라이언트 요청(Body, Query) 데이터 검증 및 응답 데이터 직렬화, OpenAPI(Swagger) 문서 자동 생성.
    - 환경 설정 관리 (pydantic-settings): .env 파일이나 시스템 환경 변수를 정적 타입 객체로 안전하게 로드 및 검증. 
    - LLM / AI 애플리케이션 (LangChain 등): OpenAI API 등의 정형화되지 않은 출력값을 구조화된 JSON 데이터로 파싱 및 강제. 
    - 데이터 파이프라인 (ETL): 외부 API나 파일(CSV/JSON)에서 유입되는 정제되지 않은 데이터의 무결성 검증 및 변환.  
"""


# 기본 검증 및 자동 타입 변환
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=50)  # 길이 제약
    email: EmailStr                                 # 이메일 형식 검증
    age: int = Field(gt=0, le=120)                 # 범위 제약 (0 < age <= 120)
    is_active: bool = True                          # 기본값 지정

# 자동 타입 변환 및 정상 동작
user_data = {
    "id": "101",  # 문자열이지만 int로 변환
    "name": "Alex",
    "email": "alex@example.com",
    "age": 28
}

user = User(**user_data)
print(user.id)        # 101 (int)
print(user.model_dump())  # Dict 변환
# --------------------------------------------------------------------------------------------------

# 커스텀 유효성 검사 (@field_validator, @model_validator)
from pydantic import BaseModel, field_validator, model_validator

class SignupForm(BaseModel):
    username: str
    password: str
    password_confirm: str

    # 특정 필드 검증 (영문/숫자 혼합 여부 등)
    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("아이디는 알판벳과 숫자만 포함해야 합니다.")
        return value

    # 필드 간 교차 검증 (비밀번호 일치 확인)
    @model_validator(mode="after")
    def check_passwords_match(self) -> "SignupForm":
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self
# --------------------------------------------------------------------------------------------------

# JSON 직렬화 및 역직렬화
# JSON 문자열 -> Pydantic 객체 (역직렬화)
json_raw = '{"id": 1, "name": "Sam", "email": "sam@test.com", "age": 30}'
user_obj = User.model_validate_json(json_raw)

# Pydantic 객체 -> JSON 문자열 (직렬화)
json_output = user_obj.model_dump_json()
print(json_output)
# --------------------------------------------------------------------------------------------------

