"""Retrieval — given a question, return the most relevant chunks.
This is the SEAM: agents call retrieve() and never know it's Chroma inside."""

from langchain_core.documents import Document
from rag.vectorstore import get_vectorstore


def retrieve(question: str, k: int = 4) -> list[Document]:
    store = get_vectorstore()                       # open the store (from milestone 4)
    results = store.similarity_search(question, k=k)  # find the k closest chunks
    return results