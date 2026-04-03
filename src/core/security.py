from fastapi import Header, HTTPException, status
from src.core.config import settings


async def validate_api_key(x_api_key: str = Header(default="")) -> str:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key