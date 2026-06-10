<div align="center">

# Global Job Intelligence System

### Automated NZ Job Market Crawler · Multi-Site · Auto-Paginated · Excel Delivered

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![n8n](https://img.shields.io/badge/n8n-Orchestrated-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Scraping-59666C?style=for-the-badge)](https://pypi.org/project/beautifulsoup4/)
[![pandas](https://img.shields.io/badge/pandas-Export-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)

**You set the keywords. The system finds the jobs.**

</div>

---

## Why this project

- **Automated Efficiency**: Manually searching through Seek, LinkedIn, and TradeMe daily is time-consuming. This system automates the heavy lifting.
- **Cross-Site Intelligence**: Jobs are often cross-posted. The fuzzy deduplication ensures you only see unique opportunities, saving review time.
- **Structured Data**: Instead of browser tabs, you get a clean, sortable Excel report with all key details in one place.
- **Extensible Architecture**: The plugin-based design means new job boards can be added with minimal effort.

---

## What It Does

| Step | Action |
|------|--------|
| 1 | You edit `config.json`: set site, keywords, and location |
| 2 | Run `python job_crawler.py` — or trigger via n8n webhook |
| 3 | Crawler hits **Seek NZ, LinkedIn NZ, and TradeMe** — up to **5 pages each** |
| 4 | Fuzzy deduplication removes cross-site duplicates |
| 5 | A structured Excel report lands in your folder (and email via n8n) |

---

## Sample Output

Running locally produces `job_report_YYYYMMDD_HHMMSS.xlsx` with columns like:

| Column | Description |
|--------|-------------|
| Position | Job title |
| Level | Inferred seniority |
| Company | Employer name |
| Link | Source URL |
| JD | Job description excerpt |
| Key Notice | Salary / visa / highlights |
| Expiry | Closing date if available |
| Source | seek / linkedin / trademe |
| Status | Filter classification |

**Try it yourself (Seek, 1 page):**

```bash
pip install -r requirements.txt
python job_crawler.py --site seek --keywords "data analyst" --location Auckland --max-pages 1
```

> Job boards change HTML frequently — if a crawler returns zero rows, check logs and update the site-specific plugin in `src/crawlers/`.

---

## Architecture

```
config.json             ← You configure: site + keywords + location
    │
    ▼
job_crawler.py          ← Entry point & orchestrator
    │
    ├── ConfigManager   ← Reads config + CLI overrides
    ├── CrawlerRegistry ← Routes site name → correct plugin
    │       ├── SeekNZCrawler       (seek.co.nz)
    │       ├── LinkedInNZCrawler   (LinkedIn guest API)
    │       └── TradeMeCrawler      (trademe.co.nz/jobs)
    │            └── BaseCrawler    ← Auto-paginates all sites
    ├── FilterEngine    ← Level, type, keyword filtering
    ├── JobDeduplicator ← Fuzzy-match cross-site dedup
    └── ExcelExporter   ← Outputs .xlsx report
```

> **Plugin Design**: Adding a new job board = 1 new file in `src/crawlers/`. Zero changes to the rest of the system.

---

## Key Features

- **Auto-Pagination** — crawls up to N pages per site automatically; stops when results end
- **Smart Deduplication** — fuzzy-match (≥85% similarity) removes the same job listed on 2+ boards
- **Plugin Architecture** — each site is an isolated class inheriting from `BaseCrawler`
- **Fully Config-Driven** — `{"site": "seek", "keywords": "data analyst", "location": "Auckland"}`
- **n8n Webhook Control** — trigger a custom search in real-time via a URL call

---

## Quick Start

```bash
pip install -r requirements.txt
python job_crawler.py
# Or override on the fly:
python job_crawler.py --site seek --keywords "data engineer" --location Wellington
```

---

## n8n Orchestration

Import `workflow.json` into n8n, then trigger via:

```
GET /webhook/trigger-crawler?site=seek&keywords=data+analyst&location=Auckland
```

n8n handles: **schedule → crawl → email report**. No manual steps required.

---

## Lessons Learned

- Job boards use **3 different pagination styles** (URL param, infinite scroll, API offset) — built site-specific strategies for each
- Generic scrapers break on every site update; **plugin isolation** means only the affected class needs to be fixed
- Cross-site deduplication requires fuzzy matching (not exact) since the same job often has slightly different titles on different boards

---

## Honest Notes

- This is a **working prototype**, not a guaranteed production scraper — site changes can break individual plugins.
- Respect each job board's terms of service; use for personal job search / portfolio demonstration.
