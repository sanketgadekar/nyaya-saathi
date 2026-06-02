import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_fn = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./legal_db")

bns_collection      = client.get_or_create_collection("bns_sections",      embedding_function=embedding_fn)
ipc_collection      = client.get_or_create_collection("ipc_sections",      embedding_function=embedding_fn)
bnss_collection     = client.get_or_create_collection("bnss_bail",         embedding_function=embedding_fn)
rights_collection   = client.get_or_create_collection("rights",            embedding_function=embedding_fn)
precedents_collection = client.get_or_create_collection("sc_precedents",   embedding_function=embedding_fn)
mapping_collection  = client.get_or_create_collection("ipc_bns_mapping",   embedding_function=embedding_fn)

def query_law(query: str, law: str = "BNS", n: int = 5) -> list:
    col = bns_collection if law == "BNS" else ipc_collection
    results = col.query(query_texts=[query], n_results=n)
    return results["documents"][0] if results["documents"] else []

def query_rights(situation: str, n: int = 5) -> list:
    results = rights_collection.query(query_texts=[situation], n_results=n)
    return results["documents"][0] if results["documents"] else []

def query_precedents(offence: str, n: int = 3) -> list:
    results = precedents_collection.query(query_texts=[offence], n_results=n)
    return results["documents"][0] if results["documents"] else []