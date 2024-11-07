from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    max_depth: int = 2
    max_urls: int = 10
    rate_limit: float = 0.5  # seconds between requests
    timeout: int = 10
    max_concurrent: int = 5
