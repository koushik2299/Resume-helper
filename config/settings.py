"""Configuration settings for the Resume Builder application."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-sonnet-4-20250514", env="CLAUDE_MODEL")
    
    # Job Board API (Adzuna)
    adzuna_app_id: str = Field(default="", env="ADZUNA_APP_ID")
    adzuna_app_key: str = Field(default="", env="ADZUNA_APP_KEY")
    
    # Job Board Settings
    default_job_role: str = Field(default="AI Engineer", env="DEFAULT_JOB_ROLE")
    default_job_industry: str = Field(default="healthcare", env="DEFAULT_JOB_INDUSTRY")
    default_job_hours: int = Field(default=24, env="DEFAULT_JOB_HOURS")
    max_job_results: int = Field(default=20, env="MAX_JOB_RESULTS")
    
    # Validation Settings
    summary_char_min: int = Field(default=105, env="SUMMARY_CHAR_MIN")
    summary_char_max: int = Field(default=109, env="SUMMARY_CHAR_MAX")
    summary_bullet_count: int = Field(default=4, env="SUMMARY_BULLET_COUNT")
    min_keywords_required: int = Field(default=5, env="MIN_KEYWORDS_REQUIRED")
    top_keywords_count: int = Field(default=8, env="TOP_KEYWORDS_COUNT")
    
    # Project Settings
    max_retries: int = Field(default=1, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
