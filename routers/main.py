from timeit import default_timer as timer
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Path, FastAPI, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from conf.settings import get_settings
from models.schemas import TagResult, TagsResponse, HealthResponse, IndexResponse, ErrorResponse
from services.tag_analyzer import get_tag_analyzer_service, TagAnalyzerService
from repositories.web_repository import get_web_repository

# Router and settings
router = APIRouter()
settings = get_settings()

# Constants for common responses
RESPONSES = {
    'index': IndexResponse(data="/v1/tags | /docs | /healthcheck"),
    'health': HealthResponse(),
    'error': ErrorResponse(data="id must be between 0 and 9")
}

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle with cache initialization and cleanup"""
    # Initialize cache
    FastAPICache.init(
        InMemoryBackend(),
        prefix="fastapi-cache",
        expire=settings.cache_expire
    )
    yield
    # Clean up resources at the end
    await get_web_repository().cleanup()

@router.get("/", response_model=IndexResponse)
async def index() -> JSONResponse:
    """Main endpoint with navigation information"""
    return JSONResponse(RESPONSES['index'].dict())

@router.get("/healthcheck", response_model=HealthResponse)
async def healthcheck() -> JSONResponse:
    """Health check endpoint"""
    return JSONResponse(RESPONSES['health'].dict())

@router.get("/favicon.ico")
async def favicon() -> FileResponse:
    """Serve the favicon"""
    return FileResponse('favicon.ico')

@router.get("/v1/tags/{url_id}", response_model=TagResult)
@cache(expire=settings.cache_expire)
async def get_tag(
    url_id: int = Path(..., ge=0, le=9),
    service: TagAnalyzerService = Depends(get_tag_analyzer_service)
) -> JSONResponse:
    """Get href count for a specific URL by ID"""
    if not (0 <= url_id <= 9):
        return JSONResponse(RESPONSES['error'].dict(), status_code=422)

    start = timer()
    result = await service.analyze_url(settings.urls[url_id], url_id)
    end = timer()

    response_data = result.dict()
    response_data['time'] = round(end - start, 4)

    return JSONResponse(response_data)

@router.get("/v1/tags", response_model=TagsResponse)
@cache(expire=settings.cache_expire)
async def get_tags(
    service: TagAnalyzerService = Depends(get_tag_analyzer_service)
) -> JSONResponse:
    """Get href count for all URLs with parallel processing"""
    start = timer()

    results = await service.analyze_all_urls()

    end = timer()

    response = TagsResponse(
        data=results,
        total_time=round(end - start, 4),
        urls_processed=len(results)
    )

    return JSONResponse(response.dict())
