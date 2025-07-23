"""Test suite for utility modules."""

import os
from datetime import datetime, time
from unittest.mock import Mock, patch

import pytest
import pytz

from src.utils.datetime_utils import (
    DateTimeParsingError,
    get_current_time,
    get_timezone,
    is_recent,
    parse_datetime,
    parse_time_only,
    to_iso_string,
)
from src.utils.airtable_client import (
    AirtableClient,
    AirtableError,
    BodyLogRecord,
    HeartLogRecord,
)


class TestDateTimeUtils:
    """Test datetime utility functions."""

    def test_get_timezone_default(self):
        """Test getting the default Central Time timezone."""
        tz = get_timezone()
        assert str(tz) == "America/Chicago"

    def test_get_current_time(self):
        """Test getting current time in configured timezone."""
        current = get_current_time()
        assert current.tzinfo is not None
        assert str(current.tzinfo) == "America/Chicago"

    def test_parse_datetime_current_when_none(self):
        """Test that parse_datetime returns current time when input is None."""
        result = parse_datetime(None)
        assert result.tzinfo is not None
        assert isinstance(result, datetime)

    def test_parse_datetime_explicit_time(self):
        """Test parsing explicit datetime string."""
        result = parse_datetime("2024-01-15 14:30:00")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_relative_datetime_yesterday(self):
        """Test parsing relative time expressions like 'yesterday'."""
        result = parse_datetime("yesterday")
        now = get_current_time()
        assert result.date() == (now.date().replace(day=now.day - 1))

    def test_parse_relative_datetime_this_morning(self):
        """Test parsing 'this morning' relative time."""
        result = parse_datetime("this morning")
        assert result.hour == 8
        assert result.minute == 0

    def test_parse_datetime_with_at_time(self):
        """Test parsing relative time with specific time (e.g., 'yesterday at 3pm')."""
        result = parse_datetime("yesterday at 3pm")
        assert result.hour == 15
        assert result.minute == 0

    def test_parse_datetime_invalid_string(self):
        """Test that invalid datetime strings raise DateTimeParsingError."""
        with pytest.raises(DateTimeParsingError):
            parse_datetime("not a date")

    def test_parse_time_only_valid(self):
        """Test parsing time-only strings."""
        result = parse_time_only("3:30pm")
        assert result.hour == 15
        assert result.minute == 30

    def test_parse_time_only_invalid(self):
        """Test parsing invalid time strings returns None."""
        result = parse_time_only("not a time")
        assert result is None

    def test_to_iso_string(self):
        """Test converting datetime to ISO string."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        dt_with_tz = get_timezone().localize(dt)
        result = to_iso_string(dt_with_tz)
        assert "2024-01-15T14:30:00" in result
        assert "-06:00" in result or "-05:00" in result  # Account for DST

    def test_is_recent_true(self):
        """Test that recent datetime is identified as recent."""
        now = get_current_time()
        assert is_recent(now, hours=1)

    def test_is_recent_false(self):
        """Test that old datetime is identified as not recent."""
        now = get_current_time()
        old_time = now.replace(year=now.year - 1)
        assert not is_recent(old_time, hours=1)


class TestAirtableClient:
    """Test Airtable client functionality."""

    def test_initialization_missing_config(self):
        """Test that initialization fails with missing configuration."""
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = ""
            mock_settings.airtable.base_id = ""
            
            with pytest.raises(AirtableError):
                AirtableClient(config=mock_settings)

    @patch('src.utils.airtable_client.Api')
    def test_initialization_success(self, mock_api):
        """Test successful initialization with valid configuration."""
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            client = AirtableClient()
            assert client is not None

    @patch('src.utils.airtable_client.Api')
    def test_write_heart_log_success(self, mock_api):
        """Test successful heart rate logging."""
        # Setup mocks
        mock_table = Mock()
        mock_table.create.return_value = {"id": "test_record_id"}
        mock_base = Mock()
        mock_base.table.return_value = mock_table
        mock_api_instance = Mock()
        mock_api_instance.base.return_value = mock_base
        mock_api.return_value = mock_api_instance
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            mock_settings.airtable.heart_log_table = "heart_log"
            
            client = AirtableClient()
            
            record = HeartLogRecord(
                timestamp=datetime.now(),
                systolic_bp=120,
                diastolic_bp=80,
                heart_rate=72
            )
            
            result = client.write_heart_log(record)
            assert result == "test_record_id"
            mock_table.create.assert_called_once()

    @patch('src.utils.airtable_client.Api')
    def test_write_body_log_success(self, mock_api):
        """Test successful body composition logging."""
        # Setup mocks
        mock_table = Mock()
        mock_table.create.return_value = {"id": "test_record_id"}
        mock_base = Mock()
        mock_base.table.return_value = mock_table
        mock_api_instance = Mock()
        mock_api_instance.base.return_value = mock_base
        mock_api.return_value = mock_api_instance
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            mock_settings.airtable.body_log_table = "body_log"
            
            client = AirtableClient()
            
            record = BodyLogRecord(
                timestamp=datetime.now(),
                weight=175.2,
                body_fat_percentage=15.5
            )
            
            result = client.write_body_log(record)
            assert result == "test_record_id"
            mock_table.create.assert_called_once()

    @patch('src.utils.airtable_client.Api')
    def test_create_record_failure(self, mock_api):
        """Test that create_record failures raise AirtableError."""
        # Setup mocks to simulate failure
        mock_table = Mock()
        mock_table.create.side_effect = Exception("API Error")
        mock_base = Mock()
        mock_base.table.return_value = mock_table
        mock_api_instance = Mock()
        mock_api_instance.base.return_value = mock_base
        mock_api.return_value = mock_api_instance
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            mock_settings.airtable.heart_log_table = "heart_log"
            
            client = AirtableClient()
            
            record = HeartLogRecord(
                timestamp=datetime.now(),
                heart_rate=72
            )
            
            with pytest.raises(AirtableError):
                client.write_heart_log(record)

    @patch('src.utils.airtable_client.Api')
    def test_test_connection_success(self, mock_api):
        """Test successful connection test."""
        # Setup mocks
        mock_base = Mock()
        mock_base.schema.return_value = {}
        mock_api_instance = Mock()
        mock_api_instance.base.return_value = mock_base
        mock_api.return_value = mock_api_instance
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            client = AirtableClient()
            result = client.test_connection()
            assert result is True

    @patch('src.utils.airtable_client.Api')
    def test_test_connection_failure(self, mock_api):
        """Test connection test failure raises AirtableError."""
        # Setup mocks to simulate failure
        mock_base = Mock()
        mock_base.schema.side_effect = Exception("Connection failed")
        mock_api_instance = Mock()
        mock_api_instance.base.return_value = mock_base
        mock_api.return_value = mock_api_instance
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.airtable.personal_access_token = "test_token"
            mock_settings.airtable.base_id = "test_base"
            
            client = AirtableClient()
            with pytest.raises(AirtableError):
                client.test_connection()