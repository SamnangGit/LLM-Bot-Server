from typing import List, Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from tools.report_writer_tool import ResearchReportWriter

load_dotenv()

class ReportAgent:
    """Agent for handling research report writing operations"""
    
    def __init__(self):
        self.report_tool = ResearchReportWriter()
        self.tools = [
            Tool(
                name="write_research_report",
                func=self.report_tool.write_file,
                description="""Write a research report to a file. Parameters:
                - content: Main content of the research report (required)
                - filename: Name for the report file (required)
                - title: Report title (optional)
                - author: Author name (optional)
                - keywords: List of keywords (optional)
                - references: List of references (optional)
                File will be automatically formatted and sanitized."""
            ),
            Tool(
                name="sanitize_content",
                func=self.report_tool.content_sanitizer,
                description="""Sanitize and format research content.
                Takes raw content string and returns cleaned, properly formatted content.
                Use this before writing if content needs pre-processing."""
            )
        ]
        
        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7
        )
    
    def init_report_agent(self):
        """Initialize the report writing agent with specific instructions"""
        report_agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier="""You are a research report writing assistant that helps with creating and formatting research reports.

    When asked to create a report:
    1. IMMEDIATELY use write_research_report with the provided content and parameters
    2. DO NOT modify or rewrite the content unless explicitly asked
    3. Use the default .md extension if no specific format is requested
    4. Report success/failure to the user

    For content sanitization:
    1. Only use sanitize_content when explicitly asked to clean up content
    2. Return the sanitized content to the user if they want to review it
    3. If writing a report with sanitized content, pass the sanitized version to write_research_report

    IMPORTANT GUIDELINES:
    - When given content to save as a report, use write_research_report IMMEDIATELY
    - Don't try to improve or modify the content without explicit request
    - Keep metadata (title, author, etc.) as provided by the user
    - Use sensible defaults for optional parameters if not specified
    - Always confirm successful report creation with the filename used

    Example usage:
    User: "Save this research summary: [content] as my-research.md"
    Action: Immediately use write_research_report with the content and filename

    User: "Clean up this text: [content]"
    Action: Use sanitize_content and return the cleaned version"""
        )
        return report_agent