"""
6-3 마무리: MCP로 가져온 도구를 실제 LangGraph 그래프(ToolNode)에 연결한다.
"agent -> tools -> agent" 순환 구조(6-2와 동일한 원리)로 ReAct 스타일 에이전트를 구성한다.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

load_dotenv()


async def main():
    mcp_client = MultiServerMCPClient({
        "manufacturing": {
            "command": "python",
            "args": ["mcp_manufacturing_server.py"],
            "transport": "stdio",
        }
    })
    tools = await mcp_client.get_tools()
    print(f"MCP에서 가져온 도구 {len(tools)}개를 LangGraph에 연결합니다.\n")

    model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    model_with_tools = model.bind_tools(tools)

    def call_model(state: MessagesState) -> dict:
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> str:
        last_message = state["messages"][-1]
        return "tools" if last_message.tool_calls else "end"

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")  # 도구 실행 후 다시 agent로 판단 -> 순환

    app = graph.compile()

    result = await app.ainvoke({
        "messages": [
            {"role": "user", "content": "HS-CNC-450X에서 E-204 오류가 떴어. 원인이 뭐고, 수리에 필요한 스핀들 베어링 재고 있어?"}
        ]
    })

    print(f"최종 답변:\n{result['messages'][-1].content}")


asyncio.run(main())
