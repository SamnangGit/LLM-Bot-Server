from typing import List, Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from tools.web_client_tool import WebClientTool

load_dotenv()

class WebClientAgent:
    """Agent class for handling web client operations using WebClientTool"""
    
    def __init__(self):
        self.web_tool = WebClientTool()
        self.tools = [
            Tool(
                name="generate_html",
                func=self.web_tool.generate_html,
                description="Generate HTML content. Takes a dictionary with 'title' (required), 'body' (required), optional 'styles' and 'scripts'"
            )
        ]
        
        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7
        )
    
    def init_web_client_agent(self):
        """Initialize and return the web client agent with specific instructions"""
        web_agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier="""You are a web content generation assistant that helps create HTML pages.
            When asked to generate HTML content:
            1. IMMEDIATELY use the generate_html tool with the provided specifications
            2. DO NOT modify or process the content beyond organizing it into the required structure
            3. Required fields are 'title' and 'body'
            4. Optional fields are 'styles' and 'scripts'
            5. Report success/failure to the user
            
            IMPORTANT: When given content to generate:
            - Organize it into the correct dictionary structure
            - Call generate_html IMMEDIATELY
            - Do not attempt to modify or enhance the content
            - Return the generated HTML or error message to the user"""
        )
        return web_agent