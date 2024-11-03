import ast
from fastapi.responses import StreamingResponse
from models.chat import GenerativeModel
from schemas.chat import Message
from utils.platform_util import PlatformUtils

from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import Any
from langchain.schema import LLMResult


import json
import re

from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub
from langchain_core.tools import Tool

from tools.online_search_tool import OnlineSearchTool
from tools.file_ops_tool import FileOpsTool

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage, FunctionMessage
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class ChatController:
    def __init__(self):
        self.platform_util = PlatformUtils()
        self.model = GenerativeModel()


    def start_chat(self, data):
        model = data.get("model")
        messages = data.get("messages")
        temperature = data.get("temperature")
        top_p = data.get("top_p")
        top_k = data.get("top_k")
        print("controller ")
        response = self.model.start_chat(model, messages, temperature, top_p, top_k)
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
            generator = await self.model.start_chat_stream_memory(model, messages, temperature, top_p, top_k)
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
        callback_handler = AsyncCallbackHandler()
        try:
            generator = self.model.start_chat_stream_memory_es(model, messages, temperature, top_p, top_k, callback_handler)
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
            
    

    def chat_with_tool(self, query):
        llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        try:
            search_tools = OnlineSearchTool().get_tools()
            file_tools = FileOpsTool().get_tools()
            tools = []
            tools.extend(search_tools)
            tools.extend(file_tools)

            # wrapped_tool = Tool(name=tool.name, 
            #         func=lambda q: tool(q),         
            #         description= tool.description)

            prompt = hub.pull("hwchase17/openai-tools-agent")
            agent = create_openai_tools_agent(llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            result = agent_executor.invoke({"input": query})
        except Exception as e:
            raise Exception(f"Error : {e}")
        return result


class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
    content: str = ""
    final_answer: bool = False

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.content += token
        print("Token: " + token)
        if self.final_answer:
            if '"action_input": "' in self.content:
                if token not in ['"', "}"]:
                    await self.queue.put(token)
        elif "Final Answer" in self.content:
            self.final_answer = True
            self.content = ""

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if self.final_answer:
            self.content = ""
            self.final_answer = False
            await self.queue.put(None)  # Signal the end of the stream
        else:
            self.content = ""
