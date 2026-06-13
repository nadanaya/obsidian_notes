from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

VALID_FOLDERS = {"Archive", "Knowledge", "Learning", "Projects", "Ideas", "Meeting", "People"}

@dataclass(frozen=True)
class AIResult:
    folder: str
    topic: str
    note_name: str
    summary: str
    tags: list[str]
    links: list[str]

def normalize_tag(value: str) -> str:
    tag = re.sub(r"[^0-9a-zA-Z가-힣_-]+", "-", value.strip().lower()).strip("-")
    return tag or "knowledge"

def clean_topic(value: str) -> str:
    topic = re.sub(r"\s+", " ", value).strip()
    topic = re.sub(r"[\\/:*?\"<>|#^\[\]]+", "", topic)
    return topic[:80] or "General"

def domain_from_url(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    return domain.removeprefix("www.")

def result(
    folder: str,
    topic: str,
    note_name: str,
    summary: str,
    tags: list[str],
    links: list[str],
) -> AIResult:
    if folder not in VALID_FOLDERS:
        folder = "Knowledge"

    cleaned_tags = []
    for tag in tags:
        normalized = normalize_tag(tag)
        if normalized not in cleaned_tags:
            cleaned_tags.append(normalized)

    cleaned_links = []
    for link in links:
        cleaned = clean_topic(link)
        if cleaned and cleaned not in cleaned_links and cleaned.lower() != note_name.lower():
            cleaned_links.append(cleaned)

    return AIResult(
        folder=folder,
        topic=clean_topic(topic),
        note_name=clean_topic(note_name),
        summary=summary.strip() or clean_topic(topic),
        tags=cleaned_tags,
        links=cleaned_links,
    )

def classify(title: str, url: str) -> AIResult:
    text = f"{title} {url}".lower()
    domain = domain_from_url(url)
    summary = title.strip() or url

    # 1. 💻 Backend MOC 분류 (Java, Spring, DB, Transaction, API)
    concept = classify_development_concept(text, title, summary)
    if concept is not None:
        return concept

    # 2. 🤖 AI MOC 분류 (ChatGPT, GPT, OpenAI, AI-Agent, LangChain, Copilot, Gemini)
    if any(term in text for term in ["chatgpt", "chat gpt", "openai", "agent", "langchain", "copilot", "gemini", "gpt", "llm", "rag", "vector"]):
        note_name = "ChatGPT"
        if "agent" in text: note_name = "AI-Agent"
        elif "langchain" in text: note_name = "LangChain"
        elif "copilot" in text: note_name = "Copilot"
        elif "gemini" in text: note_name = "Gemini"
        elif "openai" in text or "platform.openai.com" in text: note_name = "OpenAI"
        elif "gpt" in text: note_name = "GPT"
        elif "rag" in text: note_name = "RAG"
        elif "vector" in text: note_name = "Vector Database"

        # 핵심 지식은 AI MOC 기둥에 밀착 연결
        return result(
            folder="Knowledge",
            topic="AI",
            note_name=note_name,
            summary=summary,
            tags=["ai", "tool"],
            links=["AI MOC"]
        )

    # 3. 🚀 Project MOC 분류 (DentaLink, nadanaya, pigge, paw-mate, kakao-map 등)
    if "github.com" in domain or "github" in text or any(p in text for p in ["dentalink", "nadanaya", "pigge", "paw-mate", "kakao-map"]):
        topic = "Project"
        repo_name = "GitHub"
        if "github.com" in domain:
            parts = [p for p in urlparse(url).path.split("/") if p]
            if len(parts) >= 2 and parts[0].lower() not in {"settings", "notifications", "organizations", "marketplace", "features", "topics"}:
                repo_name = parts[1]
        elif "dentalink" in text: repo_name = "DentaLink"
        elif "nadanaya" in text: repo_name = "nadanaya"
        elif "pigge" in text: repo_name = "pigge_server"
        elif "paw-mate" in text: repo_name = "paw-mate-backend"
        elif "kakao-map" in text: repo_name = "kakao-map"

        return result(
            folder="Projects",
            topic=topic,
            note_name=repo_name,
            summary=summary,
            tags=["project", "github"],
            links=["Project MOC"]
        )

    # 4. ✍️ Content MOC 및 📚 Learning MOC 매핑 (블로그, 코테, 자소서 등)
    if any(term in text for term in ["blog", "블로그", "spring_blog", "발표", "슬라이드", "플래시카드", "자소서", "이력서"]):
        note_name = "Blog" if "blog" in text else "Career"
        return result(folder="Archive", topic="Content", note_name=note_name, summary=summary, tags=["content"], links=["Content MOC"])

    if any(term in text for term in ["codingtest", "코딩테스트", "백준", "프로그래머스", "cs ", "cs지식", "readme"]):
        note_name = "CodingTest" if "coding" in text or "코딩" in text else "CS"
        return result(folder="Learning", topic="Study", note_name=note_name, summary=summary, tags=["learning"], links=["Learning MOC"])

    # 5. YouTube 처리 (학습/일반)
    if "youtube.com" in domain or "youtu.be" in domain:
        learning_terms = ["tutorial", "course", "lecture", "강의", "튜토리얼", "learn", "study"]
        if any(term in text for term in learning_terms):
            return result(folder="Learning", topic="Video", note_name="YouTube Learning", summary=summary, tags=["youtube", "learning"], links=["Learning MOC"])
        return result(folder="Archive", topic="Media", note_name="YouTube", summary=summary, tags=["media"], links=[])

    # Fallback 기본 분류
    return result(folder="Knowledge", topic="General", note_name=infer_topic(title, fallback="General"), summary=summary, tags=["knowledge"], links=[])

def classify_development_concept(text: str, title: str, summary: str) -> AIResult | None:
    if any(term in text for term in ["transaction", "트랜잭션", "db lock", "lock", "isolation"]):
        return result(folder="Knowledge", topic="Database", note_name="Transaction", summary=summary, tags=["database", "transaction"], links=["Backend MOC"])
    
    if any(term in text for term in ["jpa", "hibernate", "querydsl"]):
        return result(folder="Knowledge", topic="Spring", note_name="JPA", summary=summary, tags=["spring", "jpa"], links=["Backend MOC"])

    if any(term in text for term in ["spring", "스프링"]):
        return result(folder="Knowledge", topic="Spring", note_name="Spring", summary=summary, tags=["spring", "backend"], links=["Backend MOC"])

    if any(term in text for term in ["mysql", "postgres", "postgresql", "database", "db "]):
        return result(folder="Knowledge", topic="Database", note_name="Database", summary=summary, tags=["database"], links=["Backend MOC"])

    if any(term in text for term in ["java", "자바"]):
        return result(folder="Knowledge", topic="Java", note_name="Java", summary=summary, tags=["java"], links=["Backend MOC"])

    if any(term in text for term in ["api", "rest api", "endpoint"]):
        return result(folder="Knowledge", topic="API", note_name="API", summary=summary, tags=["api"], links=["Backend MOC"])

    return None

def infer_topic(title: str, fallback: str) -> str:
    title = re.sub(r"\s*[-|–—]\s*.*$", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    return clean_topic(title) if title else fallback
