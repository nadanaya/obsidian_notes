import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def ask_ollama(context, question):
    prompt = f"""
너는 개인 지식 AI다.

CONTEXT:
{context}

QUESTION:
{question}

짧고 정확하게 답해.
"""

    res = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return res.json()["response"]