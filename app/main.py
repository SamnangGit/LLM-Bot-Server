from fastapi import FastAPI
# from routers.chat import router
from routers.auth import router as auth_router
from routers.chat import router as chat_router
from configs.cors_config import configure_cors

app = FastAPI()

configure_cors(app)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
# app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)  # Run the app with localhost