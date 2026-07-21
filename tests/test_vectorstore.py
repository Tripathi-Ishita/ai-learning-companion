from ingestion.pdf_loader import load_pdf
from rag.chunk import chunk_documents
from rag.vectorstore import add_documents, get_vectorstore

# --- INDEX: PDF -> chunks -> Chroma on disk ---
docs = load_pdf("data/uploads/KoreanPhrases.pdf")
chunks = chunk_documents(docs)
add_documents(chunks)

# --- VERIFY: reopen the store and count ---
store = get_vectorstore()
print("total chunks in store:", store._collection.count())

# --- SEARCH: does similarity retrieval actually work? ---
print("\n--- search: 'how to say hello' ---")
results = store.similarity_search("how to say hello", k=2)
for d in results:
    print(f"[page {d.metadata.get('page')}] {d.page_content[:120]}")