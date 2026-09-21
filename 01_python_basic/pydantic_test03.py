# 시스템 환경변수 및 Config 관리 (pydantic-settings)
from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    app_name: str = "My Microservice"
    environment: str = "development"
    debug: bool = False
    
    # 민감 정보 보호 (SecretStr 사용 시 print 시 마스킹됨)
    api_key: SecretStr
    database_url: PostgresDsn

    # .env 파일 로드 설정 (pydantic-settings 설치 필요)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 환경변수 로드
# config = AppConfig()
# --------------------------------------------------------------------------------------------------


# LLM 응답을 구조화된 데이터로 추출 (Structured Outputs / Instructor)
from typing import List
from pydantic import BaseModel, Field

class SentimentAnalysis(BaseModel):
    sentiment: str = Field(description="텍스트의 감정 (positive, neutral, negative)")
    score: float = Field(description="감정 점수 (0.0 ~ 1.0)")
    keywords: List[str] = Field(description="감정 분석 판단 기준이 된 핵심 단어 리스트")

# LLM 프롬프트 생성 또는 Structured Output 스키마 전달에 그대로 활용
print(SentimentAnalysis.model_json_schema())
# --------------------------------------------------------------------------------------------------
