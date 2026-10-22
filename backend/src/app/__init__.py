"""
Async POC — FastAPI + uvloop + Granian + Prefect + Queuefy + NiceGUI
=====================================================================

100% async, layered architecture:

    presentation/  →  HTTP routes (FastAPI) & UI pages (NiceGUI)
    application/   →  Use-cases / orchestrators
    domain/        →  Entities, value objects, repository ports
    infrastructure/→  Adapters: DB, Queuefy, Prefect, external APIs
"""

__version__ = "0.1.0"
