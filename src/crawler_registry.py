import logging
from .crawlers.seek_crawler import SeekNZCrawler
from .crawlers.linkedin_crawler import LinkedInNZCrawler
from .crawlers.trademe_crawler import TradeMeCrawler

# Registry maps config "site" string to the corresponding crawler class.
# To add a new site: create a new plugin in src/crawlers/ and add it here.
CRAWLER_REGISTRY = {
    "seek": SeekNZCrawler,
    "linkedin": LinkedInNZCrawler,
    "trademe": TradeMeCrawler,
}


class CrawlerRegistry:
    """
    Resolves a job definition from config to the correct crawler plugin,
    instantiates it, and drives the pagination loop.
    """

    def get_crawler(self, job_def: dict):
        """
        Looks up the crawler class by site name and returns an instance.
        Raises ValueError for unknown site names with a helpful message.
        """
        site = job_def.get("site", "").lower().strip()
        keywords = job_def.get("keywords", "")
        location = job_def.get("location", "New Zealand")

        crawler_class = CRAWLER_REGISTRY.get(site)

        if crawler_class is None:
            supported = ", ".join(CRAWLER_REGISTRY.keys())
            raise ValueError(
                f"Unknown site '{site}'. Supported sites: {supported}. "
                f"To add a new site, create a plugin in src/crawlers/ and register it in crawler_registry.py."
            )

        logging.info(f"Resolved site '{site}' → {crawler_class.__name__}(keywords='{keywords}', location='{location}')")
        return crawler_class(keywords=keywords, location=location)
