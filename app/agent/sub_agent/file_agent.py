from typing import List, Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from tools.file_ops_tool import FileOpsTool

load_dotenv()

class FileAgent:
    def __init__(self):
        self.file_tool = FileOpsTool()
        self.tools = [
            Tool(
                name="write_file",
                func=self.file_tool.write_file,
                description="Write content to a file. Takes a dictionary with 'content' containing the data and optional 'filename'",
            ),
            Tool(
                name="read_file",
                func=self.file_tool.read_file,
                description="Read content from files. Takes query_type ('latest', 'by_name', 'search', 'all'), optional value, and max_results",
            ),
            # Tool(
            #     name="write_html",
            #     func=self.file_tool.write_html,
            #     description="""Write HTML content to a file. Expects:
            #         - content (dict): Dictionary with:
            #             - title: Page title (required)
            #             - body: HTML body content (required)
            #             - styles: CSS styles (optional)
            #             - scripts: JavaScript code (optional)
            #         - filename (optional): Name for the HTML file""",
            # )
        ]
        
        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7
        )

    def init_file_agent(self):
        file_agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier="""You are a file management assistant that helps with reading and writing files.
            When asked to save content to a file, IMMEDIATELY use the write_file tool with the content.
            DO NOT make additional API calls or try to modify the content.
            
            For write_file:
            1. Take the exact content provided
            2. Call write_file immediately
            3. Report success/failure to the user
            
            For read_file:
            1. Use appropriate query_type ('latest', 'by_name', 'search', 'all')
            2. Provide value if searching
            3. Return results to user
            
            IMPORTANT: When given content to save, use write_file IMMEDIATELY without additional processing."""
        )
        return file_agent
