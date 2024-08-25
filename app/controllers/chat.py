import ast
from fastapi.responses import StreamingResponse
from models.chat import GenerativeModel
from schemas.chat import Message
from utils.platform_util import PlatformUtils

import json
import re

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
        uuid = data.get("uuid")
        # try:
        response, platform, model_code = self.model.start_custom_chat(model, messages, temperature, top_p, top_k, uuid)
        formatted_response = self.standardize_response(model_code, platform, response)
        # except Exception as e:
        #     return {"error": str(e)}
        return formatted_response
    

    def standardize_response(self, model_code, platform, response):
        if platform == "groq_platform":
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
                "content": self.parse_chat_messages(response),
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
    

    async def stream_chat(self, data):
        model = data.get("model")
        messages_data = data.get("messages")
        temperature = data.get("temperature")
        top_p = data.get("top_p")
        top_k = data.get("top_k")
        
        messages = messages_data
        
        try:
            generator = self.model.start_chat_stream(model, messages, temperature, top_p, top_k)
        except Exception as e:
            raise Exception(f"Error in starting chat stream: {e}")
        
        return generator



    async def stream_chat_memory(self, data):
        model = data.get("model")
        messages_data = data.get("messages")
        temperature = data.get("temperature")
        top_p = data.get("top_p")
        top_k = data.get("top_k")
        
        messages = messages_data
        
        try:
            generator = self.model.start_chat_stream_memory(model, messages, temperature, top_p, top_k)
        except Exception as e:
            raise Exception(f"Error in starting chat stream: {e}")
        
        return generator
        


    async def stream_chat_es(self, data):
        model = data.get("model")
        messages_data = data.get("messages")
        temperature = data.get("temperature")
        top_p = data.get("top_p")
        top_k = data.get("top_k")
        
        messages = messages_data
        
        try:
            generator = self.model.start_chat_stream_memory_es(model, messages, temperature, top_p, top_k)
        except Exception as e:
            raise Exception(f"Error in starting chat stream: {e}")
        
        return generator

    def parse_chat_messages(self, raw_string):
        cleaned_string = re.sub(r'^(Human:|AI:)\s*', '', raw_string.strip())
        print("clean string: " + cleaned_string)

        try:
            json_string = cleaned_string.replace("'", '"')
            # Parse the JSON string
            data = json.loads(json_string)
            # Extract and return the content
            return data[0]['content']
        except (json.JSONDecodeError, IndexError, KeyError):
            return "Error: Could not parse the message or extract content."