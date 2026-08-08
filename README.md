# Studybook — AI Research & Learning Companion

Ask questions against your own material. Upload PDFs, notes, web articles, or YouTube transcripts, then talk to them: get beginner-friendly explanations, generated quizzes, or cited factual answers — grounded in *your* documents, not the model's memory, and remembered across sessions.

Built as a portfolio project to cover the GenAI stack end to end: RAG, multi-agent orchestration with LangGraph, persistent conversation memory, a FastAPI backend, and a Streamlit frontend.

<!-- SCREENSHOT 1: loaded conversation, dark theme, TUTOR answer with Retrieved chunks expanded -->
![Studybook — conversation with retrieved chunks](docs/screenshot-conversation.png)

---

## What it does

You add sources from the sidebar — drag-and-drop a PDF or TXT, or paste a web page / YouTube URL. Each source is loaded, chunked, embedded, and indexed into a persistent vector store. Then you ask questions in the chat, and an intent router sends each one to the right specialist:

- **TUTOR** — beginner-friendly explanation, analogy first, plain prose
- **QUIZ** — multiple-choice questions generated from retrieved material
- **RESEARCH** — factual answers with explicit citations (`[from source, page N]`)

Every answer carries an uppercase label showing which specialist produced it, and a collapsible **Retrieved chunks** panel showing exactly what the agent read before answering — the actual tool output from that turn, not a re-run of retrieval.

Conversations are remembered per user across sessions and across server restarts.

<!-- SCREENSHOT 2: empty state, dark theme -->
![Studybook — empty state](docs/screenshot-empty.png)

---

## Architecture

Two separate processes, talking only over HTTP:

```
Browser
  └── Streamlit UI (:8501)          ui/app.py — imports nothing from the project
        └── HTTP / JSON
              └── FastAPI (:8000)   api/main.py — /upload, /ask, /profile/{user_id}
                    └── LangGraph   router → { tutor | quiz | research } → (tools → back)* → END
                          ├── Chroma          persistent vector store (retrieval seam: rag/retrieve.py)
                          ├── SqliteSaver     conversation checkpoints, keyed by thread_id = user_id
                          └── Groq LLM        llama-3.1-8b-instant
```

Dependency direction is strictly one-way: `ui → api → agents → rag → ingestion → config`. The UI imports only `requests` and `streamlit` — it could be replaced with React tomorrow and no AI code would change.

**Two mechanisms in one graph.** The intent router is a *workflow*: a human-written rule reads the classified intent and picks the lane. The tool loop is an *agent*: the model itself decides whether to call `search_documents` (and writes its own search query — "explain chunking like I'm a beginner" becomes `query="chunking definition"`). A hard `step_count` ceiling, reset per turn by the router, guarantees the loop terminates regardless of what the model does.

**Three separate stores, three separate jobs.**

| Store | Holds | Keyed by |
|---|---|---|
| Chroma (`data/chroma_db`) | document chunks + embeddings | — (shared pool) |
| SQLite (`data/checkpoints.sqlite`) | full conversation state snapshots | `thread_id` = `user_id` |
| `data/profiles.json` | per-user topic progress | `user_id` |

Conversation memory and user memory are deliberately separate: the checkpointer answers "what did we just say?", the profile store answers "what does this person know?". The profile store is scaffolded and tested but not yet wired to a grader — automatic topic-tagging is deferred (see roadmap).

---

## Stack

Python · LangGraph · LangChain · Chroma · sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`) · Groq (`llama-3.1-8b-instant`) · FastAPI + uvicorn · Streamlit

---

## Running it locally

```bash
git clone <this repo>
cd ai-learning-companion
python -m venv venv && venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env                               # add your GROQ_API_KEY
```

Two terminals:

```bash
# 1 — the API
uvicorn api.main:api --reload

# 2 — the UI
streamlit run ui/app.py
```

Open http://localhost:8501, add a source from the sidebar, and ask a question. The API also exposes interactive docs at http://localhost:8000/docs.

---

## Design decisions worth defending

**The chunks panel shows what the agent saw, not a fresh retrieval.** `/ask` extracts the `ToolMessage`s from the current turn rather than re-running `retrieve(question)`. The agent rewrites the user's question into its own search query, so re-retrieving on the raw question would display chunks the model never read. Honesty over convenience — with the accepted cost that formatted tool output carries no similarity scores.

**Deterministic chunk ids.** Every chunk is stored as `{source}::{index}`, so re-ingesting a source is an upsert, not a duplicate insert. Verified: adding the same URL twice leaves the store unchanged.

**The router's fallback is always a grounded lane.** Unvalidated model output never becomes control flow: the router's reply is checked against `{tutor, quiz, research}` with a hard fallback to `tutor`. A proposed ungrounded "chat" lane was rejected — routing errors into it would silently turn a grounded system into a generic chatbot.

**Never ask the model a fact you can compute.** Anything about the shape of its own input — is there prior history, which message is newest — is computed in Python and stated in the prompt as fact. A rule asking the model to introspect its own context window failed in both directions before being replaced with `has_prior_answer` computed in code.

**Heavy objects load once at startup.** The embedding model and compiled graph are built at import time, never per request.

---

## Known limitations (measured, not guessed)

These were found by testing the running system, and are documented deliberately — identifying weaknesses is the point of measuring.

**Tool use is non-deterministic.** The tutor *may* answer easy general-knowledge questions from the model's own training instead of searching — observed live: the same question retrieved chunks on one run and skipped retrieval on another. Mitigation: the research lane must cite, so an uncited claim signals a training leak. Roadmap: enforce a tool call before answering.

**Web boilerplate occupies retrieval slots.** Wikipedia's page footer ("Retrieved from …oldid=…") was returned as a top-k chunk. Fix is reranking plus ingestion cleaning (roadmap).

**Retrieval underperforms on list-structured documents.** With a phrase-list PDF, chunks share near-identical structure, so the embedder scores sentence *shape* over answer *content*. Prose sources retrieve well. Planned fix: hybrid BM25 + vector search with cross-encoder reranking.

**Quiz coverage equals one retrieval.** A quiz is built from ~4 chunks similar to a single model-written query — "quiz me on attention" works; "quiz me on my documents" produces an arbitrary quiz. The fix is broad-corpus quiz retrieval — different retrieval, not a different prompt.

**Follow-ups reuse conversation instead of re-searching.** Once material is in the message history, later turns often answer from it with no new retrieval — which also means later turns are less grounded than the first.

**No per-user document isolation.** Conversations are isolated per user (`thread_id = user_id`), but the vector store is a shared pool: chunk metadata carries `source` and `type` only. Fixing this is non-trivial because the LLM writes the tool call and has no access to user identity — it requires injected state or per-request tool construction.

**UI display state is session-scoped.** A browser refresh clears the visible chat, source list, and counters; the underlying data survives in Chroma and SQLite. Rehydration on load is the first roadmap item.

**No authentication.** User identity is a plain text input, sufficient to demonstrate per-user conversation isolation.

---

## Roadmap (v2)

In order: a login page for identity capture → rehydrating the UI from the durable stores on login (sources, counts, and prior chat) → multi-chat per user (`thread_id = user_id::chat_id`) → per-user document isolation in Chroma → quiz configuration (question count, difficulty) scoped to the profile store's `topics_seen` → broad-coverage quiz retrieval → similarity scores in the chunks panel → hybrid search + reranking → knowledge graph + GraphRAG (Neo4j) → an evaluation harness.

---

## Project structure

```
config.py            env, constants, shared llm + embeddings
state.py             LearningState TypedDict
ingestion/           pdf / web / youtube / notes loaders + dispatcher
rag/                 chunking, vector store, retrieval seam, RAG chain
agents/              tools, nodes (router + 3 specialists), graph, profile store
api/main.py          FastAPI: /upload, /ask, /profile/{user_id}
ui/app.py            Streamlit frontend (HTTP only)
tests/               run as: python -m tests.<name>
```
