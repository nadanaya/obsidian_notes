from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

VAULT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VAULT))

from connectors.chrome_history import ChromeVisit, find_profiles, read_history
from scripts.ai_classifier import classify

def safe_markdown_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")

def safe_heading(value: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|#^\[\]]+", "", value)
    return cleaned.strip() or "Untitled"

def build_note(folder: str, visits: list[ChromeVisit]) -> str:
    """날짜 개념을 완전히 제거하고, 단일 MOC 허브로 직결되는 단일 노드 본문을 생성합니다."""
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        "---",
        "source: chrome_history",
        f"category: {folder}",
        f"ingested_at: {now}",
        "tags:",
        "  - chrome-history",
        "  - auto-ingest",
        "---",
        "",
        f"# Chrome History - {folder}",
        "",
    ]

    by_topic = defaultdict(list)
    all_tags = set()
    all_links = set()

    classified_items = []
    for visit in visits:
        analysis = classify(visit.title, visit.url)
        classified_items.append((visit, analysis))
        by_topic[analysis.topic].append((visit, analysis))
        all_tags.update(analysis.tags)
        all_links.update(analysis.links)

    if all_tags:
        lines.extend(["## Tags", ""])
        lines.append(" ".join(f"#{tag}" for tag in sorted(all_tags)))
        lines.append("")

    if all_links:
        lines.extend(["## Graph Links", ""])
        # 핵심 MOC 기둥들이 최상단 그래프 링크로 직결됨
        lines.extend(f"- [[{link}]]" for link in sorted(all_links))
        lines.append("")

    for topic, items in sorted(by_topic.items()):
        lines.extend([f"## {safe_heading(topic)}", ""])

        for visit, analysis in items:
            title = safe_heading(visit.title)
            url = safe_markdown_text(visit.url)
            tags_text = " ".join(f"#{t}" for t in analysis.tags)
            links_text = ", ".join(f"[[{l}]]" for l in analysis.links) or "-"
            time_text = visit.visit_time.strftime("%H:%M")

            lines.extend(
                [
                    f"### {title}",
                    "",
                    f"- Time: {time_text}",
                    f"- URL: {url}",
                    f"- Summary: {safe_markdown_text(analysis.summary)}",
                    f"- Tags: {tags_text or '-'}",
                    f"- Links: {links_text}",
                    "",
                ]
            )

    lines.extend(["## Raw Table", "", "| Time | Topic | Title | URL | Visits |", "| --- | --- | --- | --- | ---: |"])
    for visit, analysis in classified_items:
        time_text = visit.visit_time.strftime("%H:%M")
        topic = safe_markdown_text(analysis.topic)
        title = safe_markdown_text(visit.title)
        url = safe_markdown_text(visit.url)
        lines.append(f"| {time_text} | {topic} | {title} | {url} | {visit.visit_count} |")

    lines.append("")
    return "\n".join(lines)

def existing_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(re.findall(r"https?://[^\s|]+", path.read_text(encoding="utf-8")))

def write_notes(visits: list[ChromeVisit], dry_run: bool = False) -> list[Path]:
    """[버그 박멸] 날짜 딕셔너리 그룹화를 완전히 없애고 오직 대분류 folder로만 묶어서 처리합니다."""
    grouped: dict[str, list[ChromeVisit]] = defaultdict(list)

    for visit in visits:
        analysis = classify(visit.title, visit.url)
        # 중요: 날짜를 떼고 오직 folder 키로만 누적 그룹화합니다.
        grouped[analysis.folder].append(visit)

    written: list[Path] = []
    # folder로만 순회를 돌기 때문에 폴더당 딱 1번만 파일 제어가 일어납니다.
    for folder, items in sorted(grouped.items()):
        target_dir = VAULT / folder / "Chrome History"
        target_path = target_dir / "Chrome History.md"
        
        known_urls = existing_urls(target_path)
        new_items = [item for item in items if item.url not in known_urls]

        if not new_items:
            continue

        if dry_run:
            written.append(target_path)
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            content = target_path.read_text(encoding="utf-8").rstrip()
            raw_note = build_note(folder, new_items)
            
            # 기존 마크다운 표 하단에 누적(Append) 행 데이터만 추출하여 병합
            if "| --- | --- | --- | --- | ---: |" in raw_note:
                addition = raw_note.split("| --- | --- | --- | --- | ---: |", 1)[1]
                target_path.write_text(f"{content}\n{addition}", encoding="utf-8")
            else:
                target_path.write_text(f"{content}\n\n{raw_note}", encoding="utf-8")
        else:
            target_path.write_text(build_note(folder, new_items), encoding="utf-8")

        written.append(target_path)

    return written

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Chrome history into Obsidian notes.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of history rows to import.")
    parser.add_argument("--days", type=int, default=1, help="Only import visits from the last N days.")
    parser.add_argument("--profile", help="Chrome profile folder name, such as Default or 'Profile 1'.")
    parser.add_argument("--dry-run", action="store_true", help="Show target notes without writing files.")
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    profiles = find_profiles()
    if args.profile:
        profile = VAULT.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / args.profile
    elif profiles:
        profile = profiles[0]
    else:
        raise SystemExit("No Chrome profile with a History database was found.")

    visits = read_history(profile, limit=args.limit, days=args.days)
    written = write_notes(visits, dry_run=args.dry_run)

    action = "Would write" if args.dry_run else "Wrote"
    print(f"{action} {len(written)} note(s) from {len(visits)} Chrome history item(s).")
    for path in written:
        print(path.relative_to(VAULT))

if __name__ == "__main__":
    main()