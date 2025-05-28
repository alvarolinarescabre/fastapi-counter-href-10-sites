import os
import uvicorn
from fastapi import FastAPI
from routers import main

app = FastAPI(lifespan=main.lifespan)
app.include_router(main.router)

if __name__ == "__main__":
    uvicorn.run(f"{os.path.basename(__file__).removesuffix('.py')}:app", host="0.0.0.0", port=8080, reload=True)
