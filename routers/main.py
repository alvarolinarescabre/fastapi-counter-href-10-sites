from timeit import default_timer as timer
from fastapi import APIRouter, Path
from conf.settings import Settings
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from libs.helpers import results

router = APIRouter()
settings = Settings()

@router.get("/")
async def index():
    return JSONResponse(
        jsonable_encoder(
            {
                "data": "/v1/tags | /docs | /healthcheck",
            }
        )
    )

@router.get("/v1/tags")
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
                    "data": "id must be 0 > to < 9",
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