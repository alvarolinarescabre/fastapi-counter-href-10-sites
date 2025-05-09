import asyncio
from timeit import default_timer as timer
from fastapi import APIRouter
from conf.settings import Settings
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from libs.helpers import results

router = APIRouter()
settings = Settings()

@router.get("/")
async def index():
    return {"Uses Path": "/v1/tags | /docs | /healthcheck"}

@router.get("/v1/tags")
async def get_tags():
    """
    Get pattern https?://
    :return: JSON with results
    """

    start = timer()
    content = []

    for id, url in enumerate(settings.urls):
        result = await results(url)

        if result:
            content.append(
                {
                    "id": id,
                    "url": url,
                    "result": result,
                })
        else:
            content.append(
                {
                    "id": id,
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

@router.get("/healthcheck")
async def healthcheck():
    """
    Healthcheck endpoint
    :return: JSON with success message
    """
    return {"success": "Ok!"}