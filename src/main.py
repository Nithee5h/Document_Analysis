from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from src.api.routes import router
from src.core.config import settings
from src.core.logging_config import setup_logging

setup_logging()

app = FastAPI(title=settings.app_name)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html at root path
@app.get("/")
async def root():
    return FileResponse(static_dir / "index.html") if static_dir.exists() else {"message": "Welcome to AI Document Analysis API"}

# Serve dashboard
@app.get("/dashboard")
async def dashboard():
    return FileResponse(static_dir / "dashboard.html") if static_dir.exists() else {"message": "Dashboard not found"}