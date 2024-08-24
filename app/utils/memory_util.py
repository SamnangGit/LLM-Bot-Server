import os
from dotenv import load_dotenv
from datetime import datetime


from langchain_community.chat_message_histories import (
    UpstashRedisChatMessageHistory, RedisChatMessageHistory
)
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationTokenBufferMemory, ConversationSummaryMemory, ConversationSummaryBufferMemory
from langchain_community.llms import Ollama

from utils.session_util import SessionUtils

load_dotenv()

class MemoryUtils:
        
    def init_upstash(self):
        upstash_redis_url = os.getenv("UPSTASH_REDIS_URL")
        upstash_redis_token = os.getenv("UPSTASH_REDIS_TOKEN")


        history = UpstashRedisChatMessageHistory(
            url=upstash_redis_url, token=upstash_redis_token, ttl=0, session_id=SessionUtils.generate_session_id()
        )
        return history    


    def init_redis(self):
        redis_url = os.getenv("REDIS_URL")
        history = RedisChatMessageHistory(url=redis_url, ttl=0, session_id=self.generate_session_id)
        return history


    # def generate_session_id(self):
    #     date = datetime.now()
    #     timestamp = date.strftime("%Y%m%d")
    #     sequence = str(date.hour * 3600 + date.minute * 60 + date.second).zfill(5)
    #     return f"{timestamp}-{sequence}"
    

    def init_buffer_memory(self):
        memory = ConversationBufferMemory(
            chat_memory=self.init_upstash(),
            return_messages=True,
        )
        return memory
    
    def init_buffer_window_memory(self):
        memory = ConversationBufferWindowMemory(
            chat_memory=self.init_upstash(),
            k=1,
            return_messages=True,
        )
        return memory
    
    # seems like there is an error of max_token_limit in ollama
    def init_token_buffer_memory(self):
        memory = ConversationTokenBufferMemory(
            llm=self.init_ollama(),
            chat_memory=self.init_upstash(),
            max_token_limit=25,
            return_messages=False,
        )
        return memory
    
    def init_summary_memory(self):
        memory = ConversationSummaryMemory(
            llm=self.init_ollama(),
            chat_memory=self.init_upstash(),
            return_messages=True,
        )
        print('Here is memory: ')
        return memory
    
    def init_summary_buffer_memory(self):
        memory = ConversationSummaryBufferMemory(
            llm=self.init_ollama(),
            chat_memory=self.init_upstash(),
            max_token_limit=100,
            return_messages=True,
        )
        return memory

    def init_ollama(self):
        llm = Ollama(model='llama3.1')
        return llm
    
