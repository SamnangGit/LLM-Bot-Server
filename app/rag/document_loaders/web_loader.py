from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders.firecrawl import FireCrawlLoader

from dotenv import load_dotenv
import os

load_dotenv()

class WebLoader:
    def __init__(self):
        pass


    def single_page_loader(self, url: str):
        loader = WebBaseLoader(web_path=url,
                requests_kwargs = {'verify':False})
        
        docs = loader.load()
        return docs
    

    def multiple_pages_loader(self, urls: list):
        loader = WebBaseLoader(web_paths=urls,
                requests_kwargs = {'verify':False})
        docs = loader.load()
        return docs
    

    def firecrawl_pages_loader(self, url: str):
        loader = FireCrawlLoader(
            api_key=os.getenv("FIRECRAWL_API_KEY"), url=url, mode="scrape"
        )   
        pages = []
        for doc in loader.lazy_load():
            pages.append(doc)

        return pages