from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()  # reads GOOGLE_API_KEY from .env
for m in client.models.list():
    if "embed" in m.name:
        print(m.name)
