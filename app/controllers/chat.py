from models.chat import GenerativeModel
from schemas.chat import Message

class ChatController:
    def __init__(self):
        self.model = GenerativeModel()


    def start_chat(self, message):
        response = self.model.start_chat(message)
        return response
    

    # def start_custom_chat(self, data: dict):
    #     model = data.get("model")
    #     message = data.get("message")
    #     temperature = data.get("temperature")
    #     top_p = data.get("top_p")
    #     top_k = data.get("top_k")
        
    #     if not message:
    #         return {"error": "Message content is required"}, 400
        
    #     content, token_usage, model_name = self.model.start_custom_chat(model, message, temperature, top_p, top_k)
    #     return self.format_response(content, token_usage, model_name)


    def start_custom_chat(self, data):
        model = data.get("model")
        messages = data.get("messages")
        temperature = data.get("temperature")
        top_p = data.get("top_p")
        top_k = data.get("top_k")
        response = self.model.start_custom_chat(model, messages, temperature, top_p, top_k)
        return response



    

    def format_response(self, content, token_usage, model_name):
        return {
            "content": content,
            "response_metadata": {
                "token_usage": token_usage,
                "model_name": model_name
            }
        }