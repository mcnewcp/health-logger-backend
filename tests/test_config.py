"""Test suite for configuration modules."""

import os
from unittest.mock import Mock, patch

import pytest

from src.config.settings import (
    AirtableConfig,
    AppConfig,
    LLMConfig,
    LLMProvider,
    Settings,
)
from src.config.llm_config import (
    LLMConfigError,
    create_llm,
    get_model_info,
    _create_ollama_llm,
    _create_openai_llm,
    _create_claude_llm,
)


class TestSettings:
    """Test the Settings configuration classes."""

    def test_llm_provider_enum(self):
        """Test LLM provider enumeration."""
        assert LLMProvider.OLLAMA == "ollama"
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.CLAUDE == "claude"

    def test_airtable_config_creation(self):
        """Test creating AirtableConfig with required fields."""
        config = AirtableConfig(
            personal_access_token="test_token",
            base_id="test_base"
        )
        
        assert config.personal_access_token == "test_token"
        assert config.base_id == "test_base"
        assert config.heart_log_table == "heart_log"  # Default value

    def test_llm_config_creation(self):
        """Test creating LLMConfig with different providers."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            ollama_model="llama3.1"
        )
        
        assert config.provider == LLMProvider.OLLAMA
        assert config.ollama_model == "llama3.1"
        assert config.ollama_base_url == "http://localhost:11434"  # Default

    def test_app_config_defaults(self):
        """Test AppConfig default values."""
        config = AppConfig()
        
        assert config.timezone == "America/Chicago"
        assert config.log_level.value == "INFO"
        assert config.log_format.value == "json"

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "test_openai_key",
        "TIMEZONE": "America/New_York"
    })
    def test_settings_load_from_env(self):
        """Test loading settings from environment variables."""
        settings = Settings.load_from_env()
        
        assert settings.airtable.personal_access_token == "test_token"
        assert settings.airtable.base_id == "test_base"
        assert settings.llm.provider == LLMProvider.OPENAI
        assert settings.llm.openai_api_key == "test_openai_key"
        assert settings.app.timezone == "America/New_York"

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "openai"
        # Missing OPENAI_API_KEY
    }, clear=True)
    def test_validate_required_keys_missing_openai(self):
        """Test validation fails when OpenAI key is missing."""
        settings = Settings.load_from_env()
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate_required_keys()
        
        assert "OpenAI API key is required" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token", 
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "claude"
        # Missing ANTHROPIC_API_KEY
    }, clear=True)
    def test_validate_required_keys_missing_claude(self):
        """Test validation fails when Claude key is missing."""
        settings = Settings.load_from_env()
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate_required_keys()
        
        assert "Anthropic API key is required" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base", 
        "LLM_PROVIDER": "ollama"
    })
    def test_validate_required_keys_ollama_success(self):
        """Test validation passes for Ollama (no API key required)."""
        settings = Settings.load_from_env()
        
        # Should not raise exception
        settings.validate_required_keys()


class TestLLMConfig:
    """Test LLM configuration and initialization."""

    @patch('src.config.llm_config.Ollama')
    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "ollama",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.1"
    })
    def test_create_ollama_llm_success(self, mock_ollama):
        """Test successful Ollama LLM creation."""
        mock_ollama_instance = Mock()
        mock_ollama.return_value = mock_ollama_instance
        
        settings = Settings.load_from_env()
        result = _create_ollama_llm(settings)
        
        assert result == mock_ollama_instance
        mock_ollama.assert_called_once_with(
            base_url="http://localhost:11434",
            model="llama3.1",
            temperature=0.1
        )

    @patch('src.config.llm_config.ChatOpenAI')
    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "test_key"
    })
    def test_create_openai_llm_success(self, mock_chat_openai):
        """Test successful OpenAI LLM creation."""
        mock_openai_instance = Mock()
        mock_chat_openai.return_value = mock_openai_instance
        
        settings = Settings.load_from_env()
        result = _create_openai_llm(settings)
        
        assert result == mock_openai_instance
        mock_chat_openai.assert_called_once_with(
            api_key="test_key",
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1000
        )

    @patch('src.config.llm_config.ChatAnthropic')
    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "claude",
        "ANTHROPIC_API_KEY": "test_key"
    })
    def test_create_claude_llm_success(self, mock_chat_anthropic):
        """Test successful Claude LLM creation."""
        mock_claude_instance = Mock()
        mock_chat_anthropic.return_value = mock_claude_instance
        
        settings = Settings.load_from_env()
        result = _create_claude_llm(settings)
        
        assert result == mock_claude_instance
        mock_chat_anthropic.assert_called_once_with(
            api_key="test_key",
            model="claude-3-haiku-20240307",
            temperature=0.1,
            max_tokens=1000
        )

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "ollama"
        # Missing OLLAMA_BASE_URL and OLLAMA_MODEL
    })
    def test_create_ollama_llm_missing_config(self):
        """Test Ollama creation fails with missing configuration."""
        settings = Settings.load_from_env()
        settings.llm.ollama_base_url = None
        
        with pytest.raises(LLMConfigError) as exc_info:
            _create_ollama_llm(settings)
        
        assert "Ollama base URL and model are required" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "openai"
        # Missing OPENAI_API_KEY
    }, clear=True)
    def test_create_openai_llm_missing_key(self):
        """Test OpenAI creation fails with missing API key."""
        settings = Settings.load_from_env()
        
        with pytest.raises(LLMConfigError) as exc_info:
            _create_openai_llm(settings)
        
        assert "OpenAI API key is required" in str(exc_info.value)

    @patch('src.config.llm_config._create_ollama_llm')
    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "ollama"
    })
    def test_create_llm_ollama(self, mock_create_ollama):
        """Test create_llm function with Ollama provider."""
        mock_llm = Mock()
        mock_create_ollama.return_value = mock_llm
        
        settings = Settings.load_from_env()
        result = create_llm(settings)
        
        assert result == mock_llm
        mock_create_ollama.assert_called_once_with(settings)

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "invalid_provider"
    })
    def test_create_llm_unsupported_provider(self):
        """Test create_llm fails with unsupported provider."""
        from pydantic import ValidationError
        from src.config.settings import AirtableConfig, AppConfig
        
        airtable_config = AirtableConfig(
            personal_access_token="test_token",
            base_id="test_base"
        )
        
        # This should raise a validation error during LLMConfig creation
        with pytest.raises(ValidationError) as exc_info:
            llm_config = LLMConfig(provider="invalid_provider")
        
        assert "Input should be 'ollama', 'openai' or 'claude'" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "ollama",
        "OLLAMA_MODEL": "llama3.1"
    })
    def test_get_model_info_ollama(self):
        """Test getting model info for Ollama provider."""
        settings = Settings.load_from_env()
        info = get_model_info(settings)
        
        assert info["provider"] == "ollama"
        assert info["model"] == "llama3.1"
        assert info["base_url"] == "http://localhost:11434"
        assert info["temperature"] == 0.1

    @patch.dict(os.environ, {
        "AIRTABLE_PAT": "test_token",
        "AIRTABLE_BASE_ID": "test_base",
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "test_key"
    })
    def test_get_model_info_openai(self):
        """Test getting model info for OpenAI provider."""
        settings = Settings.load_from_env()
        info = get_model_info(settings)
        
        assert info["provider"] == "openai"
        assert info["model"] == "gpt-4o-mini"
        assert info["api_key_configured"] is True