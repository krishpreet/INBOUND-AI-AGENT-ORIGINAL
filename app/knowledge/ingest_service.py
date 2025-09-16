# app/knowledge/ingest_service.py
"""
Ingest service: chunking + safe upsert to vector store.

This version offloads heavy work to a threadpool (asyncio.to_thread)
and enforces a per-ingest timeout to avoid hanging requests.
"""
from typing import List, Dict, Optional
import uuid
import logging
import asyncio
from app.knowledge.vector_store import get_vector_store

logger = logging.getLogger(__name__)

CHUNK_SIZE = 800  # characters
CHUNK_OVERLAP = 100
# Per-ingest timeout (seconds) — tune as needed
INGEST_TIMEOUT_SECONDS = 10.0


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text or ""
    text = text.strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    L = len(text)
    while start < L:
        end = min(L, start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
        if start >= L:
            break
    return chunks


async def embed_texts(texts: List[str]) -> List:
    """
    Pluggable embedding — default is no-op (return texts).
    Replace this with a true embedding provider if available.
    Keep this async-friendly (avoid blocking on the event loop).
    """
    # If you add network calls here, make them async (httpx AsyncClient).
    return texts


async def _run_upsert_in_thread(store, doc_id: str, chunk_objs: List[Dict]):
    """
    Helper to call store.upsert_document in a thread so we don't block event loop.
    """
    return await asyncio.to_thread(store.upsert_document, doc_id, chunk_objs)


async def ingest_document(doc_id: str, raw_text: str, meta: Optional[Dict] = None) -> Dict:
    """
    Ingest a document safely:
      - chunk the text
      - build chunk objects
      - offload store.upsert_document to threadpool
      - enforce timeout and logging
    Returns: {"doc_id": ..., "chunks": N}
    """
    meta = meta or {}
    start_ts = asyncio.get_event_loop().time()
    logger.debug("ingest_document called doc_id=%s text_len=%d", doc_id, len(raw_text or ""))

    # lightweight chunking on event loop (fast)
    chunks = chunk_text(raw_text)
    if not chunks:
        logger.warning("ingest_document called with empty or whitespace-only text")
        return {"doc_id": doc_id, "chunks": 0}

    store = get_vector_store()
    chunk_objs = []
    for idx, c in enumerate(chunks):
        chunk_id = f"{doc_id}::{idx}::{uuid.uuid4().hex[:6]}"
        chunk_objs.append({"chunk_id": chunk_id, "text": c, "meta": meta})

    # Offload heavy upsert to thread and enforce timeout
    try:
        res = await asyncio.wait_for(_run_upsert_in_thread(store, doc_id, chunk_objs), timeout=INGEST_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        logger.exception("ingest_document timed out for doc %s after %s seconds", doc_id, INGEST_TIMEOUT_SECONDS)
        raise Exception(f"ingest timeout after {INGEST_TIMEOUT_SECONDS}s")
    except Exception as e:
        logger.exception("ingest_document failed for doc %s: %s", doc_id, str(e)[:200])
        raise

    elapsed = asyncio.get_event_loop().time() - start_ts
    logger.info("Ingested doc %s with %d chunks in %.3fs", doc_id, len(chunk_objs), elapsed)
    # Return normalized response
    return {"doc_id": doc_id, "chunks": len(chunk_objs)}