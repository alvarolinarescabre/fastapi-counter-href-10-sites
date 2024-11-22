import os
import uvicorn
from fastapi import FastAPI
from conf.settings import Settings
from routers import main

settings = Settings()
app = FastAPI(docs_url="/docs", openapi_prefix="/")
app.include_router(main.router)

if __name__ == "__main__":
    uvicorn_app = f"{os.path.basename(__file__).removesuffix('.py')}:app"
    uvicorn.run(uvicorn_app, host="0.0.0.0", port=80, reload=True, timeout_workers=600)
