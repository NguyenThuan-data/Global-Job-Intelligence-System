import urllib.parse
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class TradeMeCrawler(BaseCrawler):
    """
    Crawler for TradeMe Jobs NZ — trademe.co.nz/a/jobs.
    Pagination: &page=N (1-indexed, standard page numbers).
    """

    BASE_URL = "https://www.trademe.co.nz/a/jobs/search"

    def build_url(self, page: int) -> str:
        params = {
            "search_string": self.keywords,
            "region": self.location,
            "page": page,
        }
        return f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

    def parse_jobs(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        # TradeMe job cards use tm-jobs-search-card components (Angular)
        # Fallback: look for structured-data JSON-LD blocks
        cards = soup.find_all("tm-jobs-search-card")

        # Fallback: some TradeMe pages render partial HTML with standard divs
        if not cards:
            cards = soup.find_all("div", class_=lambda c: c and "job" in c.lower() and "card" in c.lower())

        for card in cards:
            title_tag = card.find(["h2", "h3", "a"])
            link_tag = card.find("a", href=True)
            company_tag = card.find(["span", "div"], string=lambda s: s and len(s) < 60)

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            href = link_tag.get("href", "") if link_tag else ""
            link = f"https://www.trademe.co.nz{href}" if href.startswith("/") else href
            company = company_tag.get_text(strip=True) if company_tag and company_tag.get_text(strip=True) != title else "Unknown"

            if not title or len(title) < 3:
                continue

            jobs.append({
                "Position": title,
                "Company": company,
                "Link to Apply": link,
                "JD": "",
                "Key Notice": self.location,
                "Expiry Date": "",
                "Source": "trademe.co.nz/jobs",
            })

        return jobs
