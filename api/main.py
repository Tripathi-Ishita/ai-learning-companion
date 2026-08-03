"""api/main.py

The front door. Wraps the graph in HTTP so a UI can reach it.
No AI logic here — this file only translates HTTP <-> the modules below.

Dependency direction: ui -> api -> agents -> rag -> ingestion -> config
"""

import os
import shutil

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, ToolMessage
from ingestion.loader import load_source
from rag.chunk import chunk_documents
from rag.vectorstore import add_documents
from agents.graph import app as graph_app
from agents.profile import load_profile

api = FastAPI(title="Studybook API")

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AskRequest(BaseModel):
    question: str
    user_id: str


@api.get("/ping")
def ping():
    return {"status": "alive"}


def _ingest(source: str, source_type: str) -> dict:
    """load -> chunk -> store. Shared by both upload paths."""
    docs = load_source(source, source_type)
    if not docs:
        return {"ok": False, "source": source, "chunks_added": 0}
    chunks = chunk_documents(docs)
    add_documents(chunks)
    return {"ok": True, "source": source, "chunks_added": len(chunks)}


@api.post("/upload")
async def upload(file: UploadFile = File(None), url: str = Form(None)):
    """Accepts EITHER an uploaded file OR a link."""
    if file is not None:
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        source_type = "pdf" if file.filename.lower().endswith(".pdf") else "notes"
        return _ingest(path, source_type)

    if url:
        source_type = "youtube" if ("youtube.com" in url or "youtu.be" in url) else "web"
        return _ingest(url, source_type)

    return {"ok": False, "error": "send a file or a url"}


def _chunks_from_this_turn(messages) -> list[str]:
    """The tool output the agent actually saw on THIS turn."""
    turn = []
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            break
        turn.append(m)
    return [m.content for m in reversed(turn) if isinstance(m, ToolMessage)]


@api.post("/ask")
def ask(req: AskRequest):
    config = {"configurable": {"thread_id": req.user_id}}
    result = graph_app.invoke(
        {"messages": [HumanMessage(content=req.question)], "user_id": req.user_id},
        config=config,
    )
    messages = result["messages"]
    return {
        "answer": messages[-1].content,
        "intent": result.get("intent", "tutor"),
        "chunks": _chunks_from_this_turn(messages),
    }


@api.get("/profile/{user_id}")
def profile(user_id: str):
    return load_profile(user_id)