from ingestion.pdf_loader import load_pdf

docs = load_pdf("data/uploads/KoreanPhrases.pdf")

print("number of pages loaded:", len(docs))
print("\n--- metadata of first page ---")
print(docs[0].metadata)
print("\n--- first 200 chars of first page ---")
print(docs[0].page_content[:200])