from ingestion.youtube_loader import load_youtube

docs = load_youtube("https://www.youtube.com/shorts/Zv_W-U1z1QI")
print("documents loaded:", len(docs))
if docs:
    print("metadata:", docs[0].metadata)
    print("first 200 chars:", docs[0].page_content[:200])
else:
    print("no transcript available for this video")