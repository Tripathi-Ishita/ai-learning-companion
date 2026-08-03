"""Vector store — embeds chunks and persists them to Chroma on disk.
Two jobs: hand back the store, and add chunks to it. Path + model come from config."""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from config import embeddings, PERSIST_DIR


def get_vectorstore() -> Chroma:
    """Open (or create) the Chroma store at the configured path."""
    return Chroma(
        persist_directory=PERSIST_DIR,        # the ONE path, from config
        embedding_function=embeddings,        # the ONE model, from config
    )


def add_documents(chunks: list[Document]) -> None:
    """Embed chunks and save them. Deterministic ids make re-ingestion an upsert."""
    store = get_vectorstore()
    ids = [f"{c.metadata.get('source', 'unknown')}::{i}" for i, c in enumerate(chunks)]
    store.add_documents(chunks, ids=ids)
    print(f"added {len(chunks)} chunks to {PERSIST_DIR}")