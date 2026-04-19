import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

print(f"--- Testing Groq Connection ---")
print(f"Model: {model}")
print(f"API Key: {'SET' if api_key else 'MISSING'}")

if not api_key:
    print("ERROR: GROQ_API_KEY not found in .env")
    exit(1)

try:
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say hello",
            }
        ],
        model=model,
    )
    print(f"SUCCESS: {chat_completion.choices[0].message.content}")
except Exception as e:
    print(f"FAILURE: {e}")
