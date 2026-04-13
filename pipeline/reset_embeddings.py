import sqlite3
import os

db_path = os.path.join("data", "rag.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('UPDATE source_chunks SET embedding_status = "pending", embedding = NULL')
print(f"Reset {c.rowcount} chunks to pending for BGE switch.")
conn.commit()
conn.close()
