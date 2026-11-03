"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.db.registry  # noqa: F401  (registers every ORM model)
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.health.router import router as health_router
from app.modules.merchants.router import router as merchants_router

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(merchants_router, prefix="/api")
