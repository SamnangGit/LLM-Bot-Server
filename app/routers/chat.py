from fastapi import APIRouter, Request, HTTPException
from controllers.chat import ChatController

router = APIRouter()
chat_controller = ChatController()

@router.post("/chat")
async def send_chat_message(request: Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    message = data.get("message")
    if message is None:
        raise HTTPException(status_code=400, detail="Message field is required")
    response = chat_controller.send_message(message)
    return {"response": response}



@router.post("/chat/custom")
async def send_custom_chat_message(request: Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    response = chat_controller.start_custom_chat(data)
    return {"response": response}


@router.get("/platforms")
async def get_platforms():
    platforms = chat_controller.get_llm_platforms()
    return platforms

