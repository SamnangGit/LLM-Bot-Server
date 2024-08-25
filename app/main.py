from fastapi import FastAPI
from routers.chat import router
from configs.cors_config import configure_cors

app = FastAPI()

configure_cors(app)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)  # Run the app with localhost