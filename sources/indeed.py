"""
sources/indeed.py — Scrape job listings from Indeed's public RSS feed.
 
Indeed exposes RSS at https://www.indeed.com/rss with no auth required.
Feed caps at 25 results per request; we search once per query string.
"""

import time
import xml.etree.ElementTree as ET
import requests
from sources.base import fetch, strip_html, make_job

SOURCE_NAME = "Indeed"


def _build_url(query: str, location: str, limit: int) -> str:
    q = requests.utils.quote(query)
    l = requests.utils.quote(location)
    return f"https://www.indeed.com/rss?q={q}&l={l}&limit={limit}&sort=date"

def _parse(xml_text: str) -> list[dict]:
    jobs = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"       [indeed] XML parse error: {e}")
        return jobs
    
    channel = root.find("channel")

    if channel is None:
        return jobs
    

    for item in channel.findall("item"):
        raw_title = item.findtext("title", "").strip()
        link      = item.findtext("link", "").strip()
        desc_raw  = item.findtext("description", "")
        pub_date  = item.findtext("pubDate", "").strip()

        # Indeed title format: "Job Title - Company - City, State"
        parts = [p.strip() for p in raw_title.split(" - ")]
        title = parts[0] if parts else raw_title
        company = parts[1] if len(parts) > 1 else "N/A"
        location = parts[2] if len(parts) > 2 else "N/A"

        jobs.append(make_job(
            title=title,
            company=company,
            location=location,
            date_posted=pub_date,
            description_snippet=strip_html(desc_raw),
            url=link,
            source=SOURCE_NAME,
        ))

        return jobs
    
    def scrape(
            queries: list[str],
            location: str = "Remote",
            max_per_query: int = 25,
            delay: float = 2.0,
    ) -> list[dict]:
        all_jobs: list[dict] = []
        seen: set[str] = set()

        for query in queries:
            print(f"   [Indeed] '{query}' in '{location}' ...")
            url = _build_url(query, location, min(max_per_query, 25))
            text = fetch(url)

            if text:
                for job in _parse(text):
                    if job["url"] not in seen:
                        seen.add(job["url"])
                        all_jobs.append(job)


            print(f"               -> {len(all_jobs)} unique listings so far")
            time.sleep(delay)

        return all_jobs
