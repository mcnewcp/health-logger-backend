"""LLM provider configuration and initialization."""

from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from .settings import LLMProvider, Settings, settings


class LLMConfigError(Exception):
    """Exception raised when LLM configuration is invalid."""
    
    pass


def create_llm(config: Settings = settings) -> Any:
    """
    Create an LLM instance based on the configuration.

    Args:
        config (Settings): Application configuration settings.

    Returns:
        Any: Configured LLM instance (ChatOllama, ChatOpenAI, or ChatAnthropic).

    Raises:
        LLMConfigError: If the LLM provider configuration is invalid.
    """
    # Validate that required keys are available
    config.validate_required_keys()
    
    if config.llm.provider == LLMProvider.OLLAMA:
        return _create_ollama_llm(config)
    elif config.llm.provider == LLMProvider.OPENAI:
        return _create_openai_llm(config)
    elif config.llm.provider == LLMProvider.CLAUDE:
        return _create_claude_llm(config)
    else:
        raise LLMConfigError(f"Unsupported LLM provider: {config.llm.provider}")


def _create_ollama_llm(config: Settings) -> ChatOllama:
    """
    Create and configure an Ollama LLM instance.

    Args:
        config (Settings): Application configuration settings.

    Returns:
        ChatOllama: Configured ChatOllama instance.

    Raises:
        LLMConfigError: If Ollama configuration is invalid.
    """
    if not config.llm.ollama_base_url or not config.llm.ollama_model:
        raise LLMConfigError("Ollama base URL and model are required for Ollama provider")
    
    try:
        return ChatOllama(
            base_url=config.llm.ollama_base_url,
            model=config.llm.ollama_model,
            temperature=0.1,  # Low temperature for consistent health data parsing
        )
    except Exception as e:
        raise LLMConfigError(f"Failed to initialize ChatOllama: {e}") from e


def _create_openai_llm(config: Settings) -> ChatOpenAI:
    """
    Create and configure an OpenAI LLM instance.

    Args:
        config (Settings): Application configuration settings.

    Returns:
        ChatOpenAI: Configured OpenAI instance.

    Raises:
        LLMConfigError: If OpenAI configuration is invalid.
    """
    if not config.llm.openai_api_key:
        raise LLMConfigError("OpenAI API key is required for OpenAI provider")
    
    try:
        return ChatOpenAI(
            api_key=config.llm.openai_api_key,
            model="gpt-4o-mini",  # Cost-effective model for health data parsing
            temperature=0.1,  # Low temperature for consistent parsing
            max_tokens=1000,  # Reasonable limit for tool calls
        )
    except Exception as e:
        raise LLMConfigError(f"Failed to initialize OpenAI: {e}") from e


def _create_claude_llm(config: Settings) -> ChatAnthropic:
    """
    Create and configure a Claude LLM instance.

    Args:
        config (Settings): Application configuration settings.

    Returns:
        ChatAnthropic: Configured Claude instance.

    Raises:
        LLMConfigError: If Claude configuration is invalid.
    """
    if not config.llm.anthropic_api_key:
        raise LLMConfigError("Anthropic API key is required for Claude provider")
    
    try:
        return ChatAnthropic(
            api_key=config.llm.anthropic_api_key,
            model="claude-3-haiku-20240307",  # Cost-effective model for health data parsing
            temperature=0.1,  # Low temperature for consistent parsing
            max_tokens=1000,  # Reasonable limit for tool calls
        )
    except Exception as e:
        raise LLMConfigError(f"Failed to initialize Claude: {e}") from e


def get_model_info(config: Settings = settings) -> dict:
    """
    Get information about the current LLM configuration.

    Args:
        config (Settings): Application configuration settings.

    Returns:
        dict: Information about the current LLM provider and model.
    """
    model_info = {
        "provider": config.llm.provider.value,
        "temperature": 0.1,
        "max_tokens": 1000,
    }
    
    if config.llm.provider == LLMProvider.OLLAMA:
        model_info.update({
            "base_url": config.llm.ollama_base_url,
            "model": config.llm.ollama_model,
        })
    elif config.llm.provider == LLMProvider.OPENAI:
        model_info.update({
            "model": "gpt-4o-mini",
            "api_key_configured": bool(config.llm.openai_api_key),
        })
    elif config.llm.provider == LLMProvider.CLAUDE:
        model_info.update({
            "model": "claude-3-haiku-20240307",
            "api_key_configured": bool(config.llm.anthropic_api_key),
        })
    
    return model_info


# Create default LLM instance
def get_default_llm() -> Any:
    """
    Get the default configured LLM instance.

    Returns:
        Any: Default LLM instance based on current settings.
    """
    return create_llm()