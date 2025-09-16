from typing import List, Dict
from app.knowledge.vector_store import get_vector_store

def retrieve(query_text: str, top_k: int = 3) -> List[Dict]:
    return get_vector_store().query(query_text, top_k)
