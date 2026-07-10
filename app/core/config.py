from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    redis_url: str = "redis://localhost:6379/0"
    refresh_token_expire_days: int = 14
    cookie_secure: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
