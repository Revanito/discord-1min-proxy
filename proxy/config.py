from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    one_min_api_key: str
    proxy_shared_secret: str
    one_min_base_url: str = "https://api.1min.ai"

    model_code_easy: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    model_code_medium: str = "us.anthropic.claude-sonnet-4-6"
    model_code_hard: str = "us.anthropic.claude-opus-4-6-v1"

    model_general_easy: str = "grok-4.3"
    model_general_medium: str = "grok-4.5"
    model_general_hard: str = "grok-4.7"

    model_specific_easy: str = "gpt-5-mini"
    model_specific_medium: str = "gpt-5.4-mini"
    model_specific_hard: str = "gpt-5.2"

    model_classifier: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        protected_namespaces = ("settings_",)


settings = Settings()
