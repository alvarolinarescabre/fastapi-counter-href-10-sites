from timeit import default_timer as timer
import asyncio
import os
from functools import lru_cache
from typing import AsyncIterator, Dict, Any
from contextlib import asynccontextmanager

from fastapi import APIRouter, Path, FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from libs.helpers import results, cleanup

# Define un tipo para los elementos de respuesta para mayor claridad y prevenir errores de tipado
ResultItem = Dict[str, Any]

router = APIRouter()

# Use lru_cache for settings to avoid repeated loading
@lru_cache()
def get_settings():
    from conf.settings import Settings
    return Settings()

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Initialize cache with optimized settings
    FastAPICache.init(
        InMemoryBackend(),
        prefix="fastapi-cache",
        expire=settings.cache_expire
    )
    yield
    # Cleanup resources when shutting down
    await cleanup()

# Pre-define constant paths and responses
FAVICON_PATH = 'favicon.ico'
INDEX_RESPONSE = {"data": "/v1/tags | /docs | /healthcheck"}
HEALTH_RESPONSE = {"data": "Ok!"}
ERROR_RESPONSE = {"data": "id must be between 0 and 9"}

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(FAVICON_PATH)

@router.get("/")
@cache(expire=60)
async def index():
    return JSONResponse(jsonable_encoder(INDEX_RESPONSE))

@router.get("/v1/tags")
@cache(expire=300)  # Aumentado tiempo de caché a 5 minutos para mejorar rendimiento
async def get_tags():
    """
    Get pattern https?:// for all URLs
    
    Returns:
        JSONResponse: Results and timing information
    """
    start = timer()
    
    # Process URLs in parallel with optimized concurrency control
    # Ajustar semáforo según número de CPUs disponibles y carga del sistema
    cpu_count = max(os.cpu_count() or 2, 2)
    # Optimización: Limitar concurrencia según tipo de URLs y capacidad del sistema
    # Para APIs externas, aumentamos un poco el límite para compensar latencia
    semaphore = asyncio.Semaphore(min(cpu_count * 3, 30))  # Balance optimizado
    
    async def process_url(url_id: int, url: str) -> ResultItem:
        """Process a single URL with concurrency control"""
        async with semaphore:
            try:
                result = await results(url)
                return {
                    "id": url_id,
                    "url": url,
                    "result": result if result else None,
                }
            except Exception as e:
                return {
                    "id": url_id,
                    "url": url,
                    "result": None,
                    "error": str(e)
                }
    
    # Create tasks for all URLs and execute in parallel
    tasks = [process_url(url_id, url) for url_id, url in enumerate(settings.urls)]
    
    # Especificar return_exceptions=True para manejar errores sin detener el proceso completo
    content: list[ResultItem] = await asyncio.gather(*tasks, return_exceptions=False)

    end = timer()

    return JSONResponse(
        jsonable_encoder({
            "data": content,
            "time": end - start
        })
    )

@router.get("/v1/tags/{url_id}")
@cache(expire=300)  # Aumentado tiempo de caché a 5 minutos para mejor rendimiento
async def get_tag(url_id: int = Path(..., ge=0, lt=10)):
    """
    Get pattern https?:// for a specific URL
    
    Args:
        url_id: The index of the URL to process (0-9)
    
    Returns:
        JSONResponse: Results and timing information
    """
    start = timer()
    
    try:
        url = settings.urls[url_id]
        result = await results(url)

        content: list[ResultItem] = [{
            "id": url_id,
            "url": url,
            "result": result if result else None,
        }]

        end = timer()

        return JSONResponse(
            jsonable_encoder({
                "data": content,
                "time": end - start
            })
        )
    except IndexError:
        return JSONResponse(jsonable_encoder(ERROR_RESPONSE), status_code=400)

@router.get("/healthcheck")
async def healthcheck():
    """
    Healthcheck endpoint
    
    Returns:
        JSONResponse: Success message
    """
    return JSONResponse(jsonable_encoder(HEALTH_RESPONSE))
