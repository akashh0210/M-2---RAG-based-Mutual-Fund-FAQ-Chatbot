import requests
import time
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("--- 1. Testing Health Check ---")
    resp = requests.get(f"{BASE_URL}/health")
    print(resp.json())
    
    print("\n--- 2. Creating Thread ---")
    resp = requests.post(f"{BASE_URL}/threads")
    data = resp.json()
    thread_id = data["thread_id"]
    print(f"Thread ID: {thread_id}")
    
    print("\n--- 3. Asking First Question (Factual) ---")
    query1 = "What is the exit load for SBI Bluechip Fund?"
    resp = requests.post(f"{BASE_URL}/threads/{thread_id}/messages", json={"query": query1})
    res1 = resp.json()
    print(f"Q: {query1}")
    print(f"A: {res1['answer'][:100]}...")
    print(f"Scheme Detected: {res1['scheme_name']}")
    
    print("\n--- 4. Asking Follow-up (Context Memory) ---")
    query2 = "What is its expense ratio?"
    resp = requests.post(f"{BASE_URL}/threads/{thread_id}/messages", json={"query": query2})
    res2 = resp.json()
    print(f"Q: {query2}")
    print(f"A: {res2['answer'][:100]}...")
    print(f"Scheme Used (from context): {res2['scheme_name']}")
    
    print("\n--- 5. Verifying Parallel Thread (Independent Memory) ---")
    resp_t2 = requests.post(f"{BASE_URL}/threads")
    thread_id_2 = resp_t2.json()["thread_id"]
    query3 = "What is its expense ratio?" # No context in this thread
    resp = requests.post(f"{BASE_URL}/threads/{thread_id_2}/messages", json={"query": query3})
    res3 = resp.json()
    print(f"T2 Q: {query3}")
    print(f"T2 Scheme: {res3['scheme_name']} (Should be None/General)")
    
    print("\n--- 6. Verifying History ---")
    resp = requests.get(f"{BASE_URL}/threads/{thread_id}")
    history = resp.json()["history"]
    print(f"History length for T1: {len(history)}")
    for msg in history:
        print(f"[{msg['role']}]: {msg['content'][:50]}...")

if __name__ == "__main__":
    # Wait for server to be ready
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health")
            break
        except:
            print("Waiting for server...")
            time.sleep(5)
    
    test_api()
