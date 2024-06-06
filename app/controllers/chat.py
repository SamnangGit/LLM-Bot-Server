from models.chat import GenerativeModel
from schemas.chat import Message

class ChatController:
    def __init__(self):
        self.model = GenerativeModel()


    def start_chat(self, message):
        response = self.model.start_chat(message)
        return response
    

    def start_custom_chat(self, data):
        model = data.get("model")
        messages = data.get("messages")
        temperature = data.get("temperature")
        top_p = data.get("top_p")
        top_k = data.get("top_k")
        response = self.model.start_custom_chat(model, messages, temperature, top_p, top_k)
        return response