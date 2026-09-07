Pydantic은 파이썬의 Type Hint(타입 힌트)를 활용해 데이터 유효성 검사(Data Validation) 및 데이터 변환(Parsing/Serialization)을 수행하는 대표적인 라이브러리입니다.  

    Pydantic 주요 사용 범위:

        - 웹 API 개발 (FastAPI 등): 클라이언트 요청(Body, Query) 데이터 검증 및 응답 데이터 직렬화, OpenAPI(Swagger) 문서 자동 생성.

        - 환경 설정 관리 (pydantic-settings): .env 파일이나 시스템 환경 변수를 정적 타입 객체로 안전하게 로드 및 검증. 

        - LLM / AI 애플리케이션 (LangChain 등): OpenAI API 등의 정형화되지 않은 출력값을 구조화된 JSON 데이터로 파싱 및 강제. 
        
        - 데이터 파이프라인 (ETL): 외부 API나 파일(CSV/JSON)에서 유입되는 정제되지 않은 데이터의 무결성 검증 및 변환.  