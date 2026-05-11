"""
main.py — CLI entry point for the multi-source job scraper.
 
Usage examples:
  python main.py
  python main.py --sources indeed
  python main.py --sources glassdoor
  python main.py --sources indeed glassdoor
  python main.py --location "New York, NY" --format json
  python main.py --include python aws --exclude intern junior
"""

import argparse
from datetime import datetime
from scraper import scrape_all
from sources import SOURCES
from utils import save_to_csv, save_to_json, filter_jobs, print_summary

DEFAULT_QUERIES = [
    "Senior Software Engineer",
    "Backend Engineer",
    "Senior Backend Developer",
    "Software Engineer"
]

DEFAULT_LOCATION = "Remote"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape job listings from Indeed and LinkedIn. Export to CSV or JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python main.py
  python main.py --sources indeed
  python main.py --sources glassdoor
  python main.py --sources indeed glassdoor --location "Toronto, ON"
  python main.py --include python fastapi --exclude intern junior
  python main.py --format json --output my_jobs.json
        """,
    )
    parser.add_argument(
        "--sources", "-s",
        nargs="+",
        choices=list(SOURCES.keys()),
        default=list(SOURCES.keys()),
        metavar="SOURCE",
        help=f"Sources to scrape. Options: {', '.join(SOURCES.keys())} (default: all)",
    )
    parser.add_argument(
        "--location", "-l",
        default=DEFAULT_LOCATION,
        help=f'Job location or "Remote" (default: "{DEFAULT_LOCATION}")',
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output filename (default: jobs_YYYYMMDD.csv or .json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "json"],
        default="csv",
        help="Output format: csv or json (default: csv)",
    )
    parser.add_argument(
        "--include", "-i",
        nargs="+",
        metavar="KEYWORD",
        help="Only keep listings containing at least one of these keywords",
    )
    parser.add_argument(
        "--exclude", "-e",
        nargs="+",
        metavar="KEYWORD",
        help="Drop listings containing any of these keywords",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Max results per query per source (max 25, default: 25)",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=5,
        metavar="N",
        help="Listings to preview in the terminal (default: 5)",
    )
 
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    datestamp = datetime.now().strftime("%Y%m%d")
    output_path = args.output or f"jobs_{datestamp}.{args.format}"
    sources_str = ", ".join(s.capitalize() for s in args.sources)

    print("\n Job Scraper - Senior Software / Backend Engineer Roles")
    print(f" Sources    : {sources_str}")
    print(f" Location   : {args.location}")
    print(f" Queries    : {', '.join(DEFAULT_QUERIES)}")
    print(f" Output     : {output_path}")

    jobs = scrape_all(
        queries = DEFAULT_QUERIES,
        location=args.location,
        max_per_query=args.limit,
        delay=2.0,
        sources=args.sources,
    )

    if not jobs:
        print("\n[main] No jobs found. Try a different location or check your connection.")
        return
    
    if args.include or args.exclude:
        before = len(jobs)
        jobs = filter_jobs(jobs, keywords=args.include, exclude_keywords=args.exclude)
        print(f"[main] Filtered: {before} -> {len(jobs)} listings")

    print_summary(jobs, limit=args.preview)

    if args.format == "json":
        save_to_json(jobs, output_path)
    else:
        save_to_csv(jobs, output_path)

    print(f"\n Done! Open '{output_path}' to see all results. \n")

    if __name__ == "__main__":
        main()