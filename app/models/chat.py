from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import DeepInfra
from langchain_anthropic import ChatAnthropic

from langchain.prompts import PromptTemplate

from configs.config import safety_settings, generation_settings
from schemas.chat import Message
import os
from dotenv import load_dotenv

load_dotenv()

class GenerativeModel:
    def __init__(self):
        self.chat = self.gemini_model()
        # self.chat = self.openai_model()
        # self.chat = self.qroq_model()
        # self.chat = self.deepinfra_model()
        # self.chat = self.anthropic_model()



    def gemini_model(self):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", 
                                      google_api_key=os.getenv("GEMINI_API_KEY"),
                                      safety_settings=safety_settings,
                                      temperature=generation_settings['temperature'])    
        return llm  

    def openai_model(self):
        template = """Question: {question}

        Answer: Let's think step by step."""

        prompt = PromptTemplate.from_template(template)
            
        llm = OpenAI(model="gpt-3.5-turbo-instruct", openai_api_key=os.getenv("OPENAI_API_KEY"))
        llm_chain = prompt | llm

        return llm_chain
    

    def qroq_model(self):
        llm = ChatGroq(model="mixtral-8x7b-32768", api_key=os.getenv("GROQ_API_KEY"), temperature=generation_settings['temperature'])
        return llm
    

    def deepinfra_model(self):
        llm = DeepInfra(model_id="meta-llama/Llama-2-70b-chat-hf", deepinfra_api_token=os.getenv("DEEPINFRA_API_TOKEN"),
                        model_kwargs = {"temperature": generation_settings['temperature'], 
                                        "top_p": generation_settings['top_p'],
                                        "repetition_penalty": 1.2})
        return llm
    

    def anthropic_model(self):
        llm = ChatAnthropic(model_name="claude-3-haiku-20240307", api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=generation_settings['temperature'])
        return llm

    def start_chat(self, message: Message):
        response = self.chat.invoke(message)
        return response

