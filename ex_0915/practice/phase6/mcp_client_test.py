""" 
6-3. MCP 클라이언트: 위 서버를 subprocess로 띄우고, 그 도구를
LangGraph/LangChain이 바로 쓸 수 있는 Tool 객체로 가져온다.
"""


import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient({
        "manufacturing": {
            "command": "python",
            "args": ["mcp_manufacturing_server.py"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()

    print(f"MCP 서버에서 가져온 도구 {len(tools)}개:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

    error_lookup_tool = next(t for t in tools if t.name == "lookup_error_code")
    result = await error_lookup_tool.ainvoke({"model": "HS-CNC-450X", "code": "E-204"})
    print(f"\n실행 결과: {result}")


asyncio.run(main())

