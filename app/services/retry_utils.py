# app/services/retry_utils.py
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio

def retry_policy(attempts: int = 3):
    return {
        "stop": stop_after_attempt(attempts),
        "wait": wait_exponential(multiplier=0.5, max=10),
        "retry": retry_if_exception_type(Exception)
    }
