**Obsidian Notes and AI Brain OS Scripts**

### Overview
The Obsidian vault contains various folders for personal Markdown notes, local RAG, graph, and Streamlit dashboard utilities, as well as integration helpers.

#### Running the Dashboard
To run the Streamlit dashboard, execute the command: `streamlit run scripts/app.py`
The dashboard expects Ollama to be available at `http://localhost:11434`.

### Useful Commands

1. **Run the Dashboard**
	* Navigate to the Brain directory: `cd C:\Users\yeoh0\Brain`
	* Run the command: `streamlit run scripts/app.py`
	* If the browser does not open automatically, visit `http://localhost:8501`

2. **Evolve AI**
	* Navigate to the Brain directory: `cd C:\Users\yeoh0\Brain`
	* Run the command: `python scripts/core/evolve.py`
	* Expected output starts like: `🧠 Evolution started... 🔍 Analyzing: Android Studio 앱 설치 주소 오류.md...`

3. **Sync GitHub Repository**
	* Navigate to the scripts directory: `cd C:\Users\yeoh0\Brain\scripts`
	* Run the command: `python github_sync.py`
	* Expected output starts like: `GitHub 저장소 동기화 시작... 생성 완료: ai-agent`

4. **Run the Linker Engine**
	* Navigate to the Brain directory: `cd C:\Users\yeoh0\Brain`
	* Run the command: `python scripts/core/linker_engine.py`

5. **Import Chrome History**
	* Navigate to the Brain directory: `cd C:\Users\yeoh0\Brain`
	* Preview today's import: `python scripts/import_chrome_history.py --dry-run`
	* Import today's recent Chrome visits: `python scripts/import_chrome_history.py`
	* Import more rows or days: `python scripts/import_chrome_history.py --limit 300 --days 7`
	* By default, notes are classified through `scripts/ai_classifier.py` and saved as concept notes such as `Knowledge\Database\Transaction.md`, with summaries, references, and `[[Wiki Links]]`.
	* To keep date-based history logs instead, run: `python scripts/import_chrome_history.py --history-log`

6. **Extract Knowledge From Existing History Logs**
	* Preview concept notes from existing `Chrome History` files: `python scripts/extract_knowledge.py --dry-run`
	* Promote existing history logs into concept notes: `python scripts/extract_knowledge.py`
