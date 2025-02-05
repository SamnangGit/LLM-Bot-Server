from typing import List, Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_community.utilities import SQLDatabase
from tools.sql_tool import SQLDatabaseTool


class SQLAgent:
    """SQL Agent class for managing LLM interactions with SQL database"""
    
    def __init__(self):

        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0
        )
                
        self.tools = [
            Tool(
                name="get_schema",
                func=SQLDatabaseTool.get_schema,
                description="Get database schema information"
            ),
            Tool(
                name="execute_sql",
                func=SQLDatabaseTool.execute_sql,
                description="Execute SQL query and return results. Takes SQL query string as input."
            )
        ]
        


    
    def init_sql_agent(self):
        """
        Initialize the SQL agent with ReAct framework
        
        Returns:
            Agent: Initialized ReAct agent
        """
        sql_agent = create_react_agent(
            self.llm,
            tools=self.tools,
            state_modifier="""You are a SQL database assistant that helps with querying and analyzing data.
            For each request:
            1. Get schema if needed using get_schema tool
            2. Generate appropriate SQL query based on the schema
            3. Execute query using execute_sql tool
            4. Explain results in natural language
            
            Be precise with SQL syntax and always verify queries before execution.
            For complex queries, break them down into steps."""
        )
        return sql_agent