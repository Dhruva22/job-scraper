# sources/__init__.py
# Each source module must expose a single function:
#    scrape(queries, location, max_per_query, delay) -> list[dict]

from sources.indeed import scrape as scrape_indeed
from sources.glassdoor import scrape as scrape_glassdoor

SOURCES = {
    "indeed": scrape_indeed,
    "glassdoor": scrape_glassdoor,
}