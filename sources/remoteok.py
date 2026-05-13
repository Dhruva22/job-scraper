"""
sources/remoteok.py — Scrape job listings from RemoteOK's free public API.

RemoteOK exposes a JSON API at https://remoteok.com/api with no auth required.
Returns up to ~150 recent remote jobs. We filter by keyword client-side.
"""

from __future__ import annotations
import time
import requests
from sources.base import strip_html, make_job

SOURCE_NAME = "RemoteOK"

API_URL = "https://remoteok.com/api"

HEADERS = {
    "User-Agent": "job-scraper-portfolio-project/1.0",
    "Accept": "application/json",
}


def _fetch_all() -> list[dict]:
    """Fetch the full RemoteOK feed (first item is a legal notice, skip it)."""
    try:
        r = requests.get(API_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data[1:] if data else []   # skip the legal notice at index 0
    except Exception as e:
        print(f"    [error] RemoteOK fetch failed: {e}")
        return []


def _matches(job: dict, queries: list[str]) -> bool:
    """Return True if any query keyword appears in the job title or tags."""
    haystack = (
        job.get("position", "") + " " +
        " ".join(job.get("tags", []))
    ).lower()
    return any(q.lower() in haystack for q in queries)


def scrape(
    queries: list[str],
    location: str = "Remote",       # RemoteOK is always remote; param kept for API compat
    max_per_query: int = 25,
    delay: float = 2.0,
) -> list[dict]:
    print(f"  [RemoteOK] Fetching full feed and filtering for: {queries} ...")
    time.sleep(delay)   # be polite — one request for the whole feed

    raw_jobs = _fetch_all()
    if not raw_jobs:
        print("  [RemoteOK] No data returned.")
        return []

    matched: list[dict] = []
    seen: set[str] = set()

    for raw in raw_jobs:
        if not _matches(raw, queries):
            continue

        url = raw.get("url", "") or f"https://remoteok.com/remote-jobs/{raw.get('id', '')}"
        if url in seen:
            continue
        seen.add(url)

        tags = ", ".join(raw.get("tags", []))
        description = strip_html(raw.get("description", "") or tags)

        matched.append(make_job(
            title=raw.get("position", "N/A"),
            company=raw.get("company", "N/A"),
            location="Remote",
            date_posted=raw.get("date", "N/A"),
            description_snippet=description or tags,
            url=url,
            source=SOURCE_NAME,
        ))

        if len(matched) >= max_per_query:
            break

    print(f"  [RemoteOK] → {len(matched)} matching listings")
    return matched