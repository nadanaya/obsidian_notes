import os
from pathlib import Path

BASE_DIR = Path(os.getenv("BRAIN_BASE_DIR", Path(__file__).resolve().parents[1]))

OBSIDIAN_PATH = BASE_DIR / "Projects"
RAG_DB_PATH = BASE_DIR / "rag_db"
GRAPH_PATH = BASE_DIR / "graph" / "graph.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

EMBEDDING_DIM = 384
TOP_K = 5

GITHUB_USER = "nadanaya"
