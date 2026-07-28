"""Run from the project root: python -m tests.test_messages
Nothing to do with the project. This exists only to make messages visible."""

from langchain_core.messages import SystemMessage, HumanMessage
from config import llm

conversation = [
    SystemMessage(content="You are a pirate. Answer in one short sentence."),
    HumanMessage(content="What is Python?"),
]

print("=== what we SEND (turn 1) ===")
for m in conversation:
    print(type(m).__name__, "->", m.content)

reply = llm.invoke(conversation)

print("\n=== what COMES BACK ===")
print(type(reply).__name__, "->", reply.content)

# "Memory" is this, and only this: keep the reply, add the next question, resend.
conversation.append(reply)
conversation.append(HumanMessage(content="What did I just ask you?"))

reply2 = llm.invoke(conversation)

print("\n=== turn 2 ===")
print(type(reply2).__name__, "->", reply2.content)

print("\n=== the whole list now ===")
for m in conversation:
    print(type(m).__name__, "->", m.content[:60])