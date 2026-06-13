from connectors.obsidian import load_obsidian
from core.rag import add_document


def ingest():
    notes = load_obsidian()

    for n in notes:
        add_document(n["id"], n["text"])
        print("ingested:", n["id"])


if __name__ == "__main__":
    ingest()