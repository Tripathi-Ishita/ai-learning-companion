from rag.retrieve import retrieve

results = retrieve("how do I say thank you in Korean?")

print("chunks returned:", len(results))
for d in results:
    print(f"\n[page {d.metadata.get('page')}] {d.page_content[:150]}")