from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    resend_api_key: str = ""
    digest_from_email: str = "onboarding@resend.dev"
    digest_to_email: str = ""

    db_path: str = "data/tech_brief.duckdb"
    briefs_dir: str = "data/briefs"

    review_model: str = "claude-haiku-4-5-20251001"

    hours_lookback: int = 24
    max_stories_per_source: int = 50

    log_level: str = "INFO"


settings = Settings()
