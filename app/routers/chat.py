from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from controllers.chat import ChatController
from utils.session_util import SessionUtils

router = APIRouter()
chat_controller = ChatController()

@router.post("/")
async def send_chat_message(request: Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
        print(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    response = chat_controller.start_chat(data)
    return {"response": response}


@router.post("/custom")
async def send_custom_chat_message(request: Request, response: Response):
    # Check Content-Type header
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
        print("data: " + str(data))
        uuid = SessionUtils.get_session_id(request)
        if uuid is None:
            response.set_cookie(
                key="uuid",
                value=SessionUtils.generate_session_id(),
                max_age=86400,  # Cookie expires in 1 day
                httponly=True,
                samesite="None",  # Allow cross-site cookies
                secure=False,  # Only send cookie over HTTPS if True
            )
        else:
            data["uuid"] = uuid
            print("uuid: " + data["uuid"])  
            print("data: " + str(data))
        # data["uuid"] = uuid
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    print("cookies: " + str(SessionUtils.get_session_id(request)))
    response_data = chat_controller.start_custom_chat(data)
    return {"response": response_data}



@router.get("/platforms")
async def get_platforms(response: Response, request: Request):
    uuid = SessionUtils.get_session_id(request)
    if uuid is None:
        response.set_cookie(
            key="uuid",
            value=SessionUtils.generate_session_id(),
            max_age=86400,  # Cookie expires in 1 day
            httponly=True,
            samesite="None",  # Allow cross-site cookies
            secure=False,  # Only send cookie over HTTPS if True
        )
    platforms = chat_controller.get_llm_platforms()
    return platforms


@router.post("/stream_chat")
async def stream_chat(request: Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    
    try:
        generator = await chat_controller.stream_chat(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return StreamingResponse(generator, media_type="text/event-stream")



@router.post("/stream_chat_memory")
async def stream_chat_memory(request: Request):
    data = await request.json()
    gen = await chat_controller.stream_chat_memory(data)
    return StreamingResponse(gen, media_type="text/event-stream")


@router.post("/stream_chat_es")
async def stream_chat_es(request: Request):
    data = await request.json()
    gen = chat_controller.stream_chat_es(data)
    return StreamingResponse(
            gen,
            media_type="text/event-stream"
        )