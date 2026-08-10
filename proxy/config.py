from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    one_min_api_key: str
    proxy_shared_secret: str
    default_model: str = "gpt-4o-mini"
    one_min_base_url: str = "https://api.1min.ai"

    class Config:
        env_file = ".env"


settings = Settings()
