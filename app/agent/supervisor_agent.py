from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from agent.sub_agent.research_agent import ResearchAgent
from agent.sub_agent.file_agent import FileAgent
from agent.sub_agent.sql_agent import SQLAgent
from agent.sub_agent.web_client_agent import WebClientAgent
from agent.sub_agent.report_writer_agent import ReportAgent
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_anthropic import ChatAnthropic




sub_agents = ['research_agent', 'sql_agent', 'web_client_agent', 'report_writer_agent', 'file_agent']
options = sub_agents + ["FINISH"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {sub_agents}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*options] # type: ignore


class State(TypedDict):
    messages: Annotated[list[str], add_messages]
    # next_agent: str

class SupervisorAgent:
    def __init__(self, agent_name: str, agent_description: str):
        self.agent_name = agent_name
        self.agent_description = agent_description
        load_dotenv()
        # self.llm = ChatGroq(
        #     model="llama-3.1-70b-versatile", 
        #     api_key=os.getenv("GROQ_API_KEY")
        # )
        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7
        )
        
    
    def supervisor_node(self, state: State) -> Command[Literal['research_agent, sql_agent, web_client_agent, report_writer_agent, file_agent', "__end__"]]:
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = self.llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto)
    

    def research_node(self, state: State) -> Command[Literal["supervisor"]]:
        agent = ResearchAgent()
        research_agent = agent.init_search_agent()
        result = research_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="research_agent")
                ]
            },
            goto="supervisor",
        )
    
    def file_node(self, state: State) -> Command[Literal["supervisor"]]:
        agent = FileAgent()
        file_agent = agent.init_file_agent()
        result = file_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="file_agent")
                ]
            },
            goto="supervisor",
        )
    
    def sql_node(self, state: State) -> Command[Literal["supervisor"]]:
        agent = SQLAgent()
        sql_agent = agent.init_sql_agent()
        result = sql_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="sql_agent")
                ]
            },
            goto="supervisor",
        )
    
    def web_client_node(self, state: State) -> Command[Literal["supervisor"]]:
        agent = WebClientAgent()
        web_client_agent = agent.init_web_client_agent()
        result = web_client_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="web_client_agent")
                ]
            },
            goto="supervisor",
        )
    
    def report_writer_node(self, state: State) -> Command[Literal["supervisor"]]:
        agent = ReportAgent()
        report_writer_agent = agent.init_report_agent()
        result = report_writer_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="report_writer_agent")
                ]
            },
            goto="supervisor",
        )



    def init_graph(self):
        builder = StateGraph(State)
        
        builder.add_edge(START, "supervisor")
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("research_agent", self.research_node)
        builder.add_node("file_agent", self.file_node)
        builder.add_node("sql_agent", self.sql_node)
        builder.add_node("web_client_agent", self.web_client_node)
        builder.add_node("report_writer_agent", self.report_writer_node)
        graph = builder.compile()
        # print(graph.get_graph().draw_mermaid())
        return graph.invoke({"messages": [("user", "Research about benefit of using LangChain over CrewAI. After research use report writer agent to save the result in report format as a file")]}, subgraphs=True, debug=True)
    


