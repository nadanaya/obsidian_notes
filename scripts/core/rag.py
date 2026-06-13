import chromadb
import numpy as np

chroma = chromadb.PersistentClient(path="../rag_db")
col = chroma.get_or_create_collection("brain")


def embed(text):
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(384).tolist()


def add_document(doc_id, text):
    col.add(
        ids=[doc_id],
        embeddings=[embed(text)],
        documents=[text],
        metadatas=[{"source": doc_id}]
    )


def search(query, k=6):
    res = col.query(
        query_embeddings=[embed(query)],
        n_results=k,
        include=["documents", "metadatas"]
    )

    return [
        {
            "text": res["documents"][0][i],
            "source": res["metadatas"][0][i].get("source", "unknown")
        }
        for i in range(len(res["documents"][0]))
    ]