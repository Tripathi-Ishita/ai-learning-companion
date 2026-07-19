"""PDF loader — turns a PDF file path into clean Document objects with metadata.
One job: read the file. No chunking, no embedding here."""

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdf(file_path: str) -> list[Document]:
    loader = PyPDFLoader(file_path)          # points at the PDF
    documents = loader.load()                # one Document per PAGE, with page metadata

    # Tag every page with source + type, so later we can filter retrieval by source.
    for doc in documents:
        doc.metadata["source"] = file_path
        doc.metadata["type"] = "pdf"

    return documents