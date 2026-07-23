from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

def load_notes(file_path: str) -> list[Document]:
    loader = TextLoader(file_path)
    documents = loader.load()
    for doc in documents:
        doc.metadata["source"] = file_path
        doc.metadata["type"] = "notes"      # "notes" — the source kind, not the file extension
    return documents