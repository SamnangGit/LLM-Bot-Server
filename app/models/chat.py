from langchain_google_genai import ChatGoogleGenerativeAI
from configs.config import safety_settings, generation_settings
from schemas.chat import Message
import os
from dotenv import load_dotenv

load_dotenv()

class GenerativeModel:
    def __init__(self):
        chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", 
                                      google_api_key=os.getenv("GEMINI_API_KEY"),
                                      safety_settings=safety_settings,
                                      temperature=generation_settings['temperature'])
        self.chat = chat


    def start_chat(self, message: Message):
        response = self.chat.invoke(message)
        return response

    # gemini-1.5-flash-latest