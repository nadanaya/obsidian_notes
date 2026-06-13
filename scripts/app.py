import sys
import json
import os
import subprocess
import streamlit as st
import requests
from pathlib import Path

# 1. 경로 설정
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

core_dir = scripts_dir / "core"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

VAULT_ROOT = Path(__file__).resolve().parent.parent
GRAPH_PATH = scripts_dir / "graph" / "graph.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

# --- 스트림릿 UI 세팅 ---
st.set_page_config(page_title="AI Brain OS Dashboard", page_icon="🧠", layout="wide")

# CSS로 UI 디자인 살짝 보강 (노션 스타일 및 컴팩트 레이아웃)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #f0f2f6; }
    .status-box { padding: 10px; border-radius: 5px; background-color: #f9f9f9; border: 1px solid #ddd; margin-bottom: 10px; }
    div[data-testid="stExpander"] { border-radius: 8px; border: 1px solid #e0e0e0; background-color: #ffffff; box-shadow: 0px 2px 4px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 사이드바: 컨트롤 타워 ---
st.sidebar.title("🧠 Brain Control")

# 지식 통계 표시부
if GRAPH_PATH.exists():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
    st.sidebar.metric("인덱싱된 지식(Nodes)", f"{len(graph_data.get('nodes', []))}개")
    st.sidebar.metric("연결된 지식 링크(Edges)", f"{len(graph_data.get('edges', []))}개")

st.sidebar.markdown("---")

# 🚀 핵심 기능: 원클릭 동기화 버튼 (벡터 DB 동기화 단계 포함)
st.sidebar.subheader("⚙️ Maintenance")
if st.sidebar.button("🔄 뇌 진화 및 지식 동기화 시작"):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        # 1단계: Evolve (AI 노트 Refactoring)
        with st.status("1단계: AI 노트 진화 중...", expanded=True) as status:
            st.write("Ollama를 통해 마크다운 구조를 최적화하고 있습니다.")
            subprocess.run(["python", "scripts/core/evolve.py"], check=True, env=env, cwd=VAULT_ROOT)
            status.update(label="✅ 1단계: 진화 완료", state="complete")

        # 2단계: Linker (자동 위키링크 생성)
        with st.status("2단계: 지식 관계 자동 연결 중...", expanded=True) as status:
            st.write("노트 간의 의미론적 연결([[링크]])을 생성 중입니다.")
            subprocess.run(["python", "scripts/core/linker_engine.py"], check=True, env=env, cwd=VAULT_ROOT)
            status.update(label="✅ 2단계: 연결 완료", state="complete")

        # 3단계: Graph/MOC (데이터 구조화)
        with st.status("3단계: 지식 지도 최신화 중...", expanded=True) as status:
            st.write("MOC 대시보드 및 그래프 데이터를 갱신 중입니다.")
            subprocess.run(["python", "scripts/graph_engine.py"], check=True, env=env, cwd=VAULT_ROOT)
            status.update(label="✅ 3단계: 구조화 완료", state="complete")

        # 🔥 4단계: ChromaDB Embedding Sync (새로 커스텀 탑재된 기능)
        with st.status("4단계: 지식 공간 벡터 DB 동기화 중...", expanded=True) as status:
            st.write("새로 백업된 메모들의 의미 매핑 공간을 빌드업합니다.")
            from core.rag_engine import update_vector_db
            update_vector_db()
            status.update(label="✅ 4단계: 벡터 DB 공간 정렬 완료", state="complete")

        st.sidebar.success("✨ 모든 동기화가 성공적으로 완료되었습니다!")
        st.balloons() 
        st.rerun()    

    except Exception as e:
        st.sidebar.error(f"❌ 동기화 도중 오류 발생: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Last Sync: 2026-06-13")


# --- 7:3 복합 화면 분할 레이아웃 배치 ---
col_chat, col_ref = st.columns([7, 3])

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_references" not in st.session_state:
    st.session_state.current_references = []

# --- 1️⃣ 좌측: 챗봇 세션 패널 (70% 비율) ---
with col_chat:
    st.title("💬 My AI Brain Assistant")
    st.caption("과거 검색 기록을 지능적으로 추적하여 폴더 전체를 의미 기반으로 탐색합니다.")
    
    # 기존 대화 렌더링
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 입력 제어부
    if user_input := st.chat_input("질문하면 내 메모를 벡터 검색하여 대답해줍니다."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("내 두뇌 벡터 자산을 탐색하고 문맥을 조립하는 중..."):
                try:
                    # 개조된 rag_engine에서 (doc, source) 묶음 배열을 리턴 받음
                    from core.rag_engine import search as vector_search
                    search_results = vector_search(user_input)
                    
                    # 우측 패널 갱신을 위해 세션에 참조 메타데이터 백업
                    st.session_state.current_references = search_results
                    
                    # LLM 전송용 컨텍스트 컨테이너 조립
                    context_accumulator = ""
                    for doc, source in search_results:
                        context_accumulator += f"\n\n[출처 메모 자산: {source}]\n{doc}"
                    
                    # LLM 프롬프트 조립
                    prompt = f"""You are a helpful AI Assistant connected to the user's personal knowledge base.
Answer the user's question ONLY using the provided context from their personal notes in Korean.
If the context doesn't contain enough info to completely answer, formulate the best response based on available notes.

[Context from personal notes]
{context_accumulator}

[User Question]
{user_input}
"""
                    # Ollama API 호출
                    r = requests.post(
                        OLLAMA_URL, 
                        json={"model": "llama3", "prompt": prompt, "stream": False},
                        timeout=30
                    )
                    answer = r.json()["response"]
                    st.write(answer)
                    
                    # 히스토리 추가 및 뷰어 갱신을 위한 리런
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"응답 생성 중 오류 발생: {e}")

# --- 2️⃣ 우측: 실시간 지식 카드 참조 뷰어 패널 (30% 비율) ---
with col_ref:
    st.markdown("### 📄 AI가 참고한 지식 카드")
    
    if st.session_state.current_references:
        st.caption("질문 분석 시 매핑된 상위 메모 자산입니다. 클릭 시 원문 조회가 가능합니다.")
        
        for idx, (doc, source) in enumerate(st.session_state.current_references):
            # 첫 번째로 매핑된 가장 중요한 문서는 기본적으로 열려있도록(expanded) 설정
            with st.expander(f"📌 {source}.md", expanded=(idx == 0)):
                # 마크다운 서식을 그대로 깨지지 않게 보존하여 스크롤 박스로 표시
                st.code(doc, language="markdown")
    else:
        st.info("💡 챗봇에게 지식 검색을 요청하면 과거 검색 발자취를 추적해 이곳에 매핑된 실제 옵시디언 메모 원본을 자동으로 로드해 줍니다.")