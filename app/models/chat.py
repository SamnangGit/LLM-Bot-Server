from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import DeepInfra
from langchain_anthropic import ChatAnthropic

from langchain.prompts import PromptTemplate

from transformers import AutoTokenizer

from configs.config import safety_settings, generation_settings
from schemas.chat import Message
import os
from dotenv import load_dotenv

import yaml
from yaml import SafeLoader

load_dotenv()

class GenerativeModel:

    def __init__(self):
        self.chat = None

    def load_yaml_and_get_model(self, model_name):
        with open('../app/configs/llm_platform.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        model_code, parent = self.get_model_code_and_parent(model_name, data)

        return model_code, parent

    def get_model_code_and_parent(self, model_name, data):
        for parent, models in data.items():
            for model in models:
                if model_name in model:
                    return model[model_name], parent
        return None, None


    def gemini_model(self, model_code, temperature):
        llm = ChatGoogleGenerativeAI(model=model_code, 
                                      google_api_key=os.getenv("GEMINI_API_KEY"),
                                      safety_settings=safety_settings,
                                      temperature=temperature,
                                      top_p=generation_settings['top_p'],
                                      top_k=generation_settings['top_k'],
                                      stream=False)    
        return llm  

    def openai_model(self, model_code, temperature):
        template = """Question: {question}

        Answer: Let's think step by step."""

        prompt = PromptTemplate.from_template(template)
            
        # llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"),
        #              temperature=generation_settings['temperature'],
        #              top_p=generation_settings['top_p'],
        #             streaming=False)

        llm = OpenAI(model=model_code, openai_api_key=os.getenv("OPENAI_API_KEY"),
                     temperature=temperature)
        llm_chain = prompt | llm

        return llm_chain
    

    def groq_model(self, model_code, temperature=0.5):
        llm = ChatGroq(model=model_code, api_key=os.getenv("GROQ_API_KEY"),
                        temperature=temperature)
        print(f"Model: {model_code}, Temperature: {temperature}")
        return llm
    

    def deepinfra_model(self, model_code, temperature):
        llm = DeepInfra(model_id=model_code, deepinfra_api_token=os.getenv("DEEPINFRA_API_TOKEN"),
                        model_kwargs = {"temperature": temperature, 
                                        "top_p": generation_settings['top_p'],
                                        # "top_k": generation_settings['top_k'],
                                        "repetition_penalty": 1.2})
        return llm
    

    def anthropic_model(self, model_code):
        llm = ChatAnthropic(model_name=model_code, api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=generation_settings['temperature'])
        return llm

    def start_chat(self, message: Message):
        response = self.chat.invoke(message)
        return response

    def start_custom_chat(self, model, message: Message,  temperature, top_p, top_k):
        # print(f"Model: {model}, Temperature: {temperature}, Top P: {top_p}, Top K: {top_k}")
        model_code, parent = self.load_yaml_and_get_model(model)
        if model_code and parent:
            # print(f"Model Code: {model_code}, Parent: {parent}")
            parent = parent.replace('(self)', '').strip()
            # print(f"Model Code: {model_code}, Parent: {parent}")
            self.chat = getattr(self, parent)(model_code, temperature)
        else:
            return {"error": "Model not found"}, 400
        try:
            response = self.chat.invoke(message)
        except Exception as e:
            return {"error": str(e)}   

        try:
             format_response = self.standardize_response(model_code, parent, response)
        except Exception as e:
            return {"error": str(e)}     
        return format_response
    

    def standardize_response(self, model_code, parent, response):
        # print(f"Parent in standard: {parent}")
        # print(f"Response: {response}")
        if parent == "groq_model":
            standardized_response = {
                "content": response.content,
                "response_metadata": {
                    "token_usage": {
                        "completion_tokens": response.response_metadata['token_usage']['completion_tokens'],
                        "prompt_tokens": response.response_metadata['token_usage']['prompt_tokens'],
                        "total_tokens": response.response_metadata['token_usage']['total_tokens']
                    },
                    "model_name": model_code,
                }
            }
            return standardized_response
        elif parent == "deepinfra_model":
                standardized_response = {
                    "content": response,
                    "count": self.count_tokens(response, model_code),
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
        elif parent == "anthropic_model":
            response = response['response']
        elif parent == "openai_model":
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
        elif parent == "gemini_model":
                standardized_response = {
                    "content": response.content,
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


    def count_tokens(self, response_text, model_code):
        tokenizer = AutoTokenizer.from_pretrained(model_code)  

        # input_tokens = tokenizer.tokenize(input_text)
        output_tokens = tokenizer.tokenize(response_text)

        return {
            # "input_tokens": len(input_tokens),
            "output_tokens": len(output_tokens),
            # "total_tokens": len(input_tokens) + len(output_tokens)
        }