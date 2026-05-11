"""
sources/base.py — Shared utilities for all scraper sources.
 
Every source module returns a list of dicts with these keys:
  title, company, location, date_posted,
  description_snippet, url, source, scraped_at
"""

import re
import requests
from datetime import datetime


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US;en;q=0.5"
}

def fetch(url: str, timeout: int = 10) -> str | None:
    """ Get a URL and return the response text, or None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"     [error] {e}")
        return None
    

def strip_html(raw: str,max_len: int = 300) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def make_job(
        *,
        title: str,
        company: str,
        location: str,
        date_posted: str,
        description_snippet: str,
        url: str,
        source: str,
) -> dict:
    """Return a job dict with a consistent schema across all sources."""
    return {
        "title": title,
        "company": company,
        "location": location,
        "date_posted": date_posted,
        "description_snippet": description_snippet,
        "url": url,
        "source": source,
        "scrapped_at": now_iso(),
    }
