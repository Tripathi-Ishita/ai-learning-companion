"""agents/nodes.py

The intent router plus the three specialist agent nodes: tutor, quiz, research.

A node is a function with a fixed shape:
    LearningState in  ->  dict of state updates out

All three specialists get the SAME tool (search_documents).
They differ only in their system prompt, which is their output contract.
The router gets NO tools — it must never search.
"""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config import llm
from agents.tools import tools
from state import LearningState

# Bind the tools once, at import time. Not inside the function.
llm_with_tools = llm.bind_tools(tools)


# ---------------------------------------------------------------- ROUTER

ROUTER_INTENT_PROMPT = """You are the intent router for a learning assistant with three \
specialists: tutor, quiz, research.

Respond with EXACTLY one word: tutor, quiz, or research.
No punctuation, no explanation, no other text.

- quiz -> the student wants to be tested. Cues: "quiz me", "test me", "give me \
questions", "practice questions", "ask me". This wins over every other cue: if the \
student asks to be tested, the answer is quiz no matter what else the message says.
- research -> the student wants a precise, cited factual answer. Cues: "according to", \
"what does the document say", "cite", "exact", pointed who/when/where lookups.
- tutor -> the student wants a concept explained or simplified. Cues: "explain", \
"what is", "help me understand", "I don't get it", "simpler", "walk me through".

Classify by the ACTION the student is requesting, never by the topic and never by what \
was discussed earlier. "quiz me on that" is quiz. "explain that simpler" is tutor.

If the message genuinely fits none of the three, answer tutor.
"""


def route_intent(state: LearningState) -> dict:
    """Classify the latest human message into one of the three specialists.

    Uses `llm`, NOT `llm_with_tools` — the router must never call a tool.
    Resets step_count: the loop guard is per-turn, and the router runs once per turn.
    """
    human_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]

    latest = human_messages[-1].content
    earlier = [m.content for m in human_messages[-3:-1]]

    # Earlier turns are demoted to context so they can't be mistaken for the question.
    context_block = ""
    if earlier:
        context_block = (
            "Earlier questions — use ONLY to resolve what 'that' / 'it' refers to:\n"
            + "\n".join(f"- {t}" for t in earlier)
            + "\n\n"
        )

    router_input = f"{context_block}Classify ONLY this message:\n{latest}"

    response = llm.invoke([
        SystemMessage(content=ROUTER_INTENT_PROMPT),
        HumanMessage(content=router_input),
    ])

    raw = response.content.strip().lower().strip(".")

    intent = raw if raw in {"tutor", "quiz", "research"} else "tutor"

    return {"intent": intent, "step_count": 0}


# ---------------------------------------------------------------- TUTOR

TUTOR_PROMPT = """You are a patient tutor. The student is learning from material they \
uploaded themselves.

Rules:
- ALWAYS call search_documents before answering any question about a topic or concept.
- The ONE exception: if the message is a greeting or small talk, reply in one short \
sentence and do not search.
- Start with a simple real-world analogy, then give the technical explanation.
- Plain prose. No bullet lists, no headings, no markdown.
- If the search returns nothing relevant, say so plainly. Do not invent an answer.
"""


def tutor_node(state: LearningState) -> dict:
    """Explain a concept from the user's documents, beginner-first."""
    messages = state["messages"]

    # Decide this in Python. Do not ask the model to inspect its own history.
    has_prior_answer = any(
        isinstance(m, AIMessage) and m.content for m in messages
    )

    prompt = TUTOR_PROMPT
    if not has_prior_answer:
        prompt += (
            "\n- FACT: this is the first turn of the conversation. Nothing has been "
            "explained yet. If the student refers back to something ('that', 'it', "
            "'simpler'), say plainly there is nothing to simplify yet and ask what "
            "they would like explained. Do not invent a topic."
        )

    response = llm_with_tools.invoke(
        [SystemMessage(content=prompt)] + messages
    )

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }


# ---------------------------------------------------------------- QUIZ

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
    """Generate multiple-choice questions from the student's material."""
    messages = state["messages"]

    response = llm_with_tools.invoke(
        [SystemMessage(content=QUIZ_PROMPT)] + messages
    )

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }


# ---------------------------------------------------------------- RESEARCH

RESEARCH_PROMPT = """You are a research assistant. The student is learning from material \
they uploaded themselves.

Rules:
- ALWAYS call search_documents first. Answer ONLY from what the search returns, never \
from your own knowledge.
- The search results are labelled like [from filename.pdf, page 3]. Carry those labels \
into your answer, unchanged.
- EVERY factual claim must end with its citation label. A sentence with no citation is \
not allowed — if you cannot cite it, do not write it.
- Begin with the answer itself. Never announce what you are about to do, never mention \
searching or search results, never explain your process.
- Be direct and factual. Answer the question asked and stop. Do not pad, do not add \
background the search did not provide.
- If the search returns nothing relevant, say so plainly and cite nothing.
"""


def research_node(state: LearningState) -> dict:
    """Answer factually from the student's material, with citations."""
    messages = state["messages"]

    response = llm_with_tools.invoke(
        [SystemMessage(content=RESEARCH_PROMPT)] + messages
    )

    return {
        "messages": [response],
        "step_count": state.get("step_count", 0) + 1,
    }