from models.chat import GenerativeModel
from schemas.chat import Message
from utils.platform_util import PlatformUtils

class ChatController:
    def __init__(self):
        self.platform_util = PlatformUtils()
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
        try:
            response, platform, model_code = self.model.start_custom_chat(model, messages, temperature, top_p, top_k)
            formatted_response = self.standardize_response(model_code, platform, response)
        except Exception as e:
            return {"error": str(e)}
        return formatted_response
    

    def standardize_response(self, model_code, platform, response):
        if platform == "groq_platform":
            standardized_response = {
                "content": response.content,
                "response_metadata": {
                    "token_usage": {
                        "completion_tokens": response.response_metadata['token_usage']['completion_tokens'],
                        "prompt_tokens": response.response_metadata['token_usage']['prompt_tokens'],
                        "total_tokens": response.response_metadata['token_usage']['total_tokens']
                    },
                    "model_name": model_code,
                }
            }
            return standardized_response
        elif platform == "deepinfra_platform":
                standardized_response = {
                    "content": response,
                    "response_metadata": {
                        "token_usage": {
                            "completion_tokens": 0,
                            "prompt_tokens": 0,
                            "total_tokens": 0
                        },
                        "model_name": model_code,
                    }
                }
                return standardized_response
        elif platform == "anthropic_platform":
            response = response['response'],
        elif platform == "openai_platform":
                standardized_response = {
                    "content": response,
                    "response_metadata": {
                        "token_usage": {
                            "completion_tokens": 0,
                            "prompt_tokens": 0,
                            "total_tokens": 0
                        },
                        "model_name": model_code,
                    }
                }
                return standardized_response
        elif platform == "gemini_platform":
                standardized_response = {
                    "content": response.content,
                    "response_metadata": {
                        "token_usage": {
                            "completion_tokens": 0,
                            "prompt_tokens": 0,
                            "total_tokens": 0
                        },
                        "model_name": model_code,
                    }
                }
                return standardized_response
        elif platform == "ollama_platform":
            standardized_response = {
                "content": response,
                "response_metadata": {
                    "token_usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                        "total_tokens": 0
                    },
                    "model_name": model_code,
                }
                    
            }
            return standardized_response
        else:
            response = response['response']


    def get_llm_platforms(self):
        return self.platform_util.get_llm_platforms()
        
        
