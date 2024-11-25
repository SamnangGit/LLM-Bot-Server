from langchain_cohere import CohereEmbeddings

import os
from dotenv import load_dotenv


load_dotenv()

class EmbeddedModel:
    def __init__(self):
        pass
        

    def cohere_platform(self, model):
        cohere_api_key = os.getenv("COHERE_API_KEY")
        embeddings = CohereEmbeddings(model=model, cohere_api_key=cohere_api_key)
        return embeddings
