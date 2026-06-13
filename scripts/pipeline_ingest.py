from pathlib import Path
from rag_engine import add_document
from graph_engine import save_graph

VAULT = r"C:\Users\yeoh0\Brain\Projects"

def ingest():
    for f in Path(VAULT).glob("*.md"):
        text = f.read_text(encoding="utf-8")

        add_document(
            doc_id=f.stem,
            text=text
        )

        print("ingested:", f.name)

    save_graph()
    print("graph updated")

if __name__ == "__main__":
    ingest()