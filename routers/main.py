import requests
from io import StringIO
from timeit import default_timer as timer
from fastapi import APIRouter
from conf.settings import Settings
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from libs.helpers import search_tag

router = APIRouter()
settings = Settings()

@router.get("/")
async def index():
    return {"Uses Path": "/v1/tags | /docs | /healthcheck"}

@router.get("/v1/tags")
async def get_tags():
    """
    Get tags from file
    :return: JSON with tags
    """
    start = timer()
    content = []
    
    for id, url in enumerate(settings.urls):
        data = requests.get(url).text
        result = search_tag(data, settings.tag)
        
        end = timer()
        
        if result:
            content.append(
                {
                    "id": id,
                    "url": url,
                    "tag": settings.tag,
                    "result": result,
                    "time": end - start
                })
        else:
            content.append(
                {
                    "id": id,
                    "url": url,
                    "tag": settings.tag,
                    "result": None,
                    "time": end - start
                })

    return JSONResponse(
            jsonable_encoder(
                {
                    "data": content,
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