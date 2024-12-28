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
from typing import AsyncGenerator


from tools.online_search_tool import OnlineSearchTool
from tools.file_ops_tool import FileOpsTool
from tools.web_scrapping_tool import WebScrapingTool
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_tool_calling_agent

from langsmith import Client

from rag.vector_stores.milvus_db import MilvusStore

# Auto-trace LLM calls in-context
client = Client(api_key=os.getenv("LANGSMITH_API_KEY"),
                api_url=os.getenv("LANGCHAIN_ENDPOINT"),
                )

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
                                    #   callbacks=[callback_handler]
                                    #   verbose=True,
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
                        temperature=temperature, streaming=True)
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
                             temperature=temperature, top_p=top_p, top_k=top_k, streaming=True)
        # , streaming=True
        return llm
    
    def ollama_platform(self, model_code, temperature, top_p, top_k):
        llm = Ollama(model=model_code, temperature=temperature)
        return llm
        


    def start_chat(self, model: str, message: Message, temperature: str, top_p: str, top_k: str):
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        if model_code and platform:
            self.chat = getattr(self, platform)(model_code, temperature, top_p, top_k)
            response = self.chat.invoke(message)
            # print(strresponse))
        return str(response)

    def start_custom_chat(self, model, message: Message, temperature, top_p, top_k, uuid):
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        if model_code and platform:
            print(f"Temperature: {temperature}, Top P: {top_p}, Top K: {top_k}")
            llm = getattr(self, platform)(model_code, temperature, top_p, top_k)
            print(llm)
            self.chat = ConversationChain(llm=llm, memory=self.memory_util.init_buffer_window_memory(uuid)
        )
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
    

    def start_chat_with_tool(self, model, message: Message, temperature, top_p, top_k, uuid="12345678111"):
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)

        search_tools = OnlineSearchTool().get_tools()
        file_tools = FileOpsTool().get_tools()
        scrape_tools = WebScrapingTool.get_tools()
        tools = []
        tools.extend(search_tools)
        tools.extend(file_tools)
        tools.extend(scrape_tools)

        prompt = ChatPromptTemplate(
            messages = [
                SystemMessagePromptTemplate(prompt=PromptTemplate(template='You are a helpful assistant')),
                MessagesPlaceholder(variable_name='chat_history', optional=True),
                HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}')),
                MessagesPlaceholder(variable_name='agent_scratchpad')
            ]
        )
        print("==========================================================")
        print(prompt)
        print("==========================================================")

        memory = self.memory_util.init_buffer_window_memory(uuid)
        if model_code and platform:
            print(f"Temperature: {temperature}, Top P: {top_p}, Top K: {top_k}")
            llm = getattr(self, platform)(model_code, temperature, top_p, top_k)
            # llm = ChatGroq(model="llama-3.1-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
            # self.chat = ConversationChain(llm=llm, memory=self.memory_util.init_buffer_window_memory(uuid)
            agent = create_tool_calling_agent(llm, tools, prompt)
            self.chat = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
            print(f"Memory before chat start: {memory.load_memory_variables({})}")
        else:
            return {"error": "Model not found"}, 400

        try:
            response = self.chat.invoke({"input": message})
        except Exception as e:
            return {"error": str(e)}
        # finally:
            # print(type(response))
            # history.add_message(conte)

        return response, platform, model_code
    

    def start_chat_with_doc(self, model, message: Message, temperature, top_p, top_k, uuid):
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        if model_code and platform:
            llm = getattr(self, platform)(model_code, temperature, top_p, top_k)
            # self.chat = ConversationChain(llm=llm, memory=self.memory_util.init_buffer_window_memory(uuid))
        else:
            return {"error": "Model not found"}, 400
        try:
            milvus = MilvusStore()
            context = milvus.document_retriever(query=str(message))

            prompt_template = """
                Please answer the following question:
                <question>
                {message}
                </question>
                Based on this following context:
                <context>
                {context}
                </context>
            """


            prompt = prompt_template.format(message=message, context=context)
            print("============================")
            print(prompt)
            print("============================")
            response = llm.invoke(prompt)
        except Exception as e:
            return {"error": str(e)}

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
        llm = getattr(self, platform)(model_code, temperature, top_p, top_k)

        # Initialize the agent with the loaded LLM and memory
        agent = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            tools=[],
            llm=llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
            memory=self.memory_util.init_buffer_window_memory("aaaaaa"),
            return_intermediate_steps=False
        )

        # print("Agent initialized: " + str(agent))

        # Define the asynchronous callback handler
        class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
            content: str = ""
            final_answer: bool = False

            async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
                self.content += token
                if self.final_answer:
                    if '"action_input": "' in self.content:
                        if token not in ['"', "}"]:
                            await self.queue.put(token)
                elif "Final Answer" in self.content:
                    self.final_answer = True
                    self.content = ""

            async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
                if self.final_answer:
                    self.content = ""
                    self.final_answer = False
                    await self.queue.put(None)  # Signal the end of the stream
                else:
                    self.content = ""

        # Define the function to run the agent call asynchronously
        async def run_call(message: str, stream_it: AsyncCallbackHandler):
            # print("Starting agent call...")
            agent.agent.llm_chain.llm.callbacks = [stream_it]
            try:
                result = await agent.acall(inputs={"input": message})
                # print("Agent call completed:", result)
            except Exception as e:
                print("Error in agent call:", e)
                raise

        # Define the generator function to stream the response tokens
        async def create_gen(message: str, stream_it: AsyncCallbackHandler):
            print("Message: " + str(message))
            task = asyncio.create_task(run_call(message, stream_it))
            print("Task created: " + str(task))

            async for token in stream_it.aiter():
                print("Token: " + str(token))
                yield token

            await task


        # Initialize the callback handler and return the generator
        stream_it = AsyncCallbackHandler()
        # return await create_gen(message, stream_it)   
        return create_gen(message, stream_it)
        


    async def start_chat_stream_memory_es(self, model: str, message: str, temperature: float, top_p: float, top_k: int, callback_handler) -> AsyncGenerator[str, None]:
        model_code, platform = self.platform_utils.load_yaml_and_get_model(model)
        llm = getattr(self, platform)(model_code, temperature, top_p, top_k, callback_handler)
        self.chat = ConversationChain(llm=llm, memory=self.memory_util.init_buffer_window_memory("ccccccc"))

        run = asyncio.create_task(self.chat.ainvoke(input=message))
        print("Messae: " + str(message))
        print("Run: " + str(run))
        print("Callback Handler: " + str(callback_handler.aiter()))
        async for token in callback_handler.aiter():
            print("Token: " + str(token))
            yield token
        await run

