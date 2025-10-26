import os
from dotenv import load_dotenv

# load .env from project root
load_dotenv()

API_KEY_OPENAI = os.getenv("OPENAI_API_KEY")
API_KEY_ASSEMBLYAI = os.getenv("API_KEY_ASSEMBLYAI")