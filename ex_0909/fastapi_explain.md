## Fastapi + pydantic + typing.Annotated 정의
---

### 1. 주요 핵심 기술 및 기능 정의

**FastAPI**
* **정의:** Python 3.8+ 기반의 현대적이고 빠르며 high-performance를 제공하는 웹 프레임워크.
* **효과:** OpenAPI(Swagger UI / ReDoc) 규격의 대화형 문서 자동 생성, 비동기(`async/await`) 완벽 지원, 높은 생산성 및 명확한 에러 응답 제공.


**Pydantic**
* **정의:** Python 타입 힌트를 활용한 데이터 검증(Validation) 및 직렬화(Serialization) 라이브러리.
* **효과:** Request Body 데이터의 타입을 자동으로 검증 및 변환하며, 규칙 미준수 시 `422 Unprocessable Entity` 에러를 자동 반환하여 안정성 확보.


**`typing.Annotated`**
* **정의:** Python 3.9+ 타입 시스템에서 원본 타입에 부가적인 메타데이터(제약 조건, 문서 설명 등)를 결합하는 기능.
* **효과:** 타입 정의와 유효성 검증 규칙(`Path`, `Query`, `Body`, `Depends`)을 명확히 분리하여 가독성을 높이고, 타입 별칭(Type Alias)을 통해 공통 파라미터 검증 로직 재사용 가능.



---

### 2. FastAPI HTTP 메서드(GET, POST, PUT, DELETE) 구조 및 특징

| 메서드 | 역할 | Request Body | 주요 특징 및 주의사항 |
| --- | --- | --- | --- |
| **`GET`** | 데이터 조회 | **불가 (사용 금지)** | **HTTP 표준상 Body를 가질 수 없음.** 파라미터 전달 시 경로(`Path`) 또는 쿼리(`Query`) 파라미터만 사용. |
| **`POST`** | 데이터 신규 생성 | **필수/권장** | 서버에 새로운 리소스를 등록할 때 사용. Pydantic 모델을 통해 JSON Body 데이터를 전달받아 저장. |
| **`PUT`** | 데이터 전체 수정/교체 | **필수/권장** | 기존 데이터의 **전체 필드**를 전달받은 데이터로 완전 교체. 일부 필드 누락 시 데이터가 덮어씌워질 수 있음. |
| **`DELETE`** | 데이터 삭제 | **비권장 (Path/Query 사용)** | 특정 리소스를 삭제할 때 사용. 삭제 대상을 지정하기 위해 주로 **경로 파라미터(`Path`)**를 사용하며, 성공 시 결과 메시지(`200 OK`) 또는 응답 본문 없이 `204 No Content`를 반환하는 것이 표준 관례. |

---
