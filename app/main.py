from fastapi import FastAPI
from routers.chat import router
from configs.cors_config import configure_cors

app = FastAPI()

configure_cors(app)

app.include_router(router)
