import sys
import json
import re
from pathlib import Path

# 1. 경로 정의 (경로 깨짐 원천 차단)
VAULT = r"C:\Users\yeoh0\Brain"
PROJECTS_DIR = Path(VAULT) / "Projects"

# graph.json 저장 위치를 절대 경로로 안전하게 고정
GRAPH_PATH = Path(__file__).resolve().parent / "graph" / "graph.json"
MOC_FILE = Path(VAULT) / "🗂️ AI Brain OS 지식 지도 (MOC).md"

# 기존 핵심 키워드 맵 유지
KEYS = {
    "rag": ["rag", "retrieval", "embedding"],
    "llm": ["llm", "gpt", "ollama"],
    "agent": ["agent", "automation", "tool"],
    "obsidian": ["obsidian", "note", "markdown"]
}


def build_graph_and_moc():
    print("🤖 지식 네트워크 연산 및 MOC 대시보드 정렬 시작...")
    
    # JSON 그래프용 데이터 구조
    nodes = set()
    edges = []
    
    # MOC 마크다운용 데이터 구조
    tag_cloud = {}
    all_notes_count = 0

    # Projects 폴더 내부의 마크다운 파일 탐색 (기존 로직 유지)
    if not PROJECTS_DIR.exists():
        # 혹시 Projects 폴더가 아니라 전체 Vault 순회할 경우를 대비한 안전장치
        search_dir = Path(VAULT)
    else:
        search_dir = PROJECTS_DIR

    for f in search_dir.rglob("*.md"):
        if ".obsidian" in f.parts or f == MOC_FILE:
            continue
            
        try:
            text = f.read_text(encoding="utf-8")
            all_notes_count += 1
            note_name = f.stem
            
            # --- 1. 기존 graph.json 노드/엣지 빌드 로직 ---
            nodes.add(note_name)
            t_lower = text.lower()
            for k, words in KEYS.items():
                if any(w in t_lower for w in words):
                    nodes.add(k)
                    edges.append({"from": note_name, "to": k})

            # --- 2. 신규 AI 태그 기반 MOC 큐레이션 로직 ---
            tags = re.findall(r"(?<!\[)#([\w/_-]+)", text)
            if tags:
                for tag in set(tags):
                    if tag not in tag_cloud:
                        tag_cloud[tag] = []
                    tag_cloud[tag].append(note_name)
            else:
                if "미분류_노트" not in tag_cloud:
                    tag_cloud["미분류_notes"] = []
                tag_cloud["미분류_notes"].append(note_name)

        except Exception as e:
            print(f"⚠️ {f.name} 처리 중 오류 (건너뜀): {e}")

    # --- 3. 🗂️ MOC 마크다운 파일 생성 코드 ---
    moc_content = [
        "# 🗂️ AI Brain OS 지식 지도 (MOC)",
        "> 🤖 AI가 자동으로 분류하고 인덱싱한 실시간 대시보드입니다.\n",
        "---",
        "## 🏷️ 인공지능 카테고리 맵 (Tags)"
    ]

    for tag in sorted(tag_cloud.keys()):
        notes_in_tag = tag_cloud[tag]
        moc_content.append(f"\n### 📂 #{tag}")
        for note in sorted(list(set(notes_in_tag))):
            moc_content.append(f"- [[{note}]]")

    moc_content.append("\n---")
    moc_content.append("\n## 📊 내뇌 자산 실시간 통계")
    moc_content.append(f"- 📝 **인덱싱된 총 노트 수:** {all_notes_count}개")
    moc_content.append(f"- 🏷️ **생성된 데이터 카테고리:** {len(tag_cloud)}개")
    moc_content.append(f"\n⏱️ **최근 동기화:** 2026-06-13")

    # 마크다운 파일 저장
    MOC_FILE.write_text("\n".join(moc_content), encoding="utf-8")
    print(f"📝 MOC 마크다운 대시보드 생성 완료!")

    # 데이터 반환
    return {"nodes": list(nodes), "edges": edges}


def save_graph():
    # 부모 폴더(graph)가 없으면 자동 생성
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 핵심 데이터 연산 실행 및 json 저장
    graph_data = build_graph_and_moc()
    GRAPH_PATH.write_text(
        json.dumps(graph_data, indent=2),
        encoding="utf-8"
    )
    print(f"📊 지식 그래프 데이터 동기화 완료: {GRAPH_PATH}")


if __name__ == "__main__":
    save_graph()