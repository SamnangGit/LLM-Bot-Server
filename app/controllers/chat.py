from models.chat import GenerativeModel
from schemas.chat import Message

class ChatController:
    def __init__(self):
        self.model = GenerativeModel()


    def send_message(self, message_text):
        # message = Message(text=message_text)
        response = self.model.start_chat(message_text)
        return response
