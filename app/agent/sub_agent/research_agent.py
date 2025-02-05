from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from tools.online_search_tool import OnlineSearchTool
from langgraph.prebuilt import create_react_agent
from langchain.tools import Tool
from langchain.agents import AgentExecutor
import os
from dotenv import load_dotenv

load_dotenv()

class ResearchAgent:
    def __init__(self):
        search_tool = OnlineSearchTool()
        
        # Define tools with proper schema and descriptions
        self.tools = [
            Tool(
                name="tavily_search",
                func=search_tool.tavily_search,
                description="Use this tool to search for current events and news. Input: a search query string",
                # return_direct=True
            ),
            Tool(
                name="exa_search",
                func=search_tool.exa_search,
                description="Use this tool to search recent news from major publications. Input: a search query string",
                # return_direct=True
            )
        ]
        
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7,
            max_tokens=1000
        )

    def init_search_agent(self):
        # Create the agent with more specific instructions
        research_agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier="""You are a research assistant that MUST use the provided search tools to find information.
            ALWAYS use at least one search tool before providing an answer.
            After getting search results:
            1. Analyze the information
            2. Provide a clear summary of what you found
            3. Cite the sources of your information
            
            Remember: NEVER respond without using a search tool first."""
        )
        return research_agent