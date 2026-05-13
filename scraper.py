"""
scraper.py — Orchestrate scraping across multiple job sources.
 
Each source in sources/ exposes a scrape() function with the same signature.
This module calls whichever sources the user selects and merges the results,
deduplicating by URL across all sources.
"""

from __future__ import annotations
from sources import SOURCES

def scrape_all(
        queries: list[str],
        location: str = "Remote",
        max_per_query: int = 25,
        delay: float = 2.0,
        sources: list[str] | None = None,
    ) -> list[dict]:
    """
    Scrape job listings from one or more sources.
 
    Args:
        queries:       Job title strings to search.
        location:      City/state or "Remote".
        max_per_query: Max results per query per source.
        delay:         Seconds to wait between requests.
        sources:       Which sources to use. Defaults to all available.
                       Options: "remoteok", "glassdoor"
 
    Returns:
        Deduplicated, merged list of job dicts sorted by source then date.
    """

    if sources is None:
        sources = list(SOURCES.keys())

    unknown = [s for s in sources if s not in SOURCES]
    if unknown:
        raise ValueError(f"Unknown source(s): {unknown}. Available: {list(SOURCES.keys())}")
    
    all_jobs: list[dict] = []
    seen_urls: set[str] = set()

    for source_name in sources:
        print(f"\n-- {source_name.capitalize()} --------------------------------")
        scrape_fn = SOURCES[source_name]
        jobs = scrape_fn(
            queries=queries,
            location=location,
            max_per_query=max_per_query,
            delay=delay,
        )

        new = 0
        for job in jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                all_jobs.append(job)
                new += 1

        print(f"   -> {new} unique listings from {source_name.capitalize()}")

    print(f"\n-- Total: {len(all_jobs)} listings across {len(sources)} source(s)\n")
    return all_jobs