import requests

def rerank(query, results):
    if not results:
        return []

    items = ""
    for i, r in enumerate(results):
        items += f"""
[{i}]
SOURCE: {r['source']}
TEXT: {r['text'][:300]}
"""

    prompt = f"""
다음 문서들을 질문과의 관련성 순으로 정렬해라.

질문: {query}

출력은 index 순서만:
예: [2,0,1]

문서:
{items}
"""

    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    try:
        order = eval(res.json()["response"])
    except:
        order = list(range(len(results)))

    return [results[i] for i in order if i < len(results)]