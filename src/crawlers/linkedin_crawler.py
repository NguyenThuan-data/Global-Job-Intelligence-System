import urllib.parse
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class LinkedInNZCrawler(BaseCrawler):
    """
    Crawler for LinkedIn Jobs using the public guest API endpoint.
    No login required. Location is locked to New Zealand.
    Pagination: &start=0, 25, 50... (increments of 25 per page).
    """

    # LinkedIn's public guest job search API (no auth token needed)
    API_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def __init__(self, keywords: str, location: str):
        super().__init__(keywords, location)
        # LinkedIn guest API requires different headers
        self.session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.linkedin.com/jobs/",
        })

    def build_url(self, page: int) -> str:
        # LinkedIn uses start index (0-based, 25 per page)
        start = (page - 1) * 25
        params = {
            "keywords": self.keywords,
            "location": "New Zealand",  # Always NZ
            "start": start,
            "count": 25,
        }
        return f"{self.API_URL}?{urllib.parse.urlencode(params)}"

    def parse_jobs(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []

        # LinkedIn guest API returns <li> elements with job cards
        cards = soup.find_all("li")

        for card in cards:
            title_tag = card.find("h3", class_="base-search-card__title")
            company_tag = card.find("h4", class_="base-search-card__subtitle")
            location_tag = card.find("span", class_="job-search-card__location")
            link_tag = card.find("a", class_="base-card__full-link")
            date_tag = card.find("time")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"
            location = location_tag.get_text(strip=True) if location_tag else "New Zealand"
            link = link_tag.get("href", "").split("?")[0]  # Strip tracking params
            posted_date = date_tag.get("datetime", "") if date_tag else ""

            jobs.append({
                "Position": title,
                "Company": company,
                "Link to Apply": link,
                "JD": f"Location: {location}",
                "Key Notice": f"Posted: {posted_date}",
                "Expiry Date": "",
                "Source": "linkedin.com/jobs",
            })

        return jobs
