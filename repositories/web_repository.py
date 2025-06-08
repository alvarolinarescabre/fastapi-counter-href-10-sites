import random
import asyncio
from typing import Protocol, Optional
from aiohttp import ClientSession, ClientTimeout, ClientError, TCPConnector
from aiohttp_client_cache.session import CachedSession
from aiohttp_client_cache import SQLiteBackend

from conf.settings import get_settings


class WebRepository(Protocol):
    """Interface for web access repository"""
    async def get_content(self, url: str) -> str:
        """Gets HTML content from a URL"""
        ...

    async def cleanup(self) -> None:
        """Cleans up used resources"""
        ...


class AioHttpRepository:
    """Implementation of WebRepository using aiohttp with cache"""

    def __init__(self):
        self._settings = get_settings()
        self._session: Optional[ClientSession] = None
        self._session_lock = asyncio.Lock()

        # Constants
        self.timeout = ClientTimeout(total=self._settings.timeout)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; FastAPICounter/1.0)',
            'Accept': 'text/html,application/xhtml+xml'
        }

    async def _get_session(self) -> ClientSession:
        """Gets a singleton HTTP session with cache"""
        async with self._session_lock:
            if self._session is None or self._session.closed:
                connector = TCPConnector(
                    limit=200,
                    ttl_dns_cache=600,
                    ssl=False,
                    use_dns_cache=True
                )

                if self._settings.cache_backend == "sqlite":
                    cache = SQLiteBackend(
                        cache_name=self._settings.cache_db_path,
                        expire_after=self._settings.cache_expire
                    )
                    self._session = CachedSession(
                        cache=cache,
                        timeout=self.timeout,
                        headers=self.headers,
                        connector=connector
                    )
                else:
                    self._session = ClientSession(
                        timeout=self.timeout,
                        headers=self.headers,
                        connector=connector
                    )
            return self._session

    async def get_content(self, url: str, max_retries: int = 3) -> str:
        """Gets HTML content from a URL with retries"""
        session = await self._get_session()

        for attempt in range(max_retries + 1):
            try:
                async with session.get(url) as response:
                    return await response.text()
            except (ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries:
                    # Instead of propagating the exception, we return an empty string and log the error
                    # In a production environment, proper logging could be implemented here
                    print(f"Error fetching {url} after {max_retries} retries: {str(e)}")
                    return ""
                # Exponential backoff with jitter to avoid request storms
                await asyncio.sleep((2 ** attempt) + random.random() * 0.1)

        return ""  # Fallback return

    async def cleanup(self) -> None:
        """Cleans up the HTTP session when finished"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None


# Singleton factory to get repository implementation
_repo_instance: Optional[WebRepository] = None

def get_web_repository() -> WebRepository:
    """Factory to get the web repository instance"""
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = AioHttpRepository()
    return _repo_instance
