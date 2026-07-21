from ingestion.pdf_loader import load_pdf
from rag.chunk import chunk_documents

docs = load_pdf("data/uploads/KoreanPhrases.pdf")
chunks = chunk_documents(docs)

print("pages loaded:", len(docs))
print("chunks produced:", len(chunks))
print("\n--- first chunk metadata ---")
print(chunks[0].metadata)
print("\n--- first chunk text ---")
print(chunks[0].page_content)