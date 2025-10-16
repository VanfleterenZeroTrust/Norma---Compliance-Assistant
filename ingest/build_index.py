import os, glob, base64, uuid
from dotenv import load_dotenv
from fastembed import TextEmbedding
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType,
    VectorSearch, HnswVectorSearchAlgorithmConfiguration
)
from azure.search.documents import SearchClient
from chunkers import pdf_to_chunks

load_dotenv()
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_KEY = os.environ["AZURE_SEARCH_ADMIN_KEY"]
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX", "docs")

model = TextEmbedding("BAAI/bge-small-en-v1.5")
VECTOR_DIM = len(next(model.embed(["test string"])))

def embed_texts(texts):
    return [list(e) for e in model.embed(texts)]

idx_client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
    SearchField(name="source", type=SearchFieldDataType.String, searchable=True),
    SearchField(
        name="embedding",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=VECTOR_DIM,
        vector_search_configuration="hnsw",
    ),
]
vector_search = VectorSearch(
    algorithm_configurations=[HnswVectorSearchAlgorithmConfiguration(name="hnsw")]
)
index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
try:
    idx_client.delete_index(INDEX_NAME)
except Exception:
    pass
print(f"Creating index '{INDEX_NAME}'...")
idx_client.create_index(index)

docs = []
for path in glob.glob("./data/*.pdf"):
    filename = os.path.basename(path)
    for ch in pdf_to_chunks(path):
        ch["source"] = filename
        docs.append(ch)

client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))
print(f"Total chunks to upload: {len(docs)}")
BATCH = 32
for i in range(0, len(docs), BATCH):
    batch = docs[i:i+BATCH]
    embs = embed_texts([d["text"] for d in batch])
    out = []
    for d, e in zip(batch, embs):
        sid = base64.urlsafe_b64encode(uuid.uuid4().hex.encode()).decode().rstrip("=")
        out.append({
            "id": sid,
            "content": d["text"],
            "source": d["source"],
            "embedding": [float(x) for x in e],
        })
    client.upload_documents(out)
    print(f"Uploaded {len(out)} docs")
print("Done.")
