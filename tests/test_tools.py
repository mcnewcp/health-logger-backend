"""Test suite for agent tools."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.agent.tools import (
    write_alcohol_log,
    write_body_log,
    write_caffeine_log,
    write_heart_log,
    write_nutrition_log,
    write_sauna_log,
    get_all_tools,
)


class TestHeartLogTool:
    """Test the write_heart_log tool."""

    @patch('src.agent.tools.AirtableClient')
    def test_write_heart_log_success(self, mock_client_class):
        """Test successful heart rate logging."""
        # Setup mock
        mock_client = Mock()
        mock_client.write_heart_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        # Test with both BP and heart rate
        result = write_heart_log.invoke({
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72
        })
        
        assert "Successfully logged heart data" in result
        assert "120/80 mmHg" in result
        assert "72 bpm" in result
        assert "test_record_id" in result
        mock_client.write_heart_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_heart_log_heart_rate_only(self, mock_client_class):
        """Test logging heart rate without blood pressure."""
        # Setup mock
        mock_client = Mock()
        mock_client.write_heart_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_heart_log.invoke({"heart_rate": 75})
        
        assert "Successfully logged heart data" in result
        assert "75 bpm" in result
        mock_client.write_heart_log.assert_called_once()

    def test_write_heart_log_no_data(self):
        """Test that providing no measurements returns error."""
        result = write_heart_log.invoke({})
        assert "Error: At least one measurement" in result

    @patch('src.agent.tools.AirtableClient')
    def test_write_heart_log_with_timestamp(self, mock_client_class):
        """Test heart rate logging with custom timestamp."""
        mock_client = Mock()
        mock_client.write_heart_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_heart_log.invoke({
            "heart_rate": 72,
            "timestamp": "yesterday at 8am"
        })
        
        assert "Successfully logged heart data" in result
        mock_client.write_heart_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_heart_log_client_error(self, mock_client_class):
        """Test handling of Airtable client errors."""
        mock_client = Mock()
        mock_client.write_heart_log.side_effect = Exception("Airtable error")
        mock_client_class.return_value = mock_client
        
        result = write_heart_log.invoke({"heart_rate": 72})
        
        assert "Error logging heart data" in result


class TestBodyLogTool:
    """Test the write_body_log tool."""

    @patch('src.agent.tools.AirtableClient')
    def test_write_body_log_success(self, mock_client_class):
        """Test successful body composition logging."""
        mock_client = Mock()
        mock_client.write_body_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_body_log.invoke({
            "weight": 175.2,
            "body_fat_percentage": 15.5,
            "muscle_mass": 145.0
        })
        
        assert "Successfully logged body data" in result
        assert "weight: 175.2 lbs" in result
        assert "body fat: 15.5%" in result
        assert "muscle mass: 145.0 lbs" in result
        mock_client.write_body_log.assert_called_once()

    def test_write_body_log_no_data(self):
        """Test that providing no measurements returns error."""
        result = write_body_log.invoke({})
        assert "Error: At least one body measurement must be provided" in result

    @patch('src.agent.tools.AirtableClient')
    def test_write_body_log_weight_only(self, mock_client_class):
        """Test logging only weight measurement."""
        mock_client = Mock()
        mock_client.write_body_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_body_log.invoke({"weight": 170.0})
        
        assert "Successfully logged body data" in result
        assert "weight: 170.0 lbs" in result
        mock_client.write_body_log.assert_called_once()


class TestNutritionLogTool:
    """Test the write_nutrition_log tool."""

    @patch('src.agent.tools.AirtableClient')
    def test_write_nutrition_log_success(self, mock_client_class):
        """Test successful nutrition logging."""
        mock_client = Mock()
        mock_client.write_nutrition_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_nutrition_log.invoke({
            "food_item": "Protein shake",
            "calories": 150,
            "protein_g": 25.0,
            "carbs_g": 5.0
        })
        
        assert "Successfully logged nutrition" in result
        assert "Protein shake" in result
        assert "150 cal" in result
        assert "25.0g protein" in result
        mock_client.write_nutrition_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_nutrition_log_food_only(self, mock_client_class):
        """Test logging food item without nutritional details."""
        mock_client = Mock()
        mock_client.write_nutrition_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_nutrition_log.invoke({"food_item": "Apple"})
        
        assert "Successfully logged nutrition" in result
        assert "Apple" in result
        mock_client.write_nutrition_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_nutrition_log_error(self, mock_client_class):
        """Test handling of nutrition logging errors."""
        mock_client = Mock()
        mock_client.write_nutrition_log.side_effect = Exception("Database error")
        mock_client_class.return_value = mock_client
        
        result = write_nutrition_log.invoke({"food_item": "Test food"})
        
        assert "Error logging nutrition data" in result


class TestCaffeineLogTool:
    """Test the write_caffeine_log tool."""

    @patch('src.agent.tools.AirtableClient')
    def test_write_caffeine_log_success(self, mock_client_class):
        """Test successful caffeine logging."""
        mock_client = Mock()
        mock_client.write_caffeine_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_caffeine_log.invoke({
            "source": "Coffee",
            "caffeine_mg": 95.0
        })
        
        assert "Successfully logged caffeine" in result
        assert "Coffee" in result
        assert "95.0mg" in result
        mock_client.write_caffeine_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_caffeine_log_with_timestamp(self, mock_client_class):
        """Test caffeine logging with custom timestamp."""
        mock_client = Mock()
        mock_client.write_caffeine_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_caffeine_log.invoke({
            "source": "Green tea",
            "caffeine_mg": 40.0,
            "timestamp": "this morning"
        })
        
        assert "Successfully logged caffeine" in result
        assert "Green tea" in result
        mock_client.write_caffeine_log.assert_called_once()


class TestAlcoholLogTool:
    """Test the write_alcohol_log tool."""

    @patch('src.agent.tools.AirtableClient')
    def test_write_alcohol_log_success(self, mock_client_class):
        """Test successful alcohol logging."""
        mock_client = Mock()
        mock_client.write_alcohol_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_alcohol_log.invoke({
            "drink_type": "Red wine",
            "volume_oz": 5.0,
            "alcohol_content": 13.0
        })
        
        assert "Successfully logged alcohol" in result
        assert "Red wine" in result
        assert "5.0oz" in result
        assert "13.0% ABV" in result
        mock_client.write_alcohol_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_alcohol_log_minimal(self, mock_client_class):
        """Test alcohol logging with minimal information."""
        mock_client = Mock()
        mock_client.write_alcohol_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_alcohol_log.invoke({"drink_type": "Beer"})
        
        assert "Successfully logged alcohol" in result
        assert "Beer" in result
        mock_client.write_alcohol_log.assert_called_once()


class TestSaunaLogTool:
    """Test the write_sauna_log tool."""

    @patch('src.agent.tools.AirtableClient')
    def test_write_sauna_log_success(self, mock_client_class):
        """Test successful sauna logging."""
        mock_client = Mock()
        mock_client.write_sauna_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_sauna_log.invoke({
            "duration_minutes": 20,
            "temperature_f": 180
        })
        
        assert "Successfully logged sauna session" in result
        assert "20 minutes" in result
        assert "180°F" in result
        mock_client.write_sauna_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_sauna_log_duration_only(self, mock_client_class):
        """Test sauna logging with duration only."""
        mock_client = Mock()
        mock_client.write_sauna_log.return_value = "test_record_id"
        mock_client_class.return_value = mock_client
        
        result = write_sauna_log.invoke({"duration_minutes": 15})
        
        assert "Successfully logged sauna session" in result
        assert "15 minutes" in result
        mock_client.write_sauna_log.assert_called_once()

    @patch('src.agent.tools.AirtableClient')
    def test_write_sauna_log_error(self, mock_client_class):
        """Test handling of sauna logging errors."""
        mock_client = Mock()
        mock_client.write_sauna_log.side_effect = Exception("Database error")
        mock_client_class.return_value = mock_client
        
        result = write_sauna_log.invoke({"duration_minutes": 20})
        
        assert "Error logging sauna data" in result


class TestToolsGeneral:
    """Test general tool functionality."""

    def test_get_all_tools(self):
        """Test that get_all_tools returns all 6 tools."""
        tools = get_all_tools()
        
        assert len(tools) == 6
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "write_heart_log",
            "write_body_log", 
            "write_nutrition_log",
            "write_caffeine_log",
            "write_alcohol_log",
            "write_sauna_log"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_all_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        tools = get_all_tools()
        
        for tool in tools:
            assert hasattr(tool, 'description')
            assert tool.description is not None
            assert len(tool.description) > 0