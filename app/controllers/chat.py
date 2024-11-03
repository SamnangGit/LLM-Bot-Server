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
from tools.web_tools import WebTools
from tools.save_to_file_tool import WebContentSaverTool
from tools.read_from_file_tool import WebContentReaderTool
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
            
    def web_chat(self, query):
        llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        scraper_tool = WebTools()
        save_tool = WebContentSaverTool()
        reader_tool = WebContentReaderTool()
        
        functions = [
            {
                "name": "web_tool",
                "description": scraper_tool.description,
                "parameters": scraper_tool.args_schema.schema()
            },
            {
                "name": "web_content_saver_tool",
                "description": save_tool.description,
                "parameters": save_tool.args_schema.schema()
            },
            {
                "name": "web_content_reader_tool",
                "description": reader_tool.description,
                "parameters": reader_tool.args_schema.schema()
            }
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that uses web tools to find and manage information.
            When you need to search for new information, use the web_tool function.
            After getting web content, if the user wants to save the scraped content to a file,
            you should always save it using the web_content_saver_tool function.
            When the user wants to retrieve previously saved content, you MUST use the web_content_reader_tool function.
            
            For the web_content_reader_tool, you MUST ALWAYS specify both query_type and value:
            - query_type: One of 'latest', 'by_domain', 'by_date', 'search', or 'file'
            - value: The search term, domain, date, or filename to look for (use empty string "" for 'latest' queries)
            - max_results: Number of results to return (optional, default 5)
            
            Example function calls:
            - For latest content: 
            {{"query_type": "latest", "value": ""}}
            - For domain search: 
            {{"query_type": "by_domain", "value": "example.com"}}
            - For date search: 
            {{"query_type": "by_date", "value": "2024-10-18"}}
            
            Always include both query_type and value parameters in your function calls."""),
            ("human", "{query}")
        ])

        
        messages = prompt.format_messages(query=query)
        response = llm.invoke(messages, functions=functions)
        
        if response.additional_kwargs.get("function_call"):
            function_call = response.additional_kwargs["function_call"]
            function_name = function_call["name"]
            function_args = json.loads(function_call["arguments"])
            
            if function_name == scraper_tool.name:
                # First, get the web content
                scraped_content = scraper_tool._run(**function_args)
                
                # Convert scraped_content to dictionary if it's a string
                if isinstance(scraped_content, str):
                    try:
                        content_dict = json.loads(scraped_content)
                    except json.JSONDecodeError:
                        content_dict = {
                            "url": function_args.get("url", ""),
                            "title": "Scraped Content",
                            "content": scraped_content,
                            "paragraphs": [scraped_content]
                        }
                else:
                    content_dict = scraped_content
                    
                # Add the scraped content to messages
                messages.append(AIMessage(content=str(scraped_content)))
                messages.append(
                    FunctionMessage(
                        content=str(scraped_content),
                        name=function_name
                    )
                )
                
                # Now, call the save tool with the content
                save_response = save_tool._run(content=content_dict)
                
                # Add the save response to messages
                messages.append(
                    FunctionMessage(
                        content=str(save_response),
                        name=save_tool.name
                    )
                )
                
                # Get the final response from the model
                final_response = llm.invoke(messages, functions=functions)
                return {"result": final_response.content}
                
            elif function_name == save_tool.name:
                # Direct call to save tool
                save_response = save_tool._run(**function_args)
                messages.append(
                    FunctionMessage(
                        content=str(save_response),
                        name=function_name
                    )
                )
                final_response = llm.invoke(messages, functions=functions)
                return {"result": final_response.content}
                
            elif function_name == "web_content_reader_tool":
                # Handle content retrieval
                reader_response = reader_tool._run(**function_args)
                
                # Add the reader response to messages
                messages.append(
                    FunctionMessage(
                        content=str(reader_response),
                        name=function_name
                    )
                )
                
                # Get final response from the model
                final_response = llm.invoke(messages)
                return {"result": final_response.content}
        
        # If no function call is needed, return the initial response
        return {"result": response.content}
    

    def chat_with_tool(self, query):
        llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        try:
            onlineSearchTool = OnlineSearchTool()
            search_tools = onlineSearchTool.get_tools()
            # file_ops_tools = FileOpsTool();
            file_tools = FileOpsTool().get_tools()
            print(file_tools)
            tools = []
            tools.extend(search_tools)
            tools.extend(file_tools)
            # tool = tools[0] 


            # print(tools)
            # print(tool.description)
            
            # print(tool.name)
     
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
