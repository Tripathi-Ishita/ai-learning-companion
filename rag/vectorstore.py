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
    """Embed chunks and save them into the persistent store."""
    store = get_vectorstore()
    store.add_documents(chunks)               # embeds each chunk, writes to disk
    print(f"added {len(chunks)} chunks to {PERSIST_DIR}")