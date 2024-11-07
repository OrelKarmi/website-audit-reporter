from urllib.parse import urlparse, urlunparse
import re

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        fragment='',
        query=''
    )
    path = normalized.path[:-1] if normalized.path.endswith('/') else normalized.path
    return urlunparse(normalized._replace(path=path))

def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and not re.search(r'<%|%>', url)

def is_same_domain(url1: str, url2: str) -> bool:
    return urlparse(url1).netloc.lower() == urlparse(url2).netloc.lower()
