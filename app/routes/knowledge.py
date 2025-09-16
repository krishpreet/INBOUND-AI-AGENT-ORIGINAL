# app/routes/knowledge.py
import logging
import uuid
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.knowledge.ingest_service import ingest_document
from app.knowledge.retriever import retrieve
from app.knowledge.vector_store import get_vector_store

logger = logging.getLogger("app.routes.knowledge")
router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

# Simple in-memory place to hold last ingest debug info (dev only)
_last_ingest_info = {"doc_id": None, "chunks": 0, "ts": None}


class UploadBody(BaseModel):
    text: str
    doc_id: Optional[str] = None  # optional, server will create if missing


class QueryBody(BaseModel):
    q: str
    top_k: int = 3


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_text(body: UploadBody):
    """
    Ingest raw text into the vector store.
    Returns: {"doc_id": "...", "chunks": N}
    """
    start_ts = datetime.datetime.utcnow()
    logger.debug("upload_text called; incoming doc_id=%s text_len=%d", body.doc_id, len(body.text) if body.text else 0)

    if not body.text or not body.text.strip():
        logger.warning("upload_text rejected empty text")
        raise HTTPException(status_code=400, detail="text is required and must be non-empty")

    doc_id = body.doc_id or f"doc-{uuid.uuid4().hex[:8]}"
    try:
        res = await ingest_document(doc_id, body.text, meta={})
    except Exception as e:
        logger.exception("ingest_document failed for doc %s", doc_id)
        raise HTTPException(status_code=500, detail=f"ingest failed: {str(e)[:200]}")

    # update last ingest debug info
    _last_ingest_info["doc_id"] = res.get("doc_id", doc_id)
    _last_ingest_info["chunks"] = res.get("chunks", 0)
    _last_ingest_info["ts"] = start_ts.isoformat() + "Z"

    logger.info("Ingest complete doc=%s chunks=%s took=%sms", doc_id, res.get("chunks"), int((datetime.datetime.utcnow() - start_ts).total_seconds()*1000))
    return res


@router.post("/upload_file", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a plain text file (utf-8). Non-text or very large files should be rejected in prod.
    """
    start_ts = datetime.datetime.utcnow()
    logger.debug("upload_file called; filename=%s content_type=%s", file.filename, file.content_type)

    try:
        raw = await file.read()
        # defensively decode, ignore errors
        text = raw.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.exception("Failed to read uploaded file %s", file.filename)
        raise HTTPException(status_code=400, detail="failed to read file upload")

    if not text.strip():
        logger.warning("upload_file rejected empty content for %s", file.filename)
        raise HTTPException(status_code=400, detail="file contains no text")

    doc_id = f"file-{file.filename}-{uuid.uuid4().hex[:6]}"
    try:
        res = await ingest_document(doc_id, text, meta={"filename": file.filename})
    except Exception as e:
        logger.exception("ingest_document failed for uploaded file %s", file.filename)
        raise HTTPException(status_code=500, detail=f"ingest failed: {str(e)[:200]}")

    _last_ingest_info["doc_id"] = res.get("doc_id", doc_id)
    _last_ingest_info["chunks"] = res.get("chunks", 0)
    _last_ingest_info["ts"] = start_ts.isoformat() + "Z"

    logger.info("File ingest complete doc=%s file=%s chunks=%s", doc_id, file.filename, res.get("chunks"))
    return res


@router.get("/docs")
async def list_docs():
    """
    Returns dev-info about vector store and currently ingested doc ids.
    """
    store = get_vector_store()
    try:
        docs = list(store._docs.keys())
    except Exception:
        logger.exception("failed to read vector store internals")
        docs = []
    return {"backend": getattr(store, "_backend", "unknown"), "docs": docs}


@router.post("/query")
async def query_knowledge(body: QueryBody):
    """
    Query the knowledge base and return top-k chunks (dev retrieval).
    """
    logger.debug("Query called q=%s top_k=%s", body.q, body.top_k)
    if not body.q or not body.q.strip():
        raise HTTPException(status_code=400, detail="q is required and must be non-empty")

    try:
        results = retrieve(body.q, top_k=body.top_k)
    except Exception as e:
        logger.exception("retriever failed for q=%s", body.q)
        raise HTTPException(status_code=500, detail=f"retrieval failed: {str(e)[:200]}")

    return {"query": body.q, "results": results, "count": len(results)}


@router.get("/last_ingest")
async def last_ingest():
    """
    Development helper: returns last ingest metadata (doc id, chunk count, timestamp).
    """
    return _last_ingest_info


@router.delete("/docs/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_doc(doc_id: str):
    store = get_vector_store()
    if doc_id in store._docs:
        try:
            del store._docs[doc_id]
            # rebuild in-memory index if needed
            store.upsert_document("__rebuild__", [])
            logger.info("Deleted doc %s from vector store", doc_id)
            return {"deleted": doc_id}
        except Exception:
            logger.exception("Failed deleting doc %s", doc_id)
            raise HTTPException(status_code=500, detail="delete failed")
    raise HTTPException(status_code=404, detail="not found")