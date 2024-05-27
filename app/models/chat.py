from langchain_google_genai import ChatGoogleGenerativeAI
from configs.config import generation_config, safety_settings
from schemas.chat import Message
import os
from dotenv import load_dotenv

load_dotenv()

class GenerativeModel:
    def __init__(self):
        chat = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GEMINI_API_KEY"))
        self.chat = chat


    def start_chat(self, message_text):
        response = self.chat.invoke(message_text)
        return response

    # gemini-1.5-flash-latest