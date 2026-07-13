"""The shared state that flows through the LangGraph. One pot, typed."""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class LearningState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # append, not overwrite
    intent: str          # "explain" / "quiz" / "research" — router's decision
    topic: str           # what's being discussed
    user_id: str         # for memory lookups
    context: str         # retrieved RAG chunks
    step_count: int      # loop guaard