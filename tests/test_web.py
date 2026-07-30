from ingestion.loader import load_source
from rag.chunk import chunk_documents
from rag.vectorstore import add_documents, get_vectorstore
from rag.retrieve import retrieve
# load te document
docs = load_source("https://en.wikipedia.org/wiki/AI_agent", "web")
# chunk the document
chunks=chunk_documents(docs)
# add the chunks to the vectorstore
add_documents(chunks)
# Open the vectorstore and count the number of chunks
store = get_vectorstore()

print("documents loaded:", len(docs))
print("total chunks in store:", store._collection.count())

print("\n--- search: 'what is an AI agent' ---")
results = retrieve("what is an AI agent", k=4)
for d in results:
    print(f"[source {d.metadata.get('source')}] {d.page_content}")