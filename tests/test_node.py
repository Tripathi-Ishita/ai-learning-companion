"""Run from the project root with: python -m tests.test_nodes"""

from langchain_core.messages import HumanMessage

from agents.nodes import tutor_node, quiz_node, research_node
cases=[
    (tutor_node,"Explain chunking to me like I'm a beginner."),
    (quiz_node,"greetings in korean."),
    (research_node, "What does my material say about embeddings?"),
] 
for node, question in cases:
    state = {"messages": [HumanMessage(content=question)], "step_count": 0}
    update = node(state)
    reply = update["messages"][0]

    print(f"\n===== {node.__name__} =====")
    print("content    :", repr(reply.content))
    print("tool_calls :", reply.tool_calls)
    print("step_count :", update["step_count"]) 