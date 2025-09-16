import os, logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class VectorStore:
    def __init__(self):
        self._backend = None
        self._docs = {}  # {doc_id: [chunks]}
        self._in_memory_texts = []
        self._tfidf = None

        redis_url = os.getenv("REDIS_URL")
        if redis_url and REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._backend = "redis"
                logger.info("VectorStore using Redis at %s", redis_url)
            except Exception as e:
                logger.error("Redis init failed, fallback to memory: %s", e)
                self._init_in_memory()
        else:
            self._init_in_memory()

    def _init_in_memory(self):
        self._backend = "in-memory"
        logger.info("VectorStore using in-memory backend")

    def upsert_document(self, doc_id: str, chunks: List[Dict]):
        self._docs[doc_id] = chunks
        if self._backend == "in-memory":
            self._in_memory_texts = [
                (c["chunk_id"], c["text"], {"doc_id": doc_id, **c.get("meta", {})})
                for d, chs in self._docs.items() for c in chs
            ]
            if SKLEARN_AVAILABLE and self._in_memory_texts:
                texts = [t for (_id, t, _m) in self._in_memory_texts]
                self._tfidf = TfidfVectorizer().fit_transform(texts)
        elif self._backend == "redis":
            self._redis.set(f"vec:doc:{doc_id}", repr(chunks))

    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        if self._backend == "in-memory":
            return self._query_in_memory(query_text, top_k)
        return self._query_redis(query_text, top_k)

    def _query_in_memory(self, query_text: str, top_k: int):
        if not self._in_memory_texts:
            return []
        if SKLEARN_AVAILABLE and self._tfidf is not None:
            vect = TfidfVectorizer().fit([t for (_, t, _) in self._in_memory_texts] + [query_text])
            q_vec = vect.transform([query_text])
            corpus = [t for (_, t, _) in self._in_memory_texts]
            corpus_vec = vect.transform(corpus)
            sims = cosine_similarity(q_vec, corpus_vec)[0]
            scored = [
                {"chunk_id": cid, "text": text, "meta": meta, "score": float(sim)}
                for (cid, text, meta), sim in zip(self._in_memory_texts, sims)
            ]
            return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
        # fallback substring
        results = []
        for cid, text, meta in self._in_memory_texts:
            score = self._simple_score(query_text, text)
            if score > 0:
                results.append({"chunk_id": cid, "text": text, "meta": meta, "score": score})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    def _query_redis(self, query_text: str, top_k: int):
        results = []
        for key in self._redis.scan_iter("vec:doc:*"):
            raw = self._redis.get(key)
            try:
                chunks = eval(raw)
            except Exception:
                continue
            for c in chunks:
                score = self._simple_score(query_text, c["text"])
                if score > 0:
                    results.append({"chunk_id": c["chunk_id"], "text": c["text"], "meta": c["meta"], "score": score})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    def _simple_score(self, q: str, text: str) -> float:
        q_words, t_words = set(q.lower().split()), set(text.lower().split())
        return len(q_words & t_words) / max(1, len(q_words))


_store: Optional[VectorStore] = None

def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
