
from fastapi import FastAPI
from fastapi_swagger_ui_theme import setup_swagger_ui_theme
from app.api.routes.health import router as health_router
from app.api.routes.workspaces import router as workspaces_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "An AI software engineering agent that investigates bugs, "
        "proposes code patches, and runs tests safely."
    ),
    docs_url=None,
)
setup_swagger_ui_theme(app)

app.include_router(health_router)
app.include_router(workspaces_router,prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "AI Software Engineer API",
        "docs": "/docs",
        "health": "/health",
    }
