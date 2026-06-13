from __future__ import annotations

import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True)
class ChromeVisit:
    title: str
    url: str
    visit_time: datetime
    visit_count: int


def default_chrome_user_data_dir() -> Path:
    return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"


def find_profiles(user_data_dir: Path | None = None) -> list[Path]:
    user_data_dir = user_data_dir or default_chrome_user_data_dir()
    candidates = [user_data_dir / "Default", *sorted(user_data_dir.glob("Profile *"))]
    return [profile for profile in candidates if (profile / "History").exists()]


def chrome_time_to_datetime(value: int) -> datetime:
    return CHROME_EPOCH + timedelta(microseconds=value)


def read_history(
    profile_dir: Path,
    limit: int = 100,
    days: int | None = None,
) -> list[ChromeVisit]:
    history_db = profile_dir / "History"
    if not history_db.exists():
        raise FileNotFoundError(f"Chrome history database not found: {history_db}")

    with tempfile.TemporaryDirectory(prefix="brain_chrome_history_") as tmp_dir:
        tmp_db = Path(tmp_dir) / "History"
        shutil.copy2(history_db, tmp_db)

        where = ""
        params: list[object] = []
        if days is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_chrome_time = int((cutoff - CHROME_EPOCH).total_seconds() * 1_000_000)
            where = "WHERE last_visit_time >= ?"
            params.append(cutoff_chrome_time)

        params.append(limit)
        query = f"""
            SELECT title, url, last_visit_time, visit_count
            FROM urls
            {where}
            ORDER BY last_visit_time DESC
            LIMIT ?
        """

        conn = sqlite3.connect(tmp_db)
        try:
            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()

    visits: list[ChromeVisit] = []
    for title, url, last_visit_time, visit_count in rows:
        if not url:
            continue

        visits.append(
            ChromeVisit(
                title=title or "(untitled)",
                url=url,
                visit_time=chrome_time_to_datetime(int(last_visit_time)).astimezone(),
                visit_count=int(visit_count or 0),
            )
        )

    return visits
