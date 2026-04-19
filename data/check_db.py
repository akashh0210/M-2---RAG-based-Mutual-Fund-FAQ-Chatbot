import sqlite3
import os

db_path = "data/rag.db"
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Source Documents ---")
cursor.execute("SELECT source_id, official_url, status, chunk_count FROM source_documents WHERE source_id IN ('url-021', 'url-022', 'url-023', 'url-024', 'url-025', 'url-026')")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- Source Chunks (Sample) ---")
cursor.execute("SELECT source_id, source_url, chunk_text FROM source_chunks WHERE source_id = 'url-023' LIMIT 1")
row = cursor.fetchone()
if row:
    print(f"URL in Chunk: {row['source_url']}")
    print(f"Content: {row['chunk_text'][:100]}...")
else:
    print("No chunks found for url-023")

conn.close()
