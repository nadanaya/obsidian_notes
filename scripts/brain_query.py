from rag_engine import search
from ollama_brain import ask_ollama
from graph_engine import save_graph


def brain(query):
    save_graph()

    results = search(query)

    if not results:
        return "📌 관련 노트를 찾지 못했습니다."

    # =========================
    # context 생성
    # =========================
    context = "\n\n".join([r[0] for r in results])

    # =========================
    # sources 정리 (강화 버전)
    # =========================
    sources = []
    for r in results:
        source = r[1]

        if not source or source == "unknown":
            continue

        sources.append(source)

    # 중복 제거
    sources = list(set(sources))

    # fallback (디버깅용)
    if not sources:
        sources = ["⚠️ source metadata 없음 (rag_engine 확인 필요)"]

    # =========================
    # LLM 호출
    # =========================
    answer = ask_ollama(context, query)

    return f"""
🧠 답변:
{answer}

📌 근거 노트:
- {chr(10).join(sources)}
"""


if __name__ == "__main__":
    print("🧠 AI Brain Ready")

    while True:
        q = input("\n질문: ")
        print("\n" + brain(q))