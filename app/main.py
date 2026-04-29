# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    'lifespan' replaces the old @app.on_event("startup") pattern.
    FastAPI 0.95+ recommends this approach.
    """

    # -- Startup ------------------
    print(f"Starting {settings.APP_NAME}...")
    print(f"Environment: {settings.APP_ENV}")

    # Quick DB connectivity check
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection successful!")
    except Exception as e:
        print(f"x Database connection FAILED: {e}")
        raise       # crash on startup if DB is unreachable - fail test
    yield           # app runs here

    # -- Shutdown ---------------------------
    await engine.dispose()
    print("Database connections closed.")

app = FastAPI(
    title = settings.APP_NAME,
    debug = settings.DEBUG,
    lifespan=lifespan,
)

@app.get("/health")
async def health_check():
    """
    Simple endpoint to confirm the API is running.
    Used by load balancers and monitoring tools in production.
    """
    return {
        "Status" : "OK!",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }