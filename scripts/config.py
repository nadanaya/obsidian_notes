from pathlib import Path

# =========================
# 📁 경로 설정
# =========================
BASE_DIR = Path(r"C:\Users\yeoh0\Brain")

OBSIDIAN_PATH = BASE_DIR / "Projects"
RAG_DB_PATH = BASE_DIR / "rag_db"
GRAPH_PATH = BASE_DIR / "graph" / "graph.json"

# =========================
# 🧠 LLM 설정 (Ollama)
# =========================
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

# =========================
# 🔍 RAG 설정
# =========================
EMBEDDING_DIM = 384
TOP_K = 5

# =========================
# 🌐 GitHub 설정
# =========================
GITHUB_USER = "nadanaya"