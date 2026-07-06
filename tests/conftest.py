import os
import sys
from pathlib import Path

# Make the app package importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Dummy credentials so app.core.config loads without a real .env
os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")
os.environ.setdefault("MODEL_NAME", "llama-3.3-70b-versatile")
