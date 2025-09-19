from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "ADK Three-Agent Service"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    AGENT_TIMEOUT_SECONDS: int = Field(30, description="Timeout seconds per agent run")
    AGENT_RETRY_ATTEMPTS: int = Field(2, description="Number of retry attempts on transient errors")
    AGENT_RETRY_BACKOFF: int = Field(1, description="Backoff multiplier in seconds")
    # ADK model settings
    MODEL_1: str = Field("openai/gpt-4o", description="Model identifier for Agent1")
    MODEL_2: str = Field("gemini-2.0", description="Model identifier for Agent2")
    MODEL_3: str = Field("gemini-2.0-flash", description="Model identifier for Agent3")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()