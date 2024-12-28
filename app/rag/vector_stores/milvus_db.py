from langchain_milvus import Milvus
from langchain_core.documents import Document

from .embedded_model import EmbeddedModel


URI = "./milvus_rag.db"

class MilvusStore:
    def __init__(self):
        self.embedded_model = EmbeddedModel().cohere_platform("embed-multilingual-v3.0")
        self.vector_store = Milvus(
             embedding_function=self.embedded_model,
             connection_args={"uri": URI}
        )

    def add_document(self, docs, ids):       
        docs = self.vector_store.add_documents(documents=docs, ids=ids)
        return str(len(docs)) + " document(s) added"


    def search_document(self, query):
        result = self.vector_store.similarity_search(
            query=query,
            k=4
        )
        return result
    
    def document_retriever(self, query):
        retriever =  self.vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4})
        retrieved_docs = retriever.invoke(query)
        return retrieved_docs


    def delete_document(self, ids):
        self.vector_store.delete(
            ids=ids
        )
        return "deleted successfully"