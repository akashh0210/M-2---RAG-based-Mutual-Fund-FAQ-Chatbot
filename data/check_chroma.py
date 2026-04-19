from pipeline.vector_store import get_vector_store
import json

vs = get_vector_store()
res = vs.collection.get(where={"source_id": "url-023"}, include=["metadatas", "documents"])

print(f"Total chunks in Chroma for url-023: {len(res['ids'])}")
if res['metadatas']:
    print("Metadata for first chunk:")
    print(json.dumps(res['metadatas'][0], indent=2))
else:
    print("No chunks found in Chroma Cloud for url-023.")
