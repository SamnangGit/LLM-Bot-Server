import os
from dotenv import load_dotenv
from datetime import datetime


from langchain_community.chat_message_histories import (
    UpstashRedisChatMessageHistory,
)
from langchain_core.language_models.base import BaseLanguageModel
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_community.llms import Ollama

load_dotenv()

class MemoryUtils:
        
    def init_upstash(self):
        redis_url = os.getenv("REDIS_URL")
        redis_token = os.getenv("REDIS_TOKEN")


        history = UpstashRedisChatMessageHistory(
            url=redis_url, token=redis_token, ttl=0, session_id=self.generate_session_id()
        )
        return history    


    def generate_session_id(self):
        date = datetime.now()
        timestamp = date.strftime("%Y%m%d")
        sequence = str(date.hour * 3600 + date.minute * 60 + date.second).zfill(5)
        return f"{timestamp}-{sequence}"
    

    def init_buffer_memory(self):
        memory = ConversationBufferMemory(
            chat_memory=self.init_upstash(),
            return_messages=True,
        )
        return memory
    
    def init_summary_memory(self):
        memory = ConversationSummaryMemory(
            llm=self.init_ollama_model(),
            chat_memory=self.init_upstash(),
            return_messages=True,
        )
        print('Here is memory: ')
        return memory

    def init_ollama_model(self):
        llm = Ollama(model='llama3.1')
        return llm