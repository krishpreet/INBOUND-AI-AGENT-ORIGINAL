# app/core/metrics.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Counters
LLM_CALLS = Counter("llm_calls_total", "Number of LLM calls")
TTS_CALLS = Counter("tts_calls_total", "Number of TTS calls")
TTS_CACHE_HITS = Counter("tts_cache_hits_total", "Number of TTS cache hits")
TWILIO_ERRORS = Counter("twilio_errors_total", "Twilio errors")

# Histograms for latency
LLM_LATENCY = Histogram("llm_latency_seconds", "LLM latency seconds")
TTS_LATENCY = Histogram("tts_latency_seconds", "TTS latency seconds")

def metrics_response():
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
