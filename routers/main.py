from timeit import default_timer as timer
from fastapi import APIRouter, Path
from starlette.responses import FileResponse

from conf.settings import Settings
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from libs.helpers import results

router = APIRouter()
settings = Settings()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend())
    yield

favicon_path = 'favicon.ico'

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@router.get("/")
@cache(expire=60)
async def index():
    return JSONResponse(
        jsonable_encoder(
            {
                "data": "/v1/tags | /docs | /healthcheck",
            }
        )
    )

@router.get("/v1/tags")
@cache(expire=60)
async def get_tags():
    """
    Get pattern https?://
    :return: JSON with results
    """

    start = timer()
    content = []

    for url_id, url in enumerate(settings.urls):
        result = await results(url)

        if result:
            content.append(
                {
                    "id": url_id,
                    "url": url,
                    "result": result,
                })
        else:
            content.append(
                {
                    "id": url_id,
                    "url": url,
                    "result": None,
                })

    end = timer()

    return JSONResponse(
        jsonable_encoder(
            {
                "data": content,
                "time": end - start
            }
        )
    )

@router.get("/v1/tags/{url_id}")
@cache(expire=60)
async def get_tag(url_id: int = Path(...)):
    """
    Get pattern https?://
    :return: JSON with results
    """

    start = timer()
    content = []

    try:
        url = settings.urls[url_id]
        result = await results(url)

        if result:
            content.append(
                {
                    "id": url_id,
                    "url": url,
                    "result": result,
                })
        else:
            content.append(
                {
                    "id": url_id,
                    "url": url,
                    "result": None,
                })

        end = timer()

        return JSONResponse(
            jsonable_encoder(
                {
                    "data": content,
                    "time": end - start
                }
            )
        )
    except IndexError:
        return JSONResponse(
            jsonable_encoder(
                {
                    "data": "id must be between 0 and 9",
                }
            )
        )


@router.get("/healthcheck")
async def healthcheck():
    """
    Healthcheck endpoint
    :return: JSON with success message
    """
    return  JSONResponse(
        jsonable_encoder(
            {
                "data": "Ok!",
            }
        )
    )
