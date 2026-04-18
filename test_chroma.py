import os
from dotenv import load_dotenv
import chromadb

# Load variables from your .env file
load_dotenv()

def test_connection():
    print("--- Testing Chroma Cloud Connection ---")
    
    tenant = os.getenv("CHROMA_TENANT")
    database = os.getenv("CHROMA_DATABASE")
    api_key = os.getenv("CHROMA_API_KEY")

    print(f"Tenant: {tenant}")
    print(f"Database: {database}")
    print(f"API Key: {'SET (Length: ' + str(len(api_key)) + ')' if api_key else 'NOT SET'}")

    try:
        client = chromadb.CloudClient(
            tenant=tenant,
            database=database,
            api_key=api_key
        )
        # The heartbeat call verifies if the API Key is actually authorized
        print(f"Heartbeat: {client.heartbeat()}")
        print("SUCCESS: Connection authorized!")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_connection()
