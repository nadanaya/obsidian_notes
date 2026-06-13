from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


VAULT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VAULT))
sys.path.insert(0, str(VAULT / "scripts"))

from connectors.chrome_history import ChromeVisit
from import_chrome_history import write_concept_notes


try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


ROW_RE = re.compile(r"^\|\s*(?P<time>\d{2}:\d{2})\s*\|")


def split_markdown_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]

    parts = re.split(r"(?<!\\)\|", line)
    return [part.strip().replace(r"\|", "|") for part in parts]


def parse_history_note(path: Path) -> list[ChromeVisit]:
    date_key = path.stem
    visits: list[ChromeVisit] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if not ROW_RE.match(line):
            continue

        parts = split_markdown_row(line)
        if len(parts) < 4:
            continue

        time_text, title, url, visit_count = parts[:4]
        if not url.startswith(("http://", "https://")):
            continue

        try:
            visit_time = datetime.fromisoformat(f"{date_key}T{time_text}:00").astimezone()
        except ValueError:
            visit_time = datetime.now().astimezone()

        try:
            count = int(visit_count)
        except ValueError:
            count = 0

        visits.append(
            ChromeVisit(
                title=title,
                url=url,
                visit_time=visit_time,
                visit_count=count,
            )
        )

    return visits


def find_history_notes(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(path).resolve() for path in paths]

    return sorted(VAULT.glob("*/Chrome History/*.md"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote Chrome History logs into concept notes.")
    parser.add_argument("paths", nargs="*", help="Optional Chrome History markdown files to extract from.")
    parser.add_argument("--dry-run", action="store_true", help="Show concept notes without writing files.")
    parser.add_argument("--include-archive", action="store_true", help="Also write low-signal Archive items.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    history_notes = find_history_notes(args.paths)
    visits: list[ChromeVisit] = []

    for path in history_notes:
        visits.extend(parse_history_note(path))

    written = write_concept_notes(
        visits,
        dry_run=args.dry_run,
        include_archive=args.include_archive,
    )

    action = "Would write" if args.dry_run else "Wrote"
    print(f"{action} {len(written)} concept note(s) from {len(visits)} history item(s).")
    for path in written:
        print(path.relative_to(VAULT))


if __name__ == "__main__":
    main()
