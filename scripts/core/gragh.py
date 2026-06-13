from pathlib import Path
import json
import re

VAULT = r"C:\Users\yeoh0\Brain"

GRAPH_PATH = Path(VAULT) / "graph" / "graph.json"


def extract_links(text):
    return re.findall(r"\[\[(.*?)\]\]", text)


def build_graph():
    nodes = set()
    edges = []

    for f in Path(VAULT).rglob("*.md"):
        text = f.read_text(encoding="utf-8")

        nodes.add(f.stem)

        for link in extract_links(text):
            nodes.add(link)
            edges.append({
                "from": f.stem,
                "to": link
            })

    return {
        "nodes": list(nodes),
        "edges": edges
    }


def save_graph():
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)

    graph = build_graph()

    GRAPH_PATH.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("🧠 Graph updated")