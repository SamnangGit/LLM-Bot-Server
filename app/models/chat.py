import asyncio
import ssl
from datetime import datetime

from typing import AsyncIterable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import DeepInfra, Ollama
from langchain_anthropic import ChatAnthropic

from langchain_community.chat_message_histories import (
    UpstashRedisChatMessageHistory,
)

from langchain.prompts import PromptTemplate

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

from configs.config import safety_settings, generation_settings
from schemas.chat import Message
import os
from dotenv import load_dotenv

from langchain.callbacks import AsyncIteratorCallbackHandler

from utils.platform_util import PlatformUtils

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

class GenerativeModel:

    def __init__(self):
        self.platform_utils = PlatformUtils()
        self.chat = None

        # initialize redis
        redis_url = os.getenv("REDIS_URL")
        redis_token = os.getenv("REDIS_TOKEN")


        history = UpstashRedisChatMessageHistory(
            url=redis_url, token=redis_token, ttl=0, session_id=self.generate_session_id()
        )

        self.memory = ConversationBufferMemory(
            chat_memory=history,
            return_messages=True,
        )

    def gemini_platform(self, model_code, temperature):
        llm = ChatGoogleGenerativeAI(model=model_code, 
                                      google_api_key=os.getenv("GEMINI_API_KEY"),
                                      safety_settings=safety_settings,
                                      temperature=temperature,
                                      top_p=generation_settings['top_p'],
                                      top_k=generation_settings['top_k'],
                                      streaming=True,
                                      verbose=True,
                                      )    
        return llm  

    def openai_platform(self, model_code, temperature):
        template = """Question: {question}

        Answer: Let's think step by step."""

        prompt = PromptTemplate.from_template(template)
            
        # llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"),
        #              temperature=generation_settings['temperature'],
        #              top_p=generation_settings['top_p'],
        #             streaming=False)

        llm = OpenAI(model=model_code, openai_api_key=os.getenv("OPENAI_API_KEY"),
                     temperature=temperature, streaming=True)
        llm_chain = prompt | llm

        return llm_chain
    

    def groq_platform(self, model_code, temperature=0.5):
        llm = ChatGroq(model=model_code, api_key=os.getenv("GROQ_API_KEY"),
                        temperature=temperature)
        print(f"Model: {model_code}, Temperature: {temperature}")
        # stream=True
        return llm
    

    def deepinfra_platform(self, model_code, temperature):
        llm = DeepInfra(model_id=model_code, deepinfra_api_token=os.getenv("DEEPINFRA_API_TOKEN"),
                        model_kwargs = {"temperature": temperature, 
                                        "top_p": generation_settings['top_p'],
                                        # "top_k": generation_settings['top_k'],
                                        "repetition_penalty": 1.2})
        return llm
    

    def anthropic_platform(self, model_code, temperature=0.5):
        llm = ChatAnthropic(model_name=model_code, api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=temperature)
        # , streaming=True
        return llm
    
    def ollama_platform(self, model_code, temperature=0.5):
        llm = Ollama(model=model_code, temperature=temperature)
        return llm
        


    def start_chat(self, message: Message):
        response = self.chat.invoke(message)
        return response

    def start_custom_chat(self, model, message: Message, temperature, top_p, top_k):

        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        if model_code and platform:
            llm = getattr(self, platform)(model_code, temperature)
            self.chat = ConversationChain(llm=llm, memory=self.memory)
        else:
            return {"error": "Model not found"}, 400

        try:
            response = self.chat.predict(input=message)
            # history.add_messages(response)
            print(f"Response: {response}")
        except Exception as e:
            return {"error": str(e)}
        finally:
            print(type(response))
            # history.add_message(conte)

        return response, platform, model_code
    

    async def start_chat_stream(self, model: str, message, temperature: float, top_p: float, top_k: int) -> AsyncIterable[str]:
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        self.chat = getattr(self, platform)(model_code, temperature)
        # print(self.chat)
        # print(f"Model: {model_code}, Platform: {platform}")
        ai_msg = "";
        stream = self.chat.astream(message)

        try:
            async for chunk in stream:
                yield chunk.content
                # print(f"Yielding chunk: {chunk.content}")
                # yield chunk
                ai_msg += chunk.content
        except Exception as e:
            print(f"Caught exception: {e}")
        finally:
            # print ai_msg here
            print(f"AI Message: {ai_msg}")
            print("Stream completed")


    def generate_session_id(self):
        date = datetime.now()
        timestamp = date.strftime("%Y%m%d")
        sequence = str(date.hour * 3600 + date.minute * 60 + date.second).zfill(5)
        return f"{timestamp}-{sequence}"