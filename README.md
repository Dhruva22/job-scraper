# 🤖 Job Listings Scraper

A Python CLI tool that searches for **Senior Software Engineer** and **Backend Engineer** roles across **Indeed** and **Glassdoor** simultaneously — no API key or login required. Results export to CSV or JSON.

## Features

- 🌐 Scrapes **Indeed** and **Glassdoor** in one run (or pick just one)
- 🔍 Searches multiple job titles per source
- 📍 Filter by location or target Remote roles
- 🧹 Keyword include/exclude filtering
- 💾 Export to CSV or JSON
- 🖨 Terminal preview of top results
- ⏱ Polite request delays between calls

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/Dhruva22/job-scraper.git
cd job-scraper

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run it
python3 main.py
```

## Usage

```bash
# Scrape both RemoteOk and Glassdoor (default)
python3 main.py

# Only Indeed
python3 main.py --sources remoteok

# Only Glassdoor
python3 main.py --sources glassdoor

# Both, specific city
python3 main.py --sources remoteok glassdoor --location "Toronto, ON"

# Filter: must mention python or fastapi, exclude intern/junior
python3 main.py --include python fastapi --exclude intern junior "entry level"

# Export as JSON
python3 main.py --format json --output backend_jobs.json
```

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--sources` | `-s` | all | Sources: `indeed`, `glassdoor` (space-separated) |
| `--location` | `-l` | `Remote` | Job location to search |
| `--output` | `-o` | auto | Output filename |
| `--format` | `-f` | `csv` | Output format: `csv` or `json` |
| `--include` | `-i` | none | Keep only listings with these keywords |
| `--exclude` | `-e` | none | Drop listings with these keywords |
| `--limit` | | `25` | Max results per query per source |
| `--preview` | | `5` | Listings to print in terminal |

## Output columns

| Column | Description |
|--------|-------------|
| `title` | Job title |
| `company` | Company name |
| `location` | Job location |
| `date_posted` | When posted |
| `description_snippet` | First 300 chars of description |
| `url` | Direct link to the listing |
| `source` | Where it came from (Indeed / Glassdoor) |
| `scraped_at` | Timestamp of when it was scraped |

## Project structure

```
job-scraper/
├── main.py              # CLI entry point
├── scraper.py           # Multi-source orchestrator
├── utils.py             # Filter, save, display
├── sources/
│   ├── __init__.py      # Source registry
│   ├── base.py          # Shared HTTP helpers + job schema
│   ├── remoteok.py        # Indeed RSS scraper
│   └── glassdoor.py     # Glassdoor RSS scraper
├── requirements.txt
├── .gitignore
└── README.md
```

## How it works

Both RemoteOk and Glassdoor expose **public RSS feeds** for job searches — no scraping of HTML, no headless browser, no API key. This tool builds the right RSS URL per source, fetches the XML, parses it with Python's built-in `xml.etree.ElementTree`, deduplicates across sources by URL, and writes clean structured data to disk.

Adding a new source is one file in `sources/` plus one line in `sources/__init__.py`.

## Tech stack

- `requests` — HTTP
- `xml.etree.ElementTree` — XML parsing (stdlib)
- `csv`, `json`, `argparse`, `pathlib`, `re` — all stdlib

## License

MIT
