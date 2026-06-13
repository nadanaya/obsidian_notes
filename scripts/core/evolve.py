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
from graph_engine import save_graph

VAULT = r"C:\Users\yeoh0\Brain"
OLLAMA_URL = "http://localhost:11434/api/generate"

# 대형 파일 및 분석 제외 파일 블랙리스트
IGNORE_FILES = [
    "README.md", 
    "ChatGPT Export.md", 
    "Chrome Bookmarks.md", 
    "🗂️ AI Brain OS 지식 지도 (MOC).md"
]


def analyze_and_rewrite(text):
    prompt = f"""
You are an expert Obsidian Knowledge Structure Refactoring AI.
Your ONLY task is to clean up, restructure, and improve the provided note.

[CRITICAL RULE]
You must ONLY respond using the exact format below. Do not include any conversational filler, introductory remarks, or markdown code blocks outside the tags.
The rewritten note MUST include the special tag "#evolved" at the very bottom.

=== REWRITTEN NOTE ===
(Write the improved, structured, and cleaned-up note content here. Include [[Wikilinks]] if necessary.)

#evolved

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
        # 1. 숨김 폴더, 백업 폴더, 블랙리스트 파일 패스
        if ".obsidian" in f.parts or "Archive" in f.parts or f.name in IGNORE_FILES:
            continue

        try:
            text = f.read_text(encoding="utf-8")

            # 2. ⚡ [핵심 수정] 이미 AI 진화가 완료된 노트는 0.1초 만에 패스!
            if "#evolved" in text or "## 🏷️ AI 분류 태그" in text:
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
                    # 저장할 때 하단에 #evolved 마킹을 남겨서 다음엔 스킵되도록 함
                    if "#evolved" not in new_content:
                        new_content += "\n\n#evolved"
                        
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