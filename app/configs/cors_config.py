from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app):
    # origin_url = "http://localhost:5173"
    origin_url = "*"
    
    origins = [
        origin_url,
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins="http://localhost:5173/",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
