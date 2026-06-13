from pathlib import Path

from core.rag import add_document
from core.graph import save_graph
from core.auto_organize import analyze_note

VAULT = r"C:\Users\yeoh0\Brain"


def ingest():
    print("🧠 ingest start")

    for f in Path(VAULT).rglob("*.md"):
        text = f.read_text(encoding="utf-8")

        # 1. RAG 저장
        add_document(f.stem, text)

        # 2. Graph 업데이트
        save_graph()

        # 3. AI 자동 분석
        analysis = analyze_note(text)

        print(f"\n📌 {f.name}")
        print(analysis)


if __name__ == "__main__":
    ingest()