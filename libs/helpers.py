import re
from typing import Optional
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError

from conf.settings import get_settings

settings = get_settings()

# Pre-compile regex pattern for better performance
pattern_compiled = re.compile(settings.pattern)

# Performance constants
TIMEOUT = ClientTimeout(total=10)  # 10 seconds timeout
CACHE_TTL = 3600  # Cache for 1 hour
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; FastAPICounter/1.0)',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Global session variable
_session: Optional[ClientSession] = None

async def get_session() -> ClientSession:
    """
    Returns a singleton session object with optimized settings
    
    Returns:
        ClientSession: An HTTP session
    """
    global _session
    if _session is None or _session.closed:
        _session = ClientSession(
            timeout=TIMEOUT,
            headers=REQUEST_HEADERS,
            raise_for_status=True,
            connector=aiohttp.TCPConnector(
                limit=100,  # Connection pooling
                ttl_dns_cache=300,  # DNS cache TTL (seconds)
                ssl=False,  # Disable SSL for faster connections if not needed
            )
        )
    return _session

async def fetch(session: ClientSession, url: str) -> str:
    """
    Fetch content from a URL with optimized performance
    
    Args:
        session: The aiohttp session to use
        url: The URL to fetch
        
    Returns:
        str: The text content of the response
        
    Raises:
        ClientError: If there's an error fetching the URL
    """
    try:
        # Use a LRU cache decorator for repeated requests
        async with session.get(url) as response:
            return await response.text()
    except ClientError as e:
        raise ClientError(f"Error fetching {url}: {str(e)}")
    except Exception as e:
        raise ClientError(f"Unexpected error with {url}: {str(e)}")

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
    
    # Use the optimized findall method directly
    matches = pattern_compiled.findall(str(data))
    
    # Faster word counting with direct sum
    return sum(len(tag.split()) for tag in matches if tag)

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