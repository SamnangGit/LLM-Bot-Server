from fastapi import APIRouter, Request
from controllers.chat import ChatController
from schemas.chat import Message

router = APIRouter()
chat_controller = ChatController()

@router.post("/message")
async def send_message(request: Request):
    data = await request.json()
    message = data["message"]
    response = chat_controller.send_message(message)
    return {"response": response}

