"""Web loader — turns a URL into a Document with metadata.
Same output shape as pdf_loader: list[Document] with source + type tags."""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


def load_web(url: str) -> list[Document]:
    loader = WebBaseLoader(url)               # points at the web page
    documents = loader.load()                 # fetches page, extracts text -> Document(s)

    for doc in documents:
        doc.metadata["source"] = url          # tag: which URL
        doc.metadata["type"] = "web"          # tag: it's a web page

    return documents


