"""Chunking — splits page Documents into smaller overlapping chunks.
One job: make embedding-sized pieces. Metadata carries down automatically."""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,          # ~500 chars per chunk (from config)
        chunk_overlap=CHUNK_OVERLAP,    # ~50 chars shared between neighbors (from config)
    )
    chunks = splitter.split_documents(documents)   # splits, keeps metadata
    return chunks