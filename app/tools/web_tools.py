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

    def google_custom_search(self, query: str):
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
            'num': 10
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            search_results = response.json().get('items', [])
            return search_results
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None



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
    

    # def scrap_main_page_link(self, query):
    #     url = self.google_search(query)[0]['url']
    #     print(url)
    #     try:
    #         response = requests.get(url)
    #         response.raise_for_status()  

    #         soup = BeautifulSoup(response.text, 'html.parser')

    #         anchors = []
    #         for a_tag in soup.find_all('a'):
    #             href = a_tag.get('href') 
    #             text = a_tag.get_text(strip=True)
    #             anchors.append({"text": text, "href": href})

    #         return anchors
    #     except requests.exceptions.RequestException as e:
    #         return {"error": str(e)}

    # def _run(self, query: str) -> str:
    #         result = self.scrap_main_page_link(query)
    #         # print(str(result))
    #         return str(result)  # Convert to string for LangChain compatibility

    # async def _arun(self, query: str) -> str:
    #     # For simplicity, we'll just call the sync version
    #     # In a real scenario, you'd want to make this truly asynchronous
    #     return self._run(query) 

    
    def scrap_main_page_link(self, query):
        url = self.google_search(query)[0]['url']
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the title
            title = soup.title.string if soup.title else "No title found"
            
            # Extract main content (this is a simple approach and might need refinement)
            main_content = ""
            for paragraph in soup.find_all('p'):
                main_content += paragraph.get_text() + "\n"
            
            # Limit the content to a reasonable length
            main_content = main_content[:1000] + "..." if len(main_content) > 1000 else main_content
            
            return {
                "title": title,
                "url": url,
                "content": main_content
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        
    def scrap_main_page_content(self, query):
        """
        Scrapes comprehensive content from a webpage including headings, paragraphs,
        lists, tables, and other relevant content.
        
        Args:
            query (str): Search query to find the target webpage or direct URL
            
        Returns:
            dict: Dictionary containing various components of the webpage content
        """
        try:
            # Handle direct URL or search query
            if query.startswith(('http://', 'https://')):
                url = query
            else:
                url = self.google_search(query)[0]['url']
            
            # Set up headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Initialize session with retry strategy
            session = requests.Session()
            retries = requests.adapters.Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
            session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
            
            # Make the request
            response = session.get(url, headers=headers, timeout=30, verify=True)
            response.raise_for_status()
            
            # Parse with error handling
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                return {
                    "error": f"HTML parsing failed: {str(e)}",
                    "url": url,
                    "raw_content": response.text[:1000]
                }
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'iframe']):
                try:
                    element.decompose()
                except:
                    pass
                
            # Initialize content dictionary with default values
            content = {
                "url": url,
                "title": "No title found",
                "meta_description": "",
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "tables": [],
                "links": [],
                "images": [],
                "structured_data": {}
            }
            
            # Extract title
            try:
                content["title"] = soup.title.string if soup.title else "No title found"
            except:
                pass
                
            # Extract meta description
            try:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    content["meta_description"] = meta_desc.get('content', '')
            except:
                pass
                
            # Extract headings
            try:
                for heading_level in range(1, 7):
                    headings = soup.find_all(f'h{heading_level}')
                    content["headings"].extend([{
                        'level': heading_level,
                        'text': heading.get_text(strip=True)
                    } for heading in headings if heading.get_text(strip=True)])
            except:
                pass
                
            # Extract paragraphs
            try:
                content["paragraphs"] = [p.get_text(strip=True) for p in soup.find_all('p') 
                                    if p.get_text(strip=True)]
            except:
                pass
                
            # Extract lists
            try:
                for list_tag in soup.find_all(['ul', 'ol']):
                    list_items = [item.get_text(strip=True) for item in list_tag.find_all('li')]
                    if list_items:
                        content["lists"].append({
                            'type': list_tag.name,
                            'items': list_items
                        })
            except:
                pass
                
            # Extract links
            try:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith(('http', 'https')):
                        content["links"].append({
                            'text': link.get_text(strip=True),
                            'url': href
                        })
            except:
                pass
                
            # Extract images
            try:
                for img in soup.find_all('img', alt=True):
                    src = img.get('src', '')
                    if src:
                        content["images"].append({
                            'alt': img['alt'],
                            'src': src if src.startswith(('http', 'https')) else urljoin(url, src)
                        })
            except:
                pass
                
            # Extract tables
            try:
                for table in soup.find_all('table'):
                    table_data = []
                    headers = []
                    
                    # Get headers
                    for th in table.find_all('th'):
                        headers.append(th.get_text(strip=True))
                        
                    # Get rows
                    for row in table.find_all('tr'):
                        row_data = [td.get_text(strip=True) for td in row.find_all('td')]
                        if row_data:
                            table_data.append(row_data)
                            
                    if table_data:
                        content["tables"].append({
                            'headers': headers,
                            'data': table_data
                        })
            except:
                pass
                
            # Extract structured data (JSON-LD)
            try:
                structured_data = soup.find_all('script', type='application/ld+json')
                for data in structured_data:
                    try:
                        json_data = json.loads(data.string)
                        content["structured_data"] = json_data
                        break  # Take only the first valid JSON-LD
                    except:
                        continue
            except:
                pass
                
            return content
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Request failed: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "url": url
            }

    def _run(self, query: str) -> str:
        # result = self.scrap_main_page_link(query)
        result = self.scrap_main_page_content(query)
        # return f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}"
        return result

    async def _arun(self, query: str) -> str:
        # For simplicity, we'll just call the sync version
        # In a real scenario, you'd want to make this truly asynchronous
        return self._run(query)