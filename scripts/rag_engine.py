import json
from pathlib import Path
import chromadb
import requests  # Ollama API 호출용

VAULT = r"C:\Users\yeoh0\Brain"
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
HISTORY_PATH = SCRIPTS_DIR / "graph" / "search_history.json"

# ChromaDB 로컬 영구 저장소 설정
chroma = chromadb.PersistentClient(path=str(SCRIPTS_DIR / "rag_db"))
col = chroma.get_or_create_collection("brain")

OLLAMA_URL = "http://localhost:11434/api/embeddings"


def embed(text):
    """Ollama를 사용하여 문장의 실제 문맥적 의미를 768차원 벡터로 추출합니다."""
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=10
        )
        return r.json()["embedding"]
    except Exception as e:
        # 에러 발생 시 폴백(Fallback)용 가짜 벡터 생성 (0으로 채움)
        print(f"❌ 임베딩 추출 실패 (Ollama 상태 확인 필요): {e}")
        return [0.0] * 768


# =========================
# 과거 검색 기록 조사 로직 (요청하신 기능)
# =========================
def get_enhanced_query(query):
    """최근 검색 기록을 자동 조사하여 유저의 숨은 문맥을 쿼리에 융합합니다."""
    context_modifier = ""
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
            # 최근에 검색했던 명령어/키워드 최대 3개 추출
            recent_queries = [h["query"] for h in history[-3:] if h["query"] != query]
            if recent_queries:
                # 검색 공간을 유저 관심사 방향으로 살짝 유도하기 위한 힌트 주입
                context_modifier = f" (연관 관심 문맥: {', '.join(recent_queries)})"
        except:
            pass
            
    # 이번 검색 기록도 파일에 세이브
    save_query_history(query)
    return query + context_modifier


def save_query_history(query):
    """유저의 질문 발자취를 json 파일에 누적 기록합니다."""
    history = []
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
    
    # 중복 저장 방지 및 기록 업데이트
    history = [h for h in history if h["query"] != query]
    history.append({"query": query})
    
    # 최근 30개까지만 타이트하게 관리
    history = history[-30:]
    
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


# =========================
# 저장 (Vault 전체 스캔용)
# =========================
def update_vector_db():
    """모든 마크다운 노트를 읽어서 임베딩 벡터화 후 컬렉션에 갱신 처리합니다."""
    print("🔮 지식 임베딩 공간 생성 및 벡터 DB 빌드업 시작...")
    
    # Ollama 엔진에 임베딩 모델이 없다면 미리 자동으로 받아두기 명령
    try:
        requests.post("http://localhost:11434/api/pull", json={"name": "nomic-embed-text"})
    except:
        pass

    for f in Path(VAULT).rglob("*.md"):
        # 블랙리스트 및 예외 폴더 필터링
        if ".obsidian" in f.parts or "Archive" in f.parts or f.name.startswith("🗂️") or f.name == "README.md":
            continue
        try:
            text = f.read_text(encoding="utf-8").strip()
            if not text:
                continue
            
            # 컬렉션에 데이터 삽입 (있으면 갱신, 없으면 추가)
            col.upsert(
                ids=[f.stem],
                embeddings=[embed(text)],
                documents=[text],
                metadatas=[{"source": f.stem}]
            )
            print(f"📦 벡터 매핑 완료: {f.name}")
        except Exception as e:
            print(f"❌ {f.name} 벡터화 실패: {e}")
    print("✨ 벡터 데이터베이스가 완벽하게 동기화되었습니다!")


# =========================
# 검색 (과거 기록 자동 조사 탑재)
# =========================
def search(query, k=3):
    # 1. 자동 검색 기록 기반 쿼리 튜닝
    enhanced_query = get_enhanced_query(query)
    
    # 2. 크로마 DB 쿼리
    res = col.query(
        query_embeddings=[embed(enhanced_query)],
        n_results=k,
        include=["documents", "metadatas"]
    )

    results = []
    if res and res["documents"] and res["documents"][0]:
        docs = res["documents"][0]
        metas = res["metadatas"][0]

        for i in range(len(docs)):
            doc = docs[i]
            meta = metas[i] if metas else {}
            source = meta.get("source", "unknown")
            results.append((doc, source))

    return results