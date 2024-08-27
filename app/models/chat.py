import asyncio
import ssl
import os
from dotenv import load_dotenv
from typing import AsyncIterable

from configs.config import safety_settings, generation_settings
from schemas.chat import Message

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import DeepInfra, Ollama
from langchain_anthropic import ChatAnthropic

from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.callbacks import AsyncIteratorCallbackHandler

from utils.platform_util import PlatformUtils
from utils.memory_util import MemoryUtils
from utils.session_util import SessionUtils


from typing import Any
from queue import Queue
from langchain.agents import AgentType, initialize_agent
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain.schema import LLMResult


ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv()

class GenerativeModel:

    def __init__(self):
        self.platform_utils = PlatformUtils()
        self.memory_util = MemoryUtils()
        self.chat = None
        # self.memory = self.memory_util.init_buffer_window_memory(uuid)

    def gemini_platform(self, model_code, temperature, top_p, top_k):
        llm = ChatGoogleGenerativeAI(model=model_code, 
                                      google_api_key=os.getenv("GEMINI_API_KEY"),
                                      safety_settings=safety_settings,
                                      temperature=temperature,
                                      top_p=top_p,
                                      top_k=top_k,
                                      streaming=True,
                                      verbose=True,
                                      )    
        return llm  

    def openai_platform(self, model_code, temperature, top_p, top_k):
        template = """Question: {question}
        Answer: Let's think step by step."""
        prompt = PromptTemplate.from_template(template)
        llm = OpenAI(model=model_code, openai_api_key=os.getenv("OPENAI_API_KEY"),
                     temperature=temperature, top_p=top_p, streaming=True)
        llm_chain = prompt | llm
        return llm_chain
    

    def groq_platform(self, model_code, temperature, top_p, top_k):
        print(f"temperature: {temperature}")
        llm = ChatGroq(model=model_code, api_key=os.getenv("GROQ_API_KEY"),
                        temperature=temperature)
        print(f"Model: {model_code}, Temperature: {temperature}")
        # stream=True
        return llm
    

    def deepinfra_platform(self, model_code, temperature, top_p, top_k):
        llm = DeepInfra(model_id=model_code, deepinfra_api_token=os.getenv("DEEPINFRA_API_TOKEN"),
                        model_kwargs = {"temperature": temperature, 
                                        "top_p": top_p,
                                        "repetition_penalty": 1.2})
        return llm
    

    def anthropic_platform(self, model_code, temperature, top_p, top_k):
        llm = ChatAnthropic(model_name=model_code, api_key=os.getenv("ANTHROPIC_API_KEY"),
                             temperature=temperature, top_p=top_p, top_k=top_k)
        # , streaming=True
        return llm
    
    def ollama_platform(self, model_code, temperature, top_p, top_k):
        llm = Ollama(model=model_code, temperature=temperature)
        return llm
        


    def start_chat(self, message: Message):
        response = self.chat.invoke(message)
        return response

    def start_custom_chat(self, model, message: Message, temperature, top_p, top_k, uuid):
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        if model_code and platform:
            print(f"Temperature: {temperature}, Top P: {top_p}, Top K: {top_k}")
            llm = getattr(self, platform)(model_code, temperature, top_p, top_k)
            self.chat = ConversationChain(llm=llm, memory=self.memory_util.init_buffer_window_memory(uuid)
        )
            print('Memory: ')
            # print(self.memory.load_memory_variables({}))
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
        ai_msg = "";
        stream = self.chat.astream(message)

        try:
            async for chunk in stream:
                yield chunk.content
                ai_msg += chunk.content
        except Exception as e:
            print(f"Caught exception: {e}")
        finally:
            print(f"AI Message: {ai_msg}")
            print("Stream completed")


    async def start_chat_stream_memory(self, model: str, message: str, temperature: float, top_p: float, top_k: int) -> Any:
        # Load model configuration and initialize LLM
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        llm = getattr(self, platform)(model_code, temperature)

        # Initialize the agent with the loaded LLM and memory
        agent = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            tools=[],
            llm=llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            memory=self.memory,
            return_intermediate_steps=False
        )

        # Define the asynchronous callback handler
        class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
            content: str = ""
            final_answer: bool = False

            def __init__(self):
                super().__init__()

            async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
                self.content += token
                if self.final_answer:
                    if '"action_input": "' in self.content:
                        if token not in ['"', "}"]:
                            self.queue.put_nowait(token)
                elif "Final Answer" in self.content:
                    self.final_answer = True
                    self.content = ""

            async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
                if self.final_answer:
                    self.content = ""
                    self.final_answer = False
                    self.done.set()
                else:
                    self.content = ""

        # Define the function to run the agent call asynchronously
        async def run_call(message: str, stream_it: AsyncCallbackHandler):
            # Assign callback handler to the agent's LLM
            agent.agent.llm_chain.llm.callbacks = [stream_it]
            await agent.acall(inputs={"input": message})

        # Define the generator function to stream the response tokens
        async def create_gen(message: str, stream_it: AsyncCallbackHandler):
            task = asyncio.create_task(run_call(message, stream_it))
            async for token in stream_it.aiter():
                yield token
            await task


        # Initialize the callback handler and return the generator
        # stream_it = AsyncCallbackHandler()
        # return await create_gen(message, stream_it)   
        create_gen(message, AsyncCallbackHandler())
        


    async def start_chat_stream_memory_es(self, model: str, message: str, temperature: float, top_p: float, top_k: int):
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        llm = getattr(self, platform)(model_code, temperature)
        self.chat = ConversationChain(llm=llm, memory=self.memory)
        callback_handler = FinalStreamingStdOutCallbackHandler()


        callback_handler = AsyncIteratorCallbackHandler()

        run = asyncio.create_task(self.chat.arun(input=message))
        async for token in callback_handler.aiter():
            yield token
        await run