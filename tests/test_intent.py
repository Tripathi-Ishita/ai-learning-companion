from langchain_core.messages import HumanMessage

from agents.nodes import tutor_node, quiz_node, research_node, route_intent

cases=[
    ("Explain chunking to me like I'm a beginner."),
    ("explain this simpler to me"),
    ("What does my material say about embeddings?"),
    ("Test my knowledge on agents"),
    ("hi"),
]
for question in cases:
    state={"messages": [HumanMessage(content=question)]} #the type of state graph can pass(we are testing this outside of graph)
    update=route_intent(state) #call a node with a state 
    reply=update["intent"]

    print("intent:", repr(reply))
