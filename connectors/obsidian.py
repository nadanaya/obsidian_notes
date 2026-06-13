from pathlib import Path

VAULT = r"C:\Users\yeoh0\Brain"

def load_obsidian():
    data = []

    for f in Path(VAULT).rglob("*.md"):
        data.append({
            "id": f.stem,
            "text": f.read_text(encoding="utf-8")
        })

    return data