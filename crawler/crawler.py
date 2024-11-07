import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import List, Set
import time
from aiohttp import ClientTimeout
from functools import lru_cache

from .models import CrawlerConfig
from .utils import normalize_url, is_valid_url, is_same_domain

class URLCrawler:
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.visited: Set[str] = set()
        self.filtered_links: Set[str] = set()
        self.last_request_time: float = 0
        self.semaphore = asyncio.Semaphore(config.max_concurrent)

    @lru_cache(maxsize=100)
    def normalize_url(self, url: str) -> str:
        return normalize_url(url)

    async def fetch_page(self, url: str, session: aiohttp.ClientSession) -> List[str]:
        async with self.semaphore:
            current_time = time.time()
            sleep_time = self.config.rate_limit - (current_time - self.last_request_time)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            
            self.last_request_time = time.time()
            
            try:
                async with session.get(url, timeout=ClientTimeout(total=self.config.timeout)) as response:
                    if response.status != 200:
                        return []
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    return [link.get('href') for link in soup.find_all('a') if link.get('href')]
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return []

    async def crawl_url(self, url: str, depth: int, session: aiohttp.ClientSession, base_url: str) -> None:
        if (depth > self.config.max_depth or 
            url in self.visited or 
            len(self.filtered_links) >= self.config.max_urls):
            return

        self.visited.add(url)
        links = await self.fetch_page(url, session)
        tasks = []

        for link in links:
            if len(self.filtered_links) >= self.config.max_urls:
                break

            full_link = (link if link.startswith("https") else
                        f"{urlparse(url).scheme}:{link}" if link.startswith("//") else
                        urljoin(url, link))
            
            full_link = self.normalize_url(full_link)
            
            if (is_valid_url(full_link) and 
                is_same_domain(base_url, full_link) and 
                full_link not in self.visited):
                self.filtered_links.add(full_link)
                tasks.append(self.crawl_url(full_link, depth + 1, session, base_url))

        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self, start_url: str) -> List[str]:
        self.visited.clear()
        self.filtered_links = {self.normalize_url(start_url)}
        
        async with aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'en-US,en;q=0.5',
        }) as session:
            await self.crawl_url(start_url, 0, session, start_url)
        
        return sorted(list(self.filtered_links))[:self.config.max_urls]
