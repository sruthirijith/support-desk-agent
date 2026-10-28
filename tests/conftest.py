import os

# Fake values so modules can be imported without real credentials.
# The tests never call Gemini or PostgreSQL.
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("EMBED_MODEL", "models/test-embedding")
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/test")
