import json
import logging
import sys


class ConfigManager:
    """
    Loads and validates config.json.
    V2 schema: 'jobs' is a list of {site, keywords, location} dicts.
    """

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load()

    def _load(self) -> dict:
        try:
            with open(self.config_path, "r") as f:
                raw = json.load(f)
            logging.info(f"Config loaded from {self.config_path}")
            return raw
        except FileNotFoundError:
            logging.warning(f"Config file not found: {self.config_path}. Using empty defaults.")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config: {e}")
            sys.exit(1)

    def merge_cli_args(self, args):
        """
        Overrides config values with CLI arguments if provided.
        """
        if args.site and args.keywords:
            self.config["jobs"] = [{
                "site": args.site,
                "keywords": args.keywords,
                "location": args.location or "New Zealand"
            }]
        if args.max_pages:
            self.config["max_pages"] = args.max_pages
        if args.email:
            self.config["email"] = args.email

    @property
    def jobs(self) -> list[dict]:
        """
        Returns the list of job search definitions.
        Each entry has: site, keywords, location.
        """
        return self.config.get("jobs", [])

    @property
    def filters(self) -> dict:
        return self.config.get("filters", {})

    @property
    def max_pages(self) -> int:
        return self.config.get("max_pages", 5)

    @property
    def deduplication_enabled(self) -> bool:
        return self.config.get("deduplication", True)

    @property
    def email(self) -> str:
        return self.config.get("email", "")
