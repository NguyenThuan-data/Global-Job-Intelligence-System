import logging
import urllib.parse
import requests
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def extract_jobs(self, html, url):
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        domain = urllib.parse.urlparse(url).netloc
        
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link.get('href', '')
            
            if len(text.split()) > 1 and len(text) > 8 and len(text) < 100:
                job_keywords = ["engineer", "developer", "analyst", "manager", "specialist", "coordinator", "assistant", "director"]
                if any(k in text.lower() for k in job_keywords) or "/job" in href.lower() or "role" in href.lower():
                    company = self._extract_company(link, text)
                    if href.startswith('http'):
                        full_link = href
                    else:
                        full_link = urllib.parse.urljoin(url, href)
                    
                    jobs.append({
                        "Position": text,
                        "Company": company,
                        "Link to Apply": full_link,
                        "JD": "Description extracted from listing... (Click link to apply)",
                        "Key Notice": "",
                        "Expiry Date": "",
                        "Source": domain
                    })
                    
        return self._deduplicate_local(jobs)

    def _extract_company(self, link_node, link_text):
        parent = link_node.find_parent('div')
        if parent:
            spans = parent.find_all('span')
            for span in spans:
                span_text = span.get_text(strip=True)
                if span_text and span_text != link_text and len(span_text) < 50:
                    return span_text
        return "Unknown"

    def _deduplicate_local(self, jobs):
        unique_jobs = {j["Link to Apply"]: j for j in jobs}
        return list(unique_jobs.values())
