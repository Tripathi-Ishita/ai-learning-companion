"""Tools the agents can call. Wraps the RAG retriever 
so an agent can search documents."""

from langchain_core.tools import tool
from rag.retrieve import retrieve


@tool
def search_documents(query: str) -> str:
    """Search the user's uploaded documents for information on a topic.
    Use this for any factual question about the user's study material."""
    chunks = retrieve(query, k=4)

    if not chunks:
        return "No relevant information found in the uploaded documents."

    # Format chunks WITH their source, so the agent can cite them.
    formatted = []
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", "?")
        formatted.append(f"[from {source}, page {page}]\n{chunk.page_content}")

    return "\n\n".join(formatted)


tools = [search_documents]