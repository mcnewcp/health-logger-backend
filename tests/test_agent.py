"""Test suite for the health logging agent."""

import os
from unittest.mock import Mock, patch

import pytest

from src.agent.agent import (
    HealthLoggerAgent,
    create_health_logger_agent,
    log_health_data,
    get_default_agent,
)
from src.config.settings import Settings


class TestHealthLoggerAgent:
    """Test the HealthLoggerAgent class."""

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_initialization_success(self, mock_create_llm, mock_create_react_agent):
        """Test successful agent initialization."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            agent = HealthLoggerAgent()
            
            assert agent.llm == mock_llm
            assert agent.agent == mock_agent
            mock_create_llm.assert_called_once()
            mock_create_react_agent.assert_called_once()

    @patch('src.agent.agent.create_llm')
    def test_initialization_failure(self, mock_create_llm):
        """Test agent initialization failure."""
        mock_create_llm.side_effect = Exception("LLM initialization failed")
        
        with pytest.raises(Exception) as exc_info:
            HealthLoggerAgent()
        
        assert "Failed to initialize HealthLoggerAgent" in str(exc_info.value)

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_process_success(self, mock_create_llm, mock_create_react_agent):
        """Test successful processing of health data input."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        
        mock_response_message = Mock()
        mock_response_message.content = "Successfully logged heart data"
        
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [mock_response_message]
        }
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            agent = HealthLoggerAgent()
            result = agent.process("My blood pressure is 120/80")
            
            assert result == "Successfully logged heart data"
            mock_agent.invoke.assert_called_once()

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_process_no_response(self, mock_create_llm, mock_create_react_agent):
        """Test processing when agent returns no response."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_agent.invoke.return_value = {}
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            agent = HealthLoggerAgent()
            result = agent.process("Test input")
            
            assert "Agent completed processing but returned no response" in result

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_process_error(self, mock_create_llm, mock_create_react_agent):
        """Test processing error handling."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        
        mock_agent = Mock()
        mock_agent.invoke.side_effect = Exception("Processing error")
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            agent = HealthLoggerAgent()
            result = agent.process("Test input")
            
            assert "Error processing health data" in result

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_process_batch(self, mock_create_llm, mock_create_react_agent):
        """Test batch processing of multiple inputs."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        
        mock_response1 = Mock()
        mock_response1.content = "Logged heart data"
        mock_response2 = Mock()
        mock_response2.content = "Logged body data"
        
        mock_agent = Mock()
        mock_agent.invoke.side_effect = [
            {"messages": [mock_response1]},
            {"messages": [mock_response2]}
        ]
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            agent = HealthLoggerAgent()
            results = agent.process_batch([
                "Blood pressure 120/80",
                "Weight 175 lbs"
            ])
            
            assert len(results) == 2
            assert results[0] == "Logged heart data"
            assert results[1] == "Logged body data"

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_get_available_tools(self, mock_create_llm, mock_create_react_agent):
        """Test getting list of available tools."""
        # Setup mocks with tools that have names
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        
        mock_tool1 = Mock()
        mock_tool1.name = "write_heart_log"
        mock_tool2 = Mock()
        mock_tool2.name = "write_body_log"
        
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            with patch('src.agent.agent.get_all_tools', return_value=[mock_tool1, mock_tool2]):
                agent = HealthLoggerAgent()
                tools = agent.get_available_tools()
                
                assert "write_heart_log" in tools
                assert "write_body_log" in tools

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_get_agent_info(self, mock_create_llm, mock_create_react_agent):
        """Test getting agent configuration information."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            mock_settings.app.timezone = "America/Chicago"
            
            with patch('src.agent.agent.get_model_info', return_value={"provider": "test"}):
                agent = HealthLoggerAgent()
                info = agent.get_agent_info()
                
                assert "llm_info" in info
                assert "available_tools" in info
                assert "timezone" in info
                assert info["timezone"] == "America/Chicago"
                assert "airtable_configured" in info

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_validate_configuration_success(self, mock_create_llm, mock_create_react_agent):
        """Test successful configuration validation."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            mock_settings.validate_required_keys = Mock()
            
            with patch('src.utils.airtable_client.AirtableClient') as mock_client:
                mock_client.return_value.test_connection.return_value = True
                
                agent = HealthLoggerAgent()
                validation = agent.validate_configuration()
                
                assert validation["valid"] is True
                assert len(validation["errors"]) == 0

    @patch('src.agent.agent.create_react_agent')
    @patch('src.agent.agent.create_llm')
    def test_validate_configuration_missing_token(self, mock_create_llm, mock_create_react_agent):
        """Test configuration validation with missing Airtable token."""
        # Setup mocks
        mock_llm = Mock()
        mock_create_llm.return_value = mock_llm
        mock_agent = Mock()
        mock_create_react_agent.return_value = mock_agent
        
        # Create a mock config with missing token
        mock_config = Mock()
        mock_config.airtable.personal_access_token = ""  # Missing token
        mock_config.airtable.base_id = "test_base"
        mock_config.validate_required_keys = Mock()
        
        agent = HealthLoggerAgent(config=mock_config)
        validation = agent.validate_configuration()
        
        assert validation["valid"] is False
        assert any("Personal Access Token" in error for error in validation["errors"])


class TestFactoryAndConvenienceFunctions:
    """Test factory and convenience functions."""

    @patch('src.agent.agent.HealthLoggerAgent')
    def test_create_health_logger_agent(self, mock_agent_class):
        """Test factory function for creating agent."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        result = create_health_logger_agent()
        
        assert result == mock_agent
        mock_agent_class.assert_called_once()

    @patch('src.agent.agent.HealthLoggerAgent')
    def test_log_health_data_convenience(self, mock_agent_class):
        """Test convenience function for logging health data."""
        mock_agent = Mock()
        mock_agent.process.return_value = "Success"
        mock_agent_class.return_value = mock_agent
        
        result = log_health_data("Test input")
        
        assert result == "Success"
        mock_agent.process.assert_called_once_with("Test input")

    @patch('src.agent.agent.HealthLoggerAgent')
    async def test_log_health_data_async(self, mock_agent_class):
        """Test async convenience function."""
        mock_agent = Mock()
        mock_agent.process_async.return_value = "Success"
        mock_agent_class.return_value = mock_agent
        
        result = await log_health_data_async("Test input")
        
        assert result == "Success"
        mock_agent.process_async.assert_called_once_with("Test input")

    @patch('src.agent.agent.HealthLoggerAgent')
    def test_get_default_agent_singleton(self, mock_agent_class):
        """Test that get_default_agent returns singleton."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Clear any existing default agent
        import src.agent.agent
        src.agent.agent._default_agent = None
        
        agent1 = get_default_agent()
        agent2 = get_default_agent()
        
        assert agent1 == agent2  # Should be same instance
        mock_agent_class.assert_called_once()  # Should only create once