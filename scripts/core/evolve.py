import sys
import requests
from pathlib import Path

# 1. 경로 설정 (최상단 고정)
scripts_dir = Path(__file__).resolve().parent.parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

core_dir = Path(__file__).resolve().parent
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

# 2. 엔진 파일 불러오기
from rag_engine import search
from graph_engine import save_graph

VAULT = r"C:\Users\yeoh0\Brain"
OLLAMA_URL = "http://localhost:11434/api/generate"


def analyze_and_rewrite(text):
    prompt = f"""
You are an expert Obsidian Knowledge Structure Refactoring AI.
Your ONLY task is to clean up, restructure, and improve the provided note.

[CRITICAL RULE]
You must ONLY respond using the exact format below. Do not include any conversational filler, introductory remarks, or markdown code blocks outside the tags.

=== REWRITTEN NOTE ===
(Write the improved, structured, and cleaned-up note content here. Include [[Wikilinks]] if necessary.)

=== TAGS ===
(Tags here)

=== LINKS ===
(Links here)

[INPUT NOTE]
{text}

[REMINDER]
Start your response immediately with "=== REWRITTEN NOTE ===". Do not say anything else.
"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "options": {
                "temperature": 0.1,
                "top_p": 0.1
            },
            "stream": False
        }
    )
    return r.json()["response"]


def evolve():
    print("🧠 Evolution started...")

    for f in Path(VAULT).rglob("*.md"):
        # 숨김 폴더나 백업 폴더 패스
        if ".obsidian" in f.parts or "Archive" in f.parts:
            continue

        try:
            text = f.read_text(encoding="utf-8")

            # 💡 [핵심 추가] 이미 진화가 완료된 파일은 굳이 Ollama 안 거치고 바로 패스!
            if "=== REWRITTEN NOTE ===" in text:
                print(f"⏭️ Already evolved (Skip): {f.name}")
                continue

            print(f"🔍 Analyzing: {f.name}...")
            result = analyze_and_rewrite(text)

            if "=== REWRITTEN NOTE ===" in result:
                parts = result.split("=== REWRITTEN NOTE ===")[1]
                
                if "=== TAGS ===" in parts:
                    new_content = parts.split("=== TAGS ===")[0].strip()
                else:
                    new_content = parts.strip()

                if new_content:
                    f.write_text(new_content, encoding="utf-8")
                    print(f"♻️ evolved: {f.name}")
            else:
                print(f"⚠️ {f.name}은 AI가 포맷을 지키지 않아 건너뜁니다.")

        except Exception as e:
            print(f"❌ {f.name} 처리 중 에러 발생: {e}")

    # 모든 파일 진화 완료 후 지식 그래프 최신화
    print("🔗 Updating Knowledge Graph...")
    try:
        save_graph()
        print("✨ All processes finished successfully!")
    except Exception as e:
        print(f"❌ 그래프 저장 실패: {e}")


if __name__ == "__main__":
    evolve()