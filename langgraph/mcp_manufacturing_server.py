"""
6-3. MCP 서버: 5-2에서 만든 제조 도구 3개를 MCP 표준 프로토콜로 노출한다.
이 서버는 LangGraph에 종속되지 않는다 - 어떤 MCP 클라이언트든(Claude Desktop, 다른 에이전트 프레임워크 등) 그대로 재사용 가능하다.
"""

from mcp.server.fastmcp import FastMCP
from manufacturing_data import SPARE_PARTS_INVENTORY, MAINTENANCE_SCHEDULE


mcp = FastMCP("manufacturing-tools")

ERROR_CODES = {
    ("HS-CNC-450X", "E-204"): "주축 모터 과부하. 즉시 가공을 중단하고 냉각 시스템을 점검해야 합니다.",
    ("HS-ROBOT-A7", "E-108"): "서보 드라이버 통신 이상. 컨트롤러 재부팅 후에도 반복되면 케이블 커넥터를 점검해야 합니다.",
}


@mcp.tool()
def lookup_error_code(model: str, code: str) -> str:
    """설비의 오류코드에 대한 원인과 조치 방법을 조회한다."""
    return ERROR_CODES.get((model, code), "해당 오류코드 정보를 찾을 수 없습니다.")


@mcp.tool()
def check_parts_stock(part_name: str) -> dict:
    """특정 부품의 현재 재고 수량과 리드타임을 조회한다."""
    info = SPARE_PARTS_INVENTORY.get(part_name)
    return info if info else {"error": f"'{part_name}' 정보를 찾을 수 없습니다."}


@mcp.tool()
def check_maintenance_schedule(equipment: str) -> dict:
    """특정 설비의 다음 정기점검 예정일과 담당 기술자를 조회한다."""
    info = MAINTENANCE_SCHEDULE.get(equipment)
    return info if info else {"error": f"'{equipment}' 정보를 찾을 수 없습니다."}



if __name__ == "__main__":
    mcp.run(transport="stdio")