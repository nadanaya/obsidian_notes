import os
import subprocess
from pathlib import Path

BASE = Path(r"C:\Users\yeoh0\Brain\scripts")

print("\n🧠 AI Brain Booting...\n")

# =========================
# 1. RAG + Graph 초기화
# =========================
print("📥 Ingesting Obsidian...")
subprocess.run(["python", "pipeline_ingest.py"], cwd=BASE)

# =========================
# 2. Graph 업데이트
# =========================
print("🔗 Building Graph...")
subprocess.run(["python", "graph_engine.py"], cwd=BASE)

# =========================
# 3. Ollama 체크 (옵션)
# =========================
print("🧠 Checking Ollama...")

try:
    subprocess.run(["ollama", "list"], check=True)
except:
    print("⚠️ Ollama 안 켜져 있음 → ollama run llama3 실행 필요")

# =========================
# 4. Brain 실행
# =========================
print("\n🚀 Brain Ready!\n")

subprocess.run(["python", "brain_query.py"], cwd=BASE)