import asyncio
import ssl
from typing import AsyncIterable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import DeepInfra, Ollama
from langchain_anthropic import ChatAnthropic

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
        self.memory = ConversationBufferMemory()

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
                print(f"Response: {response}")
            except Exception as e:
                return {"error": str(e)}

            return response, platform, model_code
    

    async def start_chat_stream(self, model: str, message, temperature: float, top_p: float, top_k: int) -> AsyncIterable[str]:
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        self.chat = getattr(self, platform)(model_code, temperature)
        print(self.chat)
        print(f"Model: {model_code}, Platform: {platform}")
        
        stream = self.chat.astream(message)

        try:
            async for chunk in stream:
                yield chunk.content
                # yield chunk
                # print(f"Yielding chunk: {chunk.content}")
        except Exception as e:
            print(f"Caught exception: {e}")
        finally:
            print("Stream completed")

# Not working, error with hugging face tokenization
    # def count_tokens(self, response_text, model_code):
    #     tokenizer = AutoTokenizer.from_pretrained(model_code)  

    #     # input_tokens = tokenizer.tokenize(input_text)
    #     output_tokens = tokenizer.tokenize(response_text)

    #     return {
    #         # "input_tokens": len(input_tokens),
    #         "output_tokens": len(output_tokens),
    #         # "total_tokens": len(input_tokens) + len(output_tokens)
    #     }