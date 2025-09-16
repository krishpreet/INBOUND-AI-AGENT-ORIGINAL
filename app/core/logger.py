# app/core/logger.py
import logging
import os
from pythonjsonlogger import jsonlogger

def configure_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root = logging.getLogger()
    if root.handlers:
        # avoid duplicate handlers if reloading
        return
    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(fmt)
    root.addHandler(handler)
    root.setLevel(level)

def get_logger(name: str):
    return logging.getLogger(name)
