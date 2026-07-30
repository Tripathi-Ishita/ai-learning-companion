"""Run from the project root with: python -m tests.test_graph"""

from langchain_core.messages import HumanMessage

from agents.graph import app

config = {"configurable": {"thread_id": "ishita"}}

turns = [
    "What does my material say about AI agents?",
    "explain that simpler",
    "quiz me on that",
]

for question in turns:
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    print(f"\n===== {question} =====")
    print("intent     :", result["intent"])
    print("step_count :", result.get("step_count"))
    print("answer     :", result["messages"][-1].content[:400])

print("\n\n===== fresh thread — should NOT remember =====")
fresh = {"configurable": {"thread_id": "someone-else"}}
result = app.invoke({"messages": [HumanMessage(content="explain that simpler")]}, config=fresh)
print(result["messages"][-1].content[:300])