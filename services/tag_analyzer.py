import re
from typing import List, Dict, Any, Protocol, Optional
import asyncio

from conf.settings import get_settings
from repositories.web_repository import WebRepository, get_web_repository
from models.schemas import TagResult


class TagAnalyzerService(Protocol):
    """Interface for the tag analysis service"""
    async def count_tags(self, url: str) -> int:
        """Counts href tags in a URL"""
        ...

    async def analyze_url(self, url: str, url_id: int) -> TagResult:
        """Analyzes a URL and returns structured result"""
        ...

    async def analyze_all_urls(self) -> List[TagResult]:
        """Analyzes all configured URLs and returns results"""
        ...


class HrefTagAnalyzer:
    """Implementation of the href tag analysis service"""

    def __init__(self, repository: Optional[WebRepository] = None):
        self._settings = get_settings()
        self._repository = repository or get_web_repository()
        # Compile the regex pattern once for reuse
        self._pattern = re.compile(
            r'<a\s+[^>]*href\s*=\s*["\'](?:http|https)://[^"\']*["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL
        )

    def _count_href_tags(self, html_content: str) -> int:
        """Counts href tags in HTML content"""
        if not html_content:
            return 0

        a_tags = self._pattern.findall(html_content)
        return sum(len(tag.split()) for tag in a_tags if tag)

    async def count_tags(self, url: str) -> int:
        """Counts href tags in a URL"""
        html_content = await self._repository.get_content(url)
        return self._count_href_tags(html_content)

    async def analyze_url(self, url: str, url_id: int) -> TagResult:
        """Analyzes a URL and returns structured result"""
        count = await self.count_tags(url)
        return TagResult(url_id=url_id, url=url, count=count)

    async def analyze_all_urls(self) -> List[TagResult]:
        """Analyzes all configured URLs and returns results"""
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(min(len(self._settings.urls), asyncio.get_event_loop().get_default_executor()._max_workers or 4))

        async def process_url(url_id: int, url: str) -> TagResult:
            async with semaphore:
                return await self.analyze_url(url, url_id)

        # Process all URLs concurrently
        tasks = [process_url(i, url) for i, url in enumerate(self._settings.urls)]
        results = await asyncio.gather(*tasks)

        return results


# Singleton factory to get service implementation
_service_instance: Optional[TagAnalyzerService] = None

def get_tag_analyzer_service() -> TagAnalyzerService:
    """Factory to get the analysis service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = HrefTagAnalyzer()
    return _service_instance
