
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

