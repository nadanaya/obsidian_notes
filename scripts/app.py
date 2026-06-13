import sys
import json
import streamlit as st
import requests
from pathlib import Path

# 1. 경로 설정 (상위 및 엔진 폴더 인식)
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

core_dir = scripts_dir / "core"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

# 엔진 파일 import
try:
    from rag_engine import search
except ImportError:
    def search(query):
        return f"[{query}]에 대한 메모 검색 결과가 여기에 표시됩니다."

# 데이터 경로
GRAPH_PATH = scripts_dir / "graph" / "graph.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

# --- 스트림릿 UI 세팅 ---
st.set_page_config(page_title="Brain OS Dashboard", page_icon="🧠", layout="wide")

st.title("🧠 AI Brain OS - 나만의 지식 비서")
st.caption("내가 작성한 Obsidian 노트를 기반으로 사고하고 답하는 로직 시스템")

# 좌측 사이드바: 통계 및 제어
st.sidebar.header("📊 나의 자산 현황")
if GRAPH_PATH.exists():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    st.sidebar.metric("인덱싱된 총 노드 수", f"{len(graph_data.get('nodes', []))}개")
    st.sidebar.metric("연결된 지식 링크(Edges)", f"{len(graph_data.get('edges', []))}개")
else:
    st.sidebar.warning("graph.json 파일을 찾을 수 없습니다. graph_engine을 먼저 실행하세요.")

st.sidebar.markdown("---")
st.sidebar.info("시스템 가동 중 | 2026-06-13")

# 메인 화면: 챗봇 세션
st.subheader("💬 내 지식 기반 AI 챗봇")

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 유저 입력창
if user_input := st.chat_input("내 메모에 대해 궁금한 점을 물어보세요! (예: DB 트랜잭션 안전하게 처리하는 법 알려줘)"):
    # 1. 유저 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. RAG 엔진 가동 (관련 노트 검색)
    with st.spinner("🧠 내 지식 저장소를 뒤지는 중..."):
        context = search(user_input)

    # 3. Ollama 모델에게 컨텍스트와 함께 질문 조립
    with st.chat_message("assistant"):
        response_placeholder = st.empty()

        prompt = f"""
You are a helpful AI Assistant connected to the user's personal knowledge base (Obsidian Vault).
Answer the user's question ONLY using the provided context from their personal notes.

[CRITICAL RULES]
- ALWAYS answer in Korean. (무조건 한국어로만 답변하세요.)
- Do not use English for the final response unless it's a technical term.
- If the context doesn't contain the answer, say "내 메모에서 관련 내용을 찾을 수 없습니다."

[Context from personal notes]
{context}

[User Question]
{user_input}
"""
        try:
            r = requests.post(
                OLLAMA_URL,
                json={"model": "llama3", "prompt": prompt, "stream": False},
                timeout=30,
            )
            answer = r.json()["response"]
            response_placeholder.write(answer)
            # 4. 어시스턴트 메시지 저장
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Ollama 통신 실패: {e}")
