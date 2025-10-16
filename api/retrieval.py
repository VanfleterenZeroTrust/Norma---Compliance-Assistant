import os
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
index = os.environ["AZURE_SEARCH_INDEX"]

model = TextEmbedding("BAAI/bge-small-en-v1.5")

def embed_query(q: str):
    return list(next(model.embed([q])))

def retrieve(question: str, k: int = 3) -> List[Dict[str, Any]]:
    client = SearchClient(endpoint, index, AzureKeyCredential(key))
    vector = embed_query(question)
    results = client.search(
        search_text=None,
        vector={"value": vector, "fields": "embedding", "k": k},
        select=["id", "content", "source"]
    )
    return [{"id": r["id"], "content": r["content"], "source": r.get("source")} for r in results]
