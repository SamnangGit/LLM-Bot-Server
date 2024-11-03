import requests
import os
from dotenv import load_dotenv

from langchain_core.tools import tool
from tavily import TavilyClient
from duckduckgo_search import DDGS
import wikipedia
from exa_py import Exa

from typing import List, Dict, Literal

load_dotenv()

class OnlineSearchTool:
    """Wrapper class for various online search tools."""
    
    def __init__(self):
        pass
    
    @staticmethod
    @tool
    def google_search(query: str):
        """
        Perform a search using the Google Custom Search API.

        Args:
            query (str): The search query string.
            num_results (int, optional): Number of search results to return (max 10). Defaults to 10.

        Returns:
            list: A list of search results, where each result is a dictionary.
        """
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': query,
            'num': 3
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            search_results = response.json().get('items', [])
            return search_results
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None


    @staticmethod
    @tool
    def ddg_search(query: str) -> List[Dict]:
        """DuckDuckGo Search - Get relevant search results from DuckDuckGo.

        Args:
            query (str): The search query to be executed

        Returns:
            List[Dict]: List of search results with metadata
        """
        try:
            results = DDGS().text(query, max_results=5)
            return results
        except Exception as e:
            return [{"error": f"DuckDuckGo search failed: {str(e)}"}]

    @staticmethod
    @tool
    def tavily_search(
                     query: str, 
                     search_depth: Literal["basic", "advanced"] = "basic",
                     include_images: bool = False,
                     include_domains: List[str] = None,
                     exclude_domains: List[str] = None) -> List[Dict]:
        """Tavily Search - Get AI-optimized search results from Tavily.

        Args:
            query (str): The search query to be executed
            search_depth (str): 'basic' or 'advanced' search (default: 'basic')
            include_images (bool): Whether to include images in results (default: False)
            include_domains (List[str]): Specific domains to include in search
            exclude_domains (List[str]): Domains to exclude from search

        Returns:
            List[Dict]: List of search results with metadata
        """

        tavily_api_key = os.getenv('TAVILY_API_KEY')
        
        tavily_client = TavilyClient(api_key=tavily_api_key)

        try:
            response = tavily_client.search(
                query=query,
                search_depth=search_depth,
                include_images=include_images,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                max_results=10
            )
            return response.get('results', [])
        except Exception as e:
            return [{"error": f"Tavily search failed: {str(e)}"}]
        
    @staticmethod
    @tool
    def you_search(query: str):
        """You.com Search - Perform a search query using the You.com API.

        Args:
            query (str): The search query to be executed.

        Returns:
            dict: The JSON response from You.com API with search results.
        """

        you_api_key = os.getenv('YOU_API_KEY')
        headers = {"X-API-Key": you_api_key}
        params = {"query": query}
        try:
            response = requests.get(
                "https://api.ydc-index.io/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()  
            return response.json()
        except requests.RequestException as e:
            return {"error": f"You.com search failed: {str(e)}"}
        
    @staticmethod
    @tool
    def exa_search(query):
        """
        Performs a search using the Exa API.

        This function interfaces with the Exa API to perform a search based on the provided query. It retrieves 
        up to 5 results from specified domains and returns relevant search information. The search results 
        are limited to articles published after June 12, 2023, from "nytimes.com" and "wsj.com" domains.

        Parameters:
            query (str): The search term or query string to use with the Exa API.

        Returns:
            dict: A dictionary containing the search results if successful, or an error message if the search fails.

        Raises:
            Exception: If there is an error with the Exa API call, it returns a dictionary with the error message.
            
        Example:
            >>> exa_search("latest economic news")
            {'results': [...]}
        """
        exa_api_key = os.getenv('EXA_API_KEY')
        try:
            exa = Exa(api_key=exa_api_key)
            result = exa.search(query,
                num_results=5,
                include_domains=["nytimes.com", "wsj.com"],
                start_published_date="2023-06-12"
            )
            return result
        except Exception as e:
            return {"error": f"Exa search failed: {str(e)}"}

        
    @staticmethod
    @tool
    def wikipedia_search(query):
        """
        Performs a search using the Wikipedia API.

        This function conducts a search on Wikipedia based on the provided query and returns a list of relevant 
        Wikipedia article titles. It provides basic error handling and returns an error message if the search fails.

        Parameters:
            query (str): The search term or query string to search on Wikipedia.

        Returns:
            list: A list of Wikipedia article titles relevant to the query, or an error message if the search fails.

        Raises:
            Exception: If there is an error with the Wikipedia API call, it returns a dictionary with the error message.

        Example:
            >>> wikipedia_search("Quantum Mechanics")
            ["Quantum mechanics", "Introduction to quantum mechanics", "Quantum field theory", ...]
        """
        try:
            result = wikipedia.search(query)
            return result
        except Exception as e:
            return [{"error": f"wikipedia search failed: {str(e)}"}]


    def get_tools(self, include: List[str] = None) -> List[tool]:
        """
        Get list of search tools to pass to LLM.

        Args:
            include (List[str]): List of tools to include. Options: ['google', 'ddg', 'tavily', 'exa','you', 'wikipedia']
                               If None, returns all available tools.

        Returns:
            List[tool]: List of tool functions to pass to LLM
        """
        search_tools = {
            'google': self.google_search,
            'ddg': self.ddg_search,
            'tavily': self.tavily_search,
            'exa': self.exa_search,
            'you': self.you_search,
            'wikipedia': self.wikipedia_search
        }
        
        if include:
            return [search_tools[name] for name in include if name in search_tools]
        return list(search_tools.values())
    

    
