import logging
import time
import requests
from abc import ABC, abstractmethod

class BaseCrawler(ABC):
    """
    Abstract base class for all site-specific job crawlers.
    Each crawler plugin must implement build_url() and parse_jobs().
    The crawl_all_pages() orchestration is handled here automatically.
    """

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, keywords: str, location: str):
        self.keywords = keywords
        self.location = location
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    @abstractmethod
    def build_url(self, page: int) -> str:
        """Build the paginated search URL for a given page number (1-indexed)."""
        ...

    @abstractmethod
    def parse_jobs(self, html: str) -> list[dict]:
        """
        Extract job listings from the raw HTML of one page.
        Returns a list of job dicts with keys:
        Position, Company, Link to Apply, JD, Key Notice, Expiry Date, Source
        """
        ...

    def fetch_page(self, url: str) -> str | None:
        """Fetch the raw HTML for a URL with error handling."""
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            logging.info(f"  ✓ Fetched: {url} [{resp.status_code}]")
            return resp.text
        except requests.exceptions.HTTPError as e:
            logging.warning(f"  HTTP error fetching {url}: {e}")
        except requests.exceptions.ConnectionError:
            logging.warning(f"  Connection error fetching {url}")
        except requests.exceptions.Timeout:
            logging.warning(f"  Timeout fetching {url}")
        return None

    def is_empty_page(self, jobs: list) -> bool:
        """Returns True if no jobs were found on a page (stop condition)."""
        return len(jobs) == 0

    def crawl_all_pages(self, max_pages: int = 5) -> list[dict]:
        """
        Automatically crawl all pages up to max_pages.
        Stops early if a page returns no jobs (end of results).
        """
        all_jobs = []
        source_name = self.__class__.__name__.replace("Crawler", "")

        for page in range(1, max_pages + 1):
            url = self.build_url(page)
            logging.info(f"[{source_name}] Crawling page {page}/{max_pages}: {url}")

            html = self.fetch_page(url)
            if not html:
                logging.warning(f"[{source_name}] Page {page} returned no content. Stopping.")
                break

            jobs = self.parse_jobs(html)

            if self.is_empty_page(jobs):
                logging.info(f"[{source_name}] No jobs on page {page}. End of results.")
                break

            logging.info(f"[{source_name}] Found {len(jobs)} jobs on page {page}.")
            all_jobs.extend(jobs)
            time.sleep(1.5)  # Polite delay between pages

        logging.info(f"[{source_name}] Total collected: {len(all_jobs)} jobs.")
        return all_jobs
