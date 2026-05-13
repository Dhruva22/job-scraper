"""
utils.py -- Save, filter, and display scraped job listings.
"""

from __future__ import annotations
import csv
import json
from pathlib import Path
from datetime import datetime

def save_to_csv(jobs: list[dict], filepath: str = "jobs.csv") -> Path:
    """Write job listings to a CSV file."""
    path = Path(filepath)
 
    if not jobs:
        print("[utils] No jobs to save.")
        return path
 
    fieldnames = list(jobs[0].keys())
 
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)
 
    print(f"[utils] Saved {len(jobs)} jobs → {path.resolve()}")
    return path

def save_to_json(jobs: list[dict], filepath: str = "jobs.json") -> Path:
    """Write job listings to a JSON file"""
 
    path = Path(filepath)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"[utils] Saved {len(jobs)} jobs -> {path.resolve()}")
    return path

def filter_jobs(
        jobs: list[dict],
        keywords: list[str] | None = None,
        exclude_keywords: list[str] | None = None,
) -> list[dict]:
    """
    
    Filter jobs by keywords found anywhere in title or description

    Args:
        jobs:             Full list of jobs dicts.
        keywords:         Keep only jobs containing at least one of these.
        exclude_keywords: Drop jobs containing any of these.

    Returns:
        Filtered list.

    """
    filtered = jobs
    if keywords:
        kw_lower = [k.lower() for k in keywords]
        filtered = [
            j for j in filtered
            if any(k in (j["title"] + " " + j["description_snippet"]).lower() for k in kw_lower)
        ]

    if exclude_keywords:
        ex_lower = [k.lower() for k in exclude_keywords]
        filtered = [
            j for j in filtered
            if not any(k in (k["title"] + " " + j["description_snippet"]).lower() for k in ex_lower)
        ]

    return filtered

def print_summary(jobs: list[dict], limit: int = 10) -> None:
    """Print a formatted summary of job listings to the terminal."""
    if not jobs:
        print("No jobs found.")
        return
    
    print(f"\n{'─' * 70}")
    print(f"  Found {len(jobs)} job listing(s)")
    print(f"{'─' * 70}")
 
    for i, job in enumerate(jobs[:limit], start=1):
        print(f"\n  [{i}] {job['title']}")
        print(f"      Company  : {job['company']}")
        print(f"      Location : {job['location']}")
        print(f"      Posted   : {job['date_posted']}")
        print(f"      URL      : {job['url']}")
        if job.get("description_snippet"):
            snippet = job["description_snippet"][:120].rstrip() + "..."
            print(f"      Snippet  : {snippet}")
 
    if len(jobs) > limit:
        print(f"\n  ... and {len(jobs) - limit} more. See the CSV for full results.")
 
    print(f"\n{'─' * 70}\n")