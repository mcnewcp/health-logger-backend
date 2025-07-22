"""Application configuration settings."""

import os
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load environment variables
load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"


class LogLevel(str, Enum):
    """Supported log levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(str, Enum):
    """Supported log formats."""
    
    JSON = "json"
    TEXT = "text"


class AirtableConfig(BaseModel):
    """Airtable configuration settings."""
    
    personal_access_token: str = Field(..., description="Airtable Personal Access Token")
    base_id: str = Field(..., description="Airtable Base ID")
    heart_log_table: str = Field(default="heart_log", description="Heart rate and blood pressure table")
    body_log_table: str = Field(default="body_log", description="Body composition table")
    nutrition_log_table: str = Field(default="nutrition_log", description="Nutrition tracking table")
    caffeine_log_table: str = Field(default="caffeine_log", description="Caffeine consumption table")
    alcohol_log_table: str = Field(default="alcohol_log", description="Alcohol consumption table")
    sauna_log_table: str = Field(default="sauna_log", description="Sauna session table")


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    
    provider: LLMProvider = Field(..., description="Selected LLM provider")
    ollama_base_url: Optional[str] = Field(default="http://localhost:11434", description="Ollama server URL")
    ollama_model: Optional[str] = Field(default="llama3.1", description="Ollama model name")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")


class AppConfig(BaseModel):
    """Application-wide configuration."""
    
    timezone: str = Field(default="America/Chicago", description="Default timezone for datetime parsing")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Application log level")
    log_format: LogFormat = Field(default=LogFormat.JSON, description="Application log format")


class Settings(BaseModel):
    """Main application settings."""
    
    airtable: AirtableConfig
    llm: LLMConfig
    app: AppConfig

    @classmethod
    def load_from_env(cls) -> "Settings":
        """
        Load settings from environment variables.

        Returns:
            Settings: Configured application settings.

        Raises:
            ValueError: If required environment variables are missing.
        """
        # Airtable configuration
        airtable_config = AirtableConfig(
            personal_access_token=os.getenv("AIRTABLE_PAT", ""),
            base_id=os.getenv("AIRTABLE_BASE_ID", ""),
            heart_log_table=os.getenv("HEART_LOG_TABLE", "heart_log"),
            body_log_table=os.getenv("BODY_LOG_TABLE", "body_log"),
            nutrition_log_table=os.getenv("NUTRITION_LOG_TABLE", "nutrition_log"),
            caffeine_log_table=os.getenv("CAFFEINE_LOG_TABLE", "caffeine_log"),
            alcohol_log_table=os.getenv("ALCOHOL_LOG_TABLE", "alcohol_log"),
            sauna_log_table=os.getenv("SAUNA_LOG_TABLE", "sauna_log"),
        )

        # LLM configuration
        llm_provider = os.getenv("LLM_PROVIDER", "ollama")
        llm_config = LLMConfig(
            provider=LLMProvider(llm_provider),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        # Application configuration
        app_config = AppConfig(
            timezone=os.getenv("TIMEZONE", "America/Chicago"),
            log_level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
            log_format=LogFormat(os.getenv("LOG_FORMAT", "json")),
        )

        return cls(
            airtable=airtable_config,
            llm=llm_config,
            app=app_config,
        )

    def validate_required_keys(self) -> None:
        """
        Validate that required API keys are present for the selected LLM provider.

        Raises:
            ValueError: If required API keys are missing for the selected provider.
        """
        if self.llm.provider == LLMProvider.OPENAI and not self.llm.openai_api_key:
            raise ValueError("OpenAI API key is required when LLM_PROVIDER=openai")
        
        if self.llm.provider == LLMProvider.CLAUDE and not self.llm.anthropic_api_key:
            raise ValueError("Anthropic API key is required when LLM_PROVIDER=claude")


# Global settings instance
settings = Settings.load_from_env()