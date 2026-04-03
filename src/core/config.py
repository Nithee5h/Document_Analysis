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
        """Auto-detect Tesseract path for cross-platform compatibility"""
        # Check environment variable
        if os.environ.get("TESSERACT_CMD"):
            return os.environ["TESSERACT_CMD"]
        
        # Try common Linux paths first (for Railway/Docker)
        linux_paths = ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]
        for path in linux_paths:
            if os.path.exists(path):
                return path
        
        # Try macOS paths
        macos_paths = ["/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"]
        for path in macos_paths:
            if os.path.exists(path):
                return path
        
        # Fallback: assume it's in PATH
        return "tesseract"


settings = Settings()