"""agents/nodes.py

The three specialist agent nodes: tutor, quiz, research.

A node is a function with a fixed shape:
    LearningState in  ->  dict of state updates out

All three specialists get the SAME tool (search_documents).
They differ only in their system prompt, which is their output contract.
"""

from langchain_core.messages import SystemMessage

from config import llm
from agents.tools import tools
from state import LearningState

# Bind the tools once, at import time. Not inside the function.
llm_with_tools = llm.bind_tools(tools)


TUTOR_PROMPT = """You are a patient tutor. The student is learning from material \
they uploaded themselves.

Rules:
- ALWAYS call search_documents first. Answer from the student's material, not from \
your own knowledge.
- Start with a simple real-world analogy, then give the technical explanation.
- Plain prose. No bullet lists, no headings, no markdown.
- If the search returns nothing relevant, say so plainly. Do not invent an answer.
"""


def tutor_node(state: LearningState) -> dict:
    """Explain a concept from the user's documents, beginner-first."""
    messages = state["messages"]

    response = llm_with_tools.invoke(
        [SystemMessage(content=TUTOR_PROMPT)] + messages
    )

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }



# QUIZ NODE
QUIZ_PROMPT = """You are a quizmaster. The student is learning from material they \
uploaded themselves.

Rules:
- ALWAYS call search_documents first. Build the quiz ONLY from what the search returns, \
never from your own knowledge.
- Write exactly 3 to 5 multiple-choice questions.
- Output NOTHING except the questions. No greeting, no introduction, no closing remark, \
no explanation of what you are about to do.
- Use exactly this format for each question:

Q1. <question text>
A) <option>
B) <option>
C) <option>
D) <option>
Answer: <letter>

- If the search returns nothing relevant, reply with exactly one sentence saying the \
uploaded material does not cover this topic. Do not invent questions.
"""

def quiz_node(state: LearningState) -> dict:
    """Quiz on a topic present in student material"""
    messages = state["messages"]

    response = llm_with_tools.invoke(
        [SystemMessage(content=QUIZ_PROMPT)] + messages
    )

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }

#RESEARCH NODE

RESEARCH_PROMPT = """You are a research assistant. The student is learning from material \
they uploaded themselves.

Rules:
- ALWAYS call search_documents first. Answer ONLY from what the search returns, never \
from your own knowledge.
- The search results are labelled like [from filename.pdf, page 3]. Carry those labels \
into your answer, unchanged.
- EVERY factual claim must end with its citation label. A sentence with no citation is \
not allowed — if you cannot cite it, do not write it.
- Be direct and factual. Answer the question asked and stop. Do not pad, do not add \
background the search did not provide.
- If the search returns nothing relevant, say so plainly and cite nothing.
"""

def research_node(state: LearningState) -> dict:
    """Research on a topic present in student material"""
    messages = state["messages"]

    response = llm_with_tools.invoke(
        [SystemMessage(content=RESEARCH_PROMPT)] + messages
    )

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }