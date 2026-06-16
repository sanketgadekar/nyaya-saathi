import os
import chromadb

# Use persistent local storage
client = chromadb.PersistentClient(path="./legal_db")

# Use ChromaDB's default embedding function
# This uses a tiny model built into chromadb itself — no sentence-transformers needed
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

embedding_fn = DefaultEmbeddingFunction()

bns_collection        = client.get_or_create_collection("bns_sections",    embedding_function=embedding_fn)
ipc_collection        = client.get_or_create_collection("ipc_sections",    embedding_function=embedding_fn)
bnss_collection       = client.get_or_create_collection("bnss_bail",       embedding_function=embedding_fn)
rights_collection     = client.get_or_create_collection("rights",          embedding_function=embedding_fn)
precedents_collection = client.get_or_create_collection("sc_precedents",   embedding_function=embedding_fn)
mapping_collection    = client.get_or_create_collection("ipc_bns_mapping", embedding_function=embedding_fn)


def query_law(query: str, law: str = "BNS", n: int = 5) -> list:
    col = bns_collection if law == "BNS" else ipc_collection
    try:
        results = col.query(query_texts=[query], n_results=min(n, col.count()) if col.count() > 0 else 1)
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        print(f"[RAG] query_law error: {e}")
        return []


def query_rights(situation: str, n: int = 5) -> list:
    try:
        count = rights_collection.count()
        if count == 0:
            return []
        results = rights_collection.query(query_texts=[situation], n_results=min(n, count))
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        print(f"[RAG] query_rights error: {e}")
        return []


def query_precedents(offence: str, n: int = 3) -> list:
    try:
        count = precedents_collection.count()
        if count == 0:
            return []
        results = precedents_collection.query(query_texts=[offence], n_results=min(n, count))
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        print(f"[RAG] query_precedents error: {e}")
        return []