from ingestion.loader import load_source

docs = load_source("data/uploads/KoreanPhrases.pdf", "pdf")
print("pdf docs:", len(docs), docs[0].metadata["type"])

docs = load_source("data/uploads/mynote.txt", "notes")
print("notes docs:", len(docs), docs[0].metadata["type"])

# Should raise ValueError loudly:
try:
    load_source("whatever", "pfd")
except ValueError as e:
    print("correctly rejected:", e)