from .models import CrawlerConfig
from .crawler import URLCrawler
import asyncio
from typing import List

def fetch_urls(url: str) -> List[str]:
    config = CrawlerConfig()
    crawler = URLCrawler(config)
    return asyncio.run(crawler.crawl(url))
