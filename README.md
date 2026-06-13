# Obsidian Notes

Personal Obsidian vault and AI Brain OS scripts.

## Contents

- `inbox/`, `Projects/`, and other vault folders contain personal Markdown notes.
- `scripts/` contains local RAG, graph, and Streamlit dashboard utilities.
- `connectors/` contains integration helpers.

## Run

```bash
streamlit run scripts/app.py
```

The Streamlit dashboard expects Ollama to be available at `http://localhost:11434`.

## Useful Commands

```bash
cd C:\Users\yeoh0\Brain
streamlit run scripts/app.py
```

If the browser does not open automatically, visit `http://localhost:8501`.

```bash
cd C:\Users\yeoh0\Brain
python scripts/core/evolve.py
```

Expected output starts like:

```text
🧠 Evolution started...
🔍 Analyzing: Android Studio 앱 설치 주소 오류.md...
```

```bash
cd C:\Users\yeoh0\Brain\scripts
python github_sync.py
```

Expected output starts like:

```text
GitHub 저장소 동기화 시작...
생성 완료: ai-agent
```

```bash
cd C:\Users\yeoh0\Brain
python scripts/core/linker_engine.py
```
