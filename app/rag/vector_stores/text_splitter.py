from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.document_loaders.local_docs_loader import LocalDocsLoader

from typing import List, Dict
from uuid import uuid4
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: Dict[str, str]

def convert_texts_to_documents(texts: List[str], source: str = "pdf") -> tuple[List[Document], List[str]]:
    documents = []
    for text in texts:
        doc = Document(
            page_content=text,
            metadata={"source": source}
        )
        documents.append(doc)
    
    uuids = [str(uuid4()) for _ in range(len(documents))]
    
    return documents, uuids

def text_splitter(file_path: str):
    loader = LocalDocsLoader()
    document = loader.pdf_loader(file_path=file_path)
    document = str(document)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=0)

    texts = text_splitter.split_text(document)
    
    documents, uuids = convert_texts_to_documents(texts)
    
    return documents, uuids

