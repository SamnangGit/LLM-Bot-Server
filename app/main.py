from fastapi import FastAPI
from routers.chat import router

app = FastAPI()

app.include_router(router)
