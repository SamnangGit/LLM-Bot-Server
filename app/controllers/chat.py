from models.chat import GenerativeModel
from schemas.chat import Message

class ChatController:
    def __init__(self):
        self.model = GenerativeModel()


    def send_message(self, message):
        response = self.model.start_chat(message)
        return response
