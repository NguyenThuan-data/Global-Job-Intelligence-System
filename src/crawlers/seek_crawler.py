import urllib.parse
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class SeekNZCrawler(BaseCrawler):
    """
    Crawler for seek.co.nz — the primary NZ job board.
    Pagination: ?page=N (1-indexed, standard page numbers).
    """

    BASE_URL = "https://www.seek.co.nz/jobs"

    def build_url(self, page: int) -> str:
        params = {
            "keywords": self.keywords,
            "where": self.location,
            "page": page,
        }
        return f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

    def parse_jobs(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        # Seek renders job cards with data-automation="jobCard"
        cards = soup.find_all("article", attrs={"data-automation": "normalJob"})
        # Fallback: older Seek layout
        if not cards:
            cards = soup.find_all("article", attrs={"data-card-type": "JobCard"})

        for card in cards:
            title_tag = card.find("a", attrs={"data-automation": "jobTitle"})
            company_tag = card.find("a", attrs={"data-automation": "jobCompany"})
            location_tag = card.find("a", attrs={"data-automation": "jobLocation"})
            desc_tag = card.find("span", attrs={"data-automation": "jobShortDescription"})

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            location = location_tag.get_text(strip=True) if location_tag else self.location
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            href = title_tag.get("href", "")
            link = f"https://www.seek.co.nz{href}" if href.startswith("/") else href

            jobs.append({
                "Position": title,
                "Company": company,
                "Link to Apply": link,
                "JD": description,
                "Key Notice": location,
                "Expiry Date": "",
                "Source": "seek.co.nz",
            })

        return jobs
