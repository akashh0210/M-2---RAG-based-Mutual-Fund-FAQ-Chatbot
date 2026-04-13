import sqlite3
import os
import json
import chromadb

def audit():
    print("=== RAG COMPONENT AUDIT ===")
    
    # 1. Normalized Data Check
    raw_dir = os.path.join("data", "raw")
    if os.path.exists(raw_dir):
        files = [f for f in os.listdir(raw_dir) if f.endswith('.txt')]
        print(f"[1] Normalized Data: {len(files)} files found in {raw_dir}")
        if files:
            sample_file = os.path.join(raw_dir, files[0])
            size = os.path.getsize(sample_file)
            print(f"    - Sample: {files[0]} ({size} bytes)")
    else:
        print("[1] Normalized Data: Directory not found!")

    # 2. Chunked Data Check
    db_path = os.path.join("data", "rag.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM source_chunks")
        chunk_count = c.fetchone()[0]
        print(f"[2] Chunked Data: {chunk_count} chunks found in {db_path} (source_chunks table)")
        
        c.execute("SELECT chunk_text FROM source_chunks LIMIT 1")
        sample_chunk = c.fetchone()
        if sample_chunk:
            preview = sample_chunk[0][:100].replace('\n', ' ')
            print(f"    - Sample Preview: {preview}...")
        conn.close()
    else:
        print("[2] Chunked Data: sqlite.db not found!")

    # 3. Embedding Check
    print(f"[3] Embedding (Knowledge Store):")
    chroma_path = os.path.join("data", "chroma_db")
    if os.path.exists(chroma_path):
        try:
            client = chromadb.PersistentClient(path=chroma_path)
            collection = client.get_collection("sbi_mf_knowledge")
            vector_count = collection.count()
            print(f"    - ChromaDB: {vector_count} vectors found in '{collection.name}'")
            
            # Dimension check (peek at metadata/embeddings)
            peek = collection.peek(1)
            if peek['embeddings']:
                dim = len(peek['embeddings'][0])
                print(f"    - Dimension: {dim} (Matches BGE-Base-en-v1.5)")
        except Exception as e:
            print(f"    - ChromaDB Error: {e}")
    else:
        print("    - ChromaDB: Directory not found!")

if __name__ == "__main__":
    audit()
