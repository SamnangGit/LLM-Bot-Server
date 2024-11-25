from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.document_loaders.web_loader import WebLoader

from typing import List, Dict
from uuid import uuid4
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: Dict[str, str]

def convert_texts_to_documents(texts: List[str], source: str = "web") -> tuple[List[Document], List[str]]:
    documents = []
    for text in texts:
        doc = Document(
            page_content=text,
            metadata={"source": source}
        )
        documents.append(doc)
    
    uuids = [str(uuid4()) for _ in range(len(documents))]
    
    return documents, uuids

def text_splitter():
    loader = WebLoader()
    document = loader.single_page_loader(url="https://edition.cnn.com/2024/11/23/entertainment/glinda-elphaba-wicked-cec/index.html")
    document = str(document)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    texts = text_splitter.split_text(document)
    
    documents, uuids = convert_texts_to_documents(texts)
    
    return documents, uuids

