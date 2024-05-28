from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from configs.config import safety_settings, generation_settings
from schemas.chat import Message
import os
from dotenv import load_dotenv

load_dotenv()

class GenerativeModel:
    def __init__(self):
        self.chat = self.gemini_model()
        # self.chat = self.openai_model()



    def gemini_model(self):
        chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", 
                                      google_api_key=os.getenv("GEMINI_API_KEY"),
                                      safety_settings=safety_settings,
                                      temperature=generation_settings['temperature'])    
        return chat    

    def openai_model(self):
        template = """Question: {question}

        Answer: Let's think step by step."""

        prompt = PromptTemplate.from_template(template)
            
        llm = OpenAI(model="gpt-3.5-turbo-instruct", openai_api_key=os.getenv("OPENAI_API_KEY"))
        llm_chain = prompt | llm

        return llm_chain


    def start_chat(self, message: Message):
        response = self.chat.invoke(message)
        return response

    # gemini-1.5-flash-latest