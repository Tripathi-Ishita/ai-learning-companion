from ingestion.web_loader import load_web

docs = load_web("https://en.wikipedia.org/wiki/Strawberry")
print("documents loaded:", len(docs))
print("metadata:", docs[0].metadata)
print("first 200 chars:", docs[0].page_content[:200])