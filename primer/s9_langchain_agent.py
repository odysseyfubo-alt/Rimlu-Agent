"""二十行写一个 Agent：工具清单、循环、记忆全由框架管。对照 s4_agent.py。"""

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from s6_langchain_hello import model
from s8_tool_decorator import query_logistics, query_order

agent = create_agent(
    model=model,
    tools=[query_order, query_logistics],
    system_prompt="你是喵购商城的客服。订单和物流信息只能来自工具返回，工具没给的一个字都不许编。",
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": "user-42"}}


def ask(text):
    result = agent.invoke({"messages": [{"role": "user", "content": text}]}, config=config)
    for m in result["messages"]:
        if m.type == "tool":
            print(f"  [工具 {m.name}] {m.content}")
    return result["messages"][-1].content


print("客服:", ask("我的订单 SO20260901 那双鞋到哪了？几号能到？"))
print("客服:", ask("那它多少钱？"))
