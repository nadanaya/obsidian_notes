# Obsidian Notes and AI Brain OS

Public-safe Obsidian vault sample and Python utilities for organizing Markdown notes with local AI/RAG workflows.

## Highlights

- Markdown vault structure for project, learning, and AI notes
- Python scripts for graph generation, note linking, RAG search, and local dashboard experiments
- Local Ollama-based workflows, designed to run without committing private API keys
- Sanitized public repository: personal inbox notes, browser history exports, and Obsidian workspace files are excluded

## Project Structure

```text
Projects/       portfolio/project notes
Knowledge/      curated concept notes
scripts/        AI, graph, RAG, and dashboard utilities
connectors/     local data connector helpers
graph/          public graph sample output
```

## Getting Started

Install the Python dependencies used by the scripts, then run the dashboard:

```bash
streamlit run scripts/app.py
```

Most AI features expect Ollama to be running locally:

```bash
ollama serve
```

## Privacy Notes

This repository is public. Do not commit:

- Chrome or browser history exports
- personal inbox notes
- `.obsidian/` workspace and plugin settings
- local vector databases or generated search history
- API keys, tokens, or account recovery notes

Private/local paths can be configured with `BRAIN_BASE_DIR`. If it is not set, scripts default to the repository root.
