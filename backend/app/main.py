
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "An AI software engineering agent that investigates bugs, "
        "proposes code patches, and runs tests safely."
    ),
)

app.include_router(health_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "AI Software Engineer API",
        "docs": "/docs",
        "health": "/health",
    }
