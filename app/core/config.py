from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "POE Profiter"
    # NOTE: Default database URL is for local development only.
    # In production, set DATABASE_URL via environment variables.
    database_url: str = "postgresql://poe_user:poe_password@db:5432/poe_profiter"
    
    class Config:
        env_file = ".env"


settings = Settings()
