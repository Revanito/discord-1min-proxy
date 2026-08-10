from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    one_min_api_key: str
    proxy_shared_secret: str
    one_min_base_url: str = "https://api.1min.ai"

    model_easy: str = "grok-4-fast-non-reasoning"
    model_medium: str = "grok-4-fast-reasoning"
    model_hard: str = "grok-4.5"
    model_classifier: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


settings = Settings()
