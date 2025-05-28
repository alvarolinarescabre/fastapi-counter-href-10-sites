import asyncio
import os
from timeit import default_timer as timer
from typing import AsyncIterator, Dict, Any
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import APIRouter, Path, FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from libs.helpers import results, cleanup

# Type aliases
ResultItem = Dict[str, Any]

# Router and settings
router = APIRouter()

@lru_cache()
def get_settings():
    from conf.settings import Settings
    return Settings()

settings = get_settings()

# Constants for responses
RESPONSES = {
    'index': {"data": "/v1/tags | /docs | /healthcheck"},
    'health': {"data": "Ok!"},
    'error': {"data": "id must be between 0 and 9"}
}

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Application lifespan with cache initialization and cleanup"""
    FastAPICache.init(
        InMemoryBackend(),
        prefix="fastapi-cache", 
        expire=settings.cache_expire
    )
    yield
    await cleanup()

@router.get("/")
async def index() -> JSONResponse:
    """Index endpoint with navigation info"""
    return JSONResponse(RESPONSES['index'])

@router.get("/healthcheck")
async def healthcheck() -> JSONResponse:
    """Health check endpoint"""
    return JSONResponse(RESPONSES['health'])

@router.get("/favicon.ico")
async def favicon() -> FileResponse:
    """Serve favicon"""
    return FileResponse('favicon.ico')

@router.get("/v1/tags/{url_id}")
@cache(expire=settings.cache_expire)
async def get_tag(url_id: int = Path(..., ge=0, le=9)) -> JSONResponse:
    """Get href count for a specific URL by ID"""
    if not (0 <= url_id <= 9):
        return JSONResponse(RESPONSES['error'], status_code=422)
    
    start = timer()
    count = await results(settings.urls[url_id])
    end = timer()
    
    return JSONResponse({
        "url_id": url_id,
        "url": settings.urls[url_id],
        "count": count,
        "time": round(end - start, 4)
    })

@router.get("/v1/tags")
@cache(expire=settings.cache_expire)
async def get_tags() -> JSONResponse:
    """Get href count for all URLs with parallel processing"""
    start = timer()
    
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(min(len(settings.urls), os.cpu_count() or 4))
    
    async def process_url(url_id: int, url: str) -> ResultItem:
        async with semaphore:
            count = await results(url)
            return {"url_id": url_id, "url": url, "count": count}
    
    # Process all URLs concurrently
    tasks = [process_url(i, url) for i, url in enumerate(settings.urls)]
    data = await asyncio.gather(*tasks)
    
    end = timer()
    
    return JSONResponse({
        "data": data,
        "total_time": round(end - start, 4),
        "urls_processed": len(data)
    })