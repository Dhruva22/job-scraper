"""
sources/glassdoor.py — Scrape job listings from Glassdoor's public RSS feed.
 
Glassdoor exposes RSS at https://www.glassdoor.com/feeds/job-feed.htm
No API key or login required.

Note: Glassdoor's RSS is less structured than Indeed's - company and 
location are often embedded in the description rather tahn separate fields,
so we extract what we can and fall back to "N/A" gracefully.
"""

import time
import re
import xml.etree.ElementTree as ET
import requests
from sources.base import fetch, strip_html, make_job

SOURCE_NAME = "Glassdoor"


def _build_url(query: str, location: str, limit: int) -> str:
    q = requests.utils.quote(query)
    l = requests.utils.quote(location)
    return (
        f"https://www.glassdoor.com/feeds/job-feed.htm"
        f"?jobType=all&locT=C&locId=1&jobId=&q={q}&city={l}"
        f"&state=&country=US&limit={limit}&fromAge=7"
    )

def _extract_company_location(title: str, description: str) -> tuple[str, str]:
    """
    Glassdoor title format varies. Common patterns:
       "Senior Engineer at Acme Corp in San Francisco, CA"
       "Senior Engineer - Acme Corp - Remote"
    Falls back to scanning the description snippet.
    """
    # Pattern: "... at Company in Location"
    m = re.search(r" at (.+?) in (.+?)(?:\.|$)", title)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    
    #Pattern: "Title - Company -Location"
    parts = [p.strip() for p in title.split(" - ")]
    if len(parts) >= 3:
        return parts[1], parts[2]
    
    if len(parts) == 2:
        return parts[1], "N/A"
    
    return "N/A", "N/A"

def _parse(xml_text: str) -> list[dict]:
    jobs = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"       [glassdoor] XML parse error: {e}")
        return jobs
    
    channel = root.find("channel")

    if channel is None:
        return jobs
    

    for item in channel.findall("item"):
        raw_title = item.findtext("title", "").strip()
        link      = item.findtext("link", "").strip()
        desc_raw  = item.findtext("description", "")
        pub_date  = item.findtext("pubDate", "").strip()

        snippet           = strip_html(desc_raw)
        company, location = _extract_company_location(raw_title, snippet)

        # Clean job title - strip everything after " at " if present
        title = re.split(r" at | - ", raw_title)[0].strip()

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
            print(f"   [Glassdoor] '{query}' in '{location}' ...")
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
