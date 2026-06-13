import requests
from core.rag import search


def ask_llm(context, q):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": f"""
너는 개인 지식 AI다.

CONTEXT:
{context}

QUESTION:
{q}

근거 기반으로 답하고 마지막에 관련 개념도 연결해.
""",
            "stream": False
        }
    )
    return r.json()["response"]


def brain(q):
    results = search(q)

    context = "\n\n".join([r["text"] for r in results])

    answer = ask_llm(context, q)

    return f"""
🧠 답변:
{answer}

📌 근거:
{chr(10).join([r['source'] for r in results])}
"""


if __name__ == "__main__":
    print("🧠 Brain Ready")

    while True:
        q = input("\n질문: ")
        print(brain(q))