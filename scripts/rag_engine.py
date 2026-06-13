import chromadb
import numpy as np

chroma = chromadb.PersistentClient(path="../rag_db")
col = chroma.get_or_create_collection("brain")


def embed(text):
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(384).tolist()


# =========================
# 저장
# =========================
def add_document(doc_id, text):
    col.add(
        ids=[doc_id],
        embeddings=[embed(text)],
        documents=[text],
        metadatas=[{"source": doc_id}]  # ✔ 핵심
    )


# =========================
# 검색 (중요 수정)
# =========================
def search(query, k=5):
    res = col.query(
        query_embeddings=[embed(query)],
        n_results=k,
        include=["documents", "metadatas"]  # ✔ 필수
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]

    results = []

    for i in range(len(docs)):
        doc = docs[i]
        meta = metas[i] if metas else {}

        source = meta.get("source", None)

        if not source:
            source = "unknown"

        results.append((doc, source))

    return results