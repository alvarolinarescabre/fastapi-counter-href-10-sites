import re
import random
import asyncio
from typing import Optional
from aiohttp import ClientSession, ClientTimeout, ClientError, TCPConnector
from aiohttp_client_cache.session import CachedSession
from aiohttp_client_cache import SQLiteBackend
from conf.settings import get_settings

settings = get_settings()

# Constants (keeping pattern_compiled for backward compatibility)
pattern_compiled = re.compile(r'<a\s+[^>]*href\s*=\s*["\'](?:http|https)://[^"\']*["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
TIMEOUT = ClientTimeout(total=settings.timeout)
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; FastAPICounter/1.0)', 'Accept': 'text/html,application/xhtml+xml'}

_session: Optional[ClientSession] = None
_session_lock = asyncio.Lock()

async def get_session() -> ClientSession:
    """Returns a singleton session with HTTP caching enabled"""
    global _session
    async with _session_lock:
        if _session is None or _session.closed:
            connector = TCPConnector(limit=200, ttl_dns_cache=600, ssl=False, use_dns_cache=True)
            
            if settings.cache_backend == "sqlite":
                cache = SQLiteBackend(cache_name=settings.cache_db_path, expire_after=settings.cache_expire)
                _session = CachedSession(cache=cache, timeout=TIMEOUT, headers=HEADERS, connector=connector)
            else:
                _session = ClientSession(timeout=TIMEOUT, headers=HEADERS, connector=connector)
        return _session

async def fetch(session: ClientSession, url: str, max_retries: int = 3) -> str:
    """Fetch content from URL with retry logic"""
    for attempt in range(max_retries + 1):
        try:
            async with session.get(url) as response:
                return await response.text()
        except (ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries:
                raise ClientError(f"Error fetching {url} after {max_retries} retries: {str(e)}")
            await asyncio.sleep((2 ** attempt) + random.random() * 0.1)
    return ""  # Fallback return

def search_tag(data: str, pattern: Optional[str] = None) -> int:
    """Search and count words within specific tags from text"""
    if not data:
        return 0
    
    compiled_pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL) if pattern else pattern_compiled
    a_tags = compiled_pattern.findall(data)
    return sum(len(tag.split()) for tag in a_tags if tag)

async def results(url: str) -> int:
    """Fetch URL and count tags with optimized caching"""
    session = await get_session()
    html = await fetch(session, url)
    return search_tag(html)

async def cleanup():
    """Clean up resources when done"""
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None
