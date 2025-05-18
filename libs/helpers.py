import re
import random
import logging
from typing import Optional
from aiohttp import ClientSession, ClientTimeout, ClientError, TCPConnector
from aiohttp_client_cache.session import CachedSession
from aiohttp_client_cache import SQLiteBackend
import asyncio

from conf.settings import get_settings

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()

# Pre-compile regex pattern for better performance - using flags for optimization
pattern_compiled = re.compile(r'<a\s+[^>]*href\s*=\s*["\'](?:http|https)://[^"\']*["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)

# Performance constants
TIMEOUT = ClientTimeout(total=settings.timeout)  # Timeout from settings
CACHE_TTL = settings.cache_expire  # Use cache time from settings
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; FastAPICounter/1.0)',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Global session variable with lock for thread safety
_session: Optional[ClientSession] = None
_session_lock = asyncio.Lock()

async def get_session() -> ClientSession:
    """
    Returns a singleton session with HTTP caching enabled
    
    Returns:
        ClientSession: An HTTP session with caching
    """
    global _session
    async with _session_lock:
        if _session is None or _session.closed:
            # Optimization: Use a custom TCP connector for all sessions
            connector = TCPConnector(
                limit=200,         # Increased limit of simultaneous connections
                ttl_dns_cache=600, # Increased DNS cache TTL to reduce lookups
                ssl=False,         # Disable SSL for faster connections if not needed
                use_dns_cache=True,# Use DNS cache
                force_close=False, # Allow connection reuse
            )
            
            # Use a SQLite cache backend if configured that way, otherwise in memory
            if settings.cache_backend == "sqlite":
                cache_backend = SQLiteBackend(
                    cache_name=settings.cache_db_path,
                    expire_after=CACHE_TTL,
                    allowed_methods=('GET', 'HEAD'), # Only cache GET and HEAD
                    allowed_codes=(200,),           # Only cache 200 responses
                )
                _session = CachedSession(
                    cache=cache_backend,
                    timeout=TIMEOUT,
                    headers=REQUEST_HEADERS,
                    raise_for_status=True,
                    connector=connector
                )
            else:
                # Fallback to normal session if there are issues with the cache
                _session = ClientSession(
                    timeout=TIMEOUT,
                    headers=REQUEST_HEADERS,
                    raise_for_status=True,
                    connector=connector
                )
        return _session

async def fetch(session: ClientSession, url: str, max_retries: int = 3) -> str:
    """
    Fetch content from a URL with optimized performance and retry logic
    
    Args:
        session: The aiohttp session to use
        url: The URL to fetch
        max_retries: Maximum number of retries on failure
        
    Returns:
        str: The text content of the response
        
    Raises:
        ClientError: If there's an error fetching the URL after all retries
    """
    retries = 0
    backoff = 1  # Initial backoff in seconds
    
    while retries <= max_retries:
        try:
            async with session.get(url) as response:
                return await response.text()
                
        except (ClientError, asyncio.TimeoutError) as e:
            retries += 1
            if retries > max_retries:
                raise ClientError(f"Error fetching {url} after {max_retries} retries: {str(e)}")
                
            # Exponential backoff with jitter
            jitter = random.random() * 0.1
            await asyncio.sleep(backoff + jitter)
            backoff *= 2  # Exponential backoff
            
        except Exception as e:
            raise ClientError(f"Unexpected error with {url}: {str(e)}")
    
    # En caso de que retries > max_retries y salga del ciclo sin excepción o return
    raise ClientError(f"Error fetching {url} after {max_retries} retries")

def search_tag(data: str, pattern: Optional[str] = None) -> int:
    """
    Search and count words within specific tags from text
    
    Args:
        data: The HTML content to search
        pattern: Optional regex pattern (uses default if None)
        
    Returns:
        int: Count of words found within matching tags
    """
    if not data:
        return 0
    
    # Use provided pattern or default pattern
    if pattern:
        # For custom patterns, use re.compile for better performance
        compiled_pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        a_tags = compiled_pattern.findall(data)
    else:
        # Use the precompiled pattern for better performance
        # Extract text content between <a> tags with href
        a_tags = pattern_compiled.findall(data)
    
    # Optimized version: uses list comprehension to count words
    # This is faster than a for loop with if condition
    return sum(len(tag.split()) for tag in a_tags if tag)

async def results(url: str) -> int:
    """
    Fetch URL and count tags with optimized caching
    
    Args:
        url: The URL to analyze
        
    Returns:
        int: Count of words in matching tags
        
    Raises:
        ClientError: If there's an error fetching the URL
    """
    session = await get_session()
    html = await fetch(session, url)
    return search_tag(html)

async def cleanup():
    """
    Clean up resources when done
    """
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None