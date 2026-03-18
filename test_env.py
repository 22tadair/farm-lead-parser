import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

if key:
    print(f"Success! Key found: {key[:5]}...{key[-4:]}")
else:
    print("Failure: Could not find GEMINI_API_KEY in .env file.")
