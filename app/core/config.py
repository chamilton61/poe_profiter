from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "POE Profiter"
    database_url: str = "postgresql://poe_user:poe_password@db:5432/poe_profiter"
    
    class Config:
        env_file = ".env"


settings = Settings()
