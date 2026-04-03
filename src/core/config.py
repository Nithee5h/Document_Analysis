from pydantic_settings import BaseSettings, SettingsConfigDict


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
    tesseract_cmd: str = "/opt/homebrew/bin/tesseract"
    spacy_model: str = "en_core_web_sm"
    
    # Google Cloud Vision Settings
    use_google_vision: bool = False
    google_vision_project_id: str = ""
    google_credentials_path: str = ""


settings = Settings()