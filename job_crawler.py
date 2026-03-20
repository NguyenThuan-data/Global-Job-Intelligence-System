import logging
import argparse
from src.config import ConfigManager
from src.crawler_registry import CrawlerRegistry
from src.filter_engine import FilterEngine
from src.deduplicator import JobDeduplicator
from src.exporter import ExcelExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    # --- Parse CLI Arguments ---
    parser = argparse.ArgumentParser(description="NZ Job Intelligence System Crawler")
    parser.add_argument("--site", help="Specific site to crawl (seek, linkedin, trademe)")
    parser.add_argument("--keywords", help="Job titles or keywords to search for")
    parser.add_argument("--location", help="Location (e.g. Auckland, Wellington)")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages per site")
    parser.add_argument("--email", help="Recipient email for the report")
    args = parser.parse_args()

    # --- Load configuration ---
    config = ConfigManager()
    config.merge_cli_args(args)

    if not config.jobs:
        logging.error("No job search definitions found in config.json. Exiting.")
        return

    logging.info(f"Loaded {len(config.jobs)} job search(es), max {config.max_pages} pages each.")

    # --- Crawl all sites ---
    registry = CrawlerRegistry()
    all_jobs = []

    for job_def in config.jobs:
        try:
            crawler = registry.get_crawler(job_def)
            jobs = crawler.crawl_all_pages(max_pages=config.max_pages)
            all_jobs.extend(jobs)
        except ValueError as e:
            logging.warning(f"Skipping job definition: {e}")

    logging.info(f"Total raw jobs collected: {len(all_jobs)}")

    # --- Filter ---
    filter_engine = FilterEngine(config.filters)
    filtered_jobs = filter_engine.classify_and_filter(all_jobs)
    logging.info(f"After filtering: {len(filtered_jobs)} jobs")

    # --- Deduplicate ---
    deduplicator = JobDeduplicator(config.deduplication_enabled)
    unique_jobs = deduplicator.deduplicate(filtered_jobs)

    # --- Export ---
    ExcelExporter.export(unique_jobs)
    logging.info("Done. ✓")


if __name__ == "__main__":
    main()
