from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    database_url_readonly: str = ""
    sql_statement_timeout_ms: int = 5000
    upstage_api_key: str = ""
    upstage_model: str = "solar-pro2"

    class Config:
        env_file = ".env"


settings = Settings()
