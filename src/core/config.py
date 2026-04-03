from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Document Analysis API"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    api_key: str = "sk_track2_987654321"
    max_file_size_mb: int = 20
    enable_celery: bool = False
    redis_url: str = "redis://localhost:6379/0"
    spacy_model: str = "en_core_web_sm"
    
    # Google Cloud Vision Settings
    use_google_vision: bool = False
    google_vision_project_id: str = ""
    google_credentials_path: str = ""
    
    @property
    def tesseract_cmd(self) -> str:
        """Auto-detect Tesseract path based on OS"""
        # Check if environment variable is set
        if os.environ.get("TESSERACT_CMD"):
            return os.environ.get("TESSERACT_CMD")
        
        # Default paths for different systems
        possible_paths = [
            "/usr/bin/tesseract",           # Linux (Railway, Docker)
            "/opt/homebrew/bin/tesseract",  # macOS (M1/M2)
            "/usr/local/bin/tesseract",     # macOS (Intel)
            "tesseract",                    # In PATH
        ]
        
        for path in possible_paths:
            if path == "tesseract":
                # Will be in PATH
                return path
            if os.path.exists(path):
                return path
        
        # Fallback to system PATH
        return "tesseract"


settings = Settings()