import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def analyze_note(text):
    prompt = f"""
너는 Obsidian 지식 정리 AI다.

다음 노트를 분석해서:

1. 태그 3개
2. 요약 1줄
3. 연결 가능한 개념 (existing wiki link 형태)

형식:
TAGS: ...
SUMMARY: ...
LINKS: [[...]], [[...]]

노트:
{text}
"""

    res = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return res.json()["response"]