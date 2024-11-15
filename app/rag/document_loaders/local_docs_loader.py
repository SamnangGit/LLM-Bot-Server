from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_unstructured import UnstructuredLoader

from dotenv import load_dotenv
import os

load_dotenv()

class LocalDocsLoader:
    def __init__(self):
        pass

    def csv_loader(self, file_path: str):
        loader = CSVLoader(file_path=file_path,
            csv_args={
            'delimiter': ',',
            'quotechar': '"'
            })
        docs = loader.load()
        return docs
    

    def pdf_loader(self, file_path: str):
        loader = PyPDFLoader(file_path)
        pages = []
        for page in loader.load():
            pages.append(page)
        return pages  
    
    def unstructured_loader(self, file_path:str):
        loader = UnstructuredLoader(
        file_path=file_path,
        strategy="hi_res",
        partition_via_api=True,
        coordinates=True,
        api_key=os.getenv("UNSTRUCTURED_API_KEY")
        )
        docs = []
        for doc in loader.lazy_load():
            docs.append(doc)
        return docs  





        
