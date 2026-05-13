# sources/__init__.py
# Each source module must expose a single function:
#    scrape(queries, location, max_per_query, delay) -> list[dict]

from sources.remoteok import scrape as scrape_remoteok
from sources.glassdoor import scrape as scrape_glassdoor

SOURCES = {
    "remoteok": scrape_remoteok,
    "glassdoor": scrape_glassdoor,
}