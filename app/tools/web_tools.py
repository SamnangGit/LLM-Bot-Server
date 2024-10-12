from langchain.tools import BaseTool

from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from dotenv import load_dotenv
import os

from typing import Optional, Type
from pydantic import BaseModel, Field

import requests
from bs4 import BeautifulSoup

import cohere


load_dotenv()

class WebScraperInput(BaseModel):
    query: str = Field(..., description="The search query to use for finding the webpage to scrape")

class WebTools(BaseTool):
    name: str = "web_tool"
    description: str = "Useful for scraping main page links from any webpage found via a Google search. Use this tool when you need to find recent news or information on any topic including what is on the news website."
    args_schema: Type[BaseModel] = WebScraperInput

    def __init__(self):
        super().__init__()

    def google_search(self, query: str) -> str:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
        search = GoogleSearchAPIWrapper(google_api_key=GOOGLE_API_KEY, google_cse_id=GOOGLE_CSE_ID)
        search_result = search.results(query=query, num_results=10)
        if not search_result:
            return "No search results found."
        return self.rerank_search(query, search_result)


    def rerank_search(self, query, search_results):
        print(list(search_results))
        co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
        urls = []
        for i in range(len(search_results)):
            url = search_results[i]['link']
            urls.append(url)
        rerank_response = co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=urls
        )
        print(rerank_response)
        
        ranked_results =[]

        for i in range(len(rerank_response.results)):
            result = rerank_response.results[i]
            ranked_results.append({
                "url": urls[result.index]
            })
        print(ranked_results)
        return ranked_results
    

    def scrap_main_page_link(self, query):
        url = self.google_search(query)[0]['url']
        print(url)
        try:
            response = requests.get(url)
            response.raise_for_status()  

            soup = BeautifulSoup(response.text, 'html.parser')

            anchors = []
            for a_tag in soup.find_all('a'):
                href = a_tag.get('href') 
                text = a_tag.get_text(strip=True)
                anchors.append({"text": text, "href": href})

            return anchors
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _run(self, query: str) -> str:
            result = self.scrap_main_page_link(query)
            # print(str(result))
            return str(result)  # Convert to string for LangChain compatibility

    async def _arun(self, query: str) -> str:
        # For simplicity, we'll just call the sync version
        # In a real scenario, you'd want to make this truly asynchronous
        return self._run(query) 
