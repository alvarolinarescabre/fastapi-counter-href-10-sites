from fastapi import APIRouter
from conf.settings import Settings
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from timeit import default_timer as timer

from libs.helpers import delete_dir, download_file, create_dir, search_tag


router = APIRouter()
settings = Settings()


@router.get("/")
async def index():
    return {"Uses Path": "/ping | /counter | /docs"}


@router.get("/ping")
async def healthcheck():
    return {"success": "pong!"}


@router.get("/counter")
def counter_tags():
    output = {}
    start = timer()
    create_dir(settings.dir_download)
    create_dir(settings.dir_counted)

    for key, page in enumerate(settings.random_website):
        output[key] = search_tag(settings.dir_counted, download_file(settings.dir_download, page), "href=")

    delete_dir(settings.dir_download)
    delete_dir(settings.dir_counted)

    end = timer()
    output[10] = f"The Execution Time take: {round(end - start, 2)} seconds"

    json_data = jsonable_encoder(output)

    return JSONResponse(content=json_data)
