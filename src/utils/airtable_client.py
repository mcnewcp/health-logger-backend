"""Airtable API client wrapper for health logging."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pyairtable import Api
from pyairtable.api.types import RecordDict
from pydantic import BaseModel, Field

from ..config.settings import Settings, settings


class AirtableError(Exception):
    """Exception raised when Airtable operations fail."""
    
    pass


class HealthRecord(BaseModel):
    """Base class for health records."""
    
    timestamp: datetime = Field(..., description="When the measurement was taken")
    notes: Optional[str] = Field(default=None, description="Optional notes")


class HeartLogRecord(HealthRecord):
    """Heart rate and blood pressure record."""
    
    systolic_bp: Optional[int] = Field(default=None, description="Systolic blood pressure (mmHg)")
    diastolic_bp: Optional[int] = Field(default=None, description="Diastolic blood pressure (mmHg)")
    heart_rate: Optional[int] = Field(default=None, description="Heart rate (bpm)")


class BodyLogRecord(HealthRecord):
    """Body composition record."""
    
    weight: Optional[float] = Field(default=None, description="Weight (lbs)")
    muscle_mass: Optional[float] = Field(default=None, description="Muscle mass (lbs)")
    body_fat_percentage: Optional[float] = Field(default=None, description="Body fat percentage")
    water_percentage: Optional[float] = Field(default=None, description="Water percentage")


class NutritionLogRecord(HealthRecord):
    """Nutrition tracking record."""
    
    food_item: str = Field(..., description="Food or drink item")
    calories: Optional[int] = Field(default=None, description="Calories")
    protein_g: Optional[float] = Field(default=None, description="Protein (grams)")
    carbs_g: Optional[float] = Field(default=None, description="Carbohydrates (grams)")
    fat_g: Optional[float] = Field(default=None, description="Fat (grams)")
    sodium_mg: Optional[float] = Field(default=None, description="Sodium (mg)")
    fiber_g: Optional[float] = Field(default=None, description="Fiber (grams)")


class CaffeineLogRecord(HealthRecord):
    """Caffeine consumption record."""
    
    source: str = Field(..., description="Caffeine source (coffee, tea, etc.)")
    caffeine_mg: float = Field(..., description="Caffeine content (mg)")


class AlcoholLogRecord(HealthRecord):
    """Alcohol consumption record."""
    
    drink_type: str = Field(..., description="Type of alcoholic drink")
    volume_oz: Optional[float] = Field(default=None, description="Volume (oz)")
    alcohol_content: Optional[float] = Field(default=None, description="Alcohol percentage")
    units: Optional[float] = Field(default=None, description="Standard alcohol units")


class SaunaLogRecord(HealthRecord):
    """Sauna session record."""
    
    duration_minutes: int = Field(..., description="Session duration (minutes)")
    temperature_f: Optional[int] = Field(default=None, description="Temperature (°F)")


class AirtableClient:
    """Client for interacting with Airtable health logging tables."""
    
    def __init__(self, config: Settings = settings):
        """
        Initialize the Airtable client.

        Args:
            config (Settings): Application configuration containing Airtable settings.
        
        Raises:
            AirtableError: If Airtable configuration is invalid.
        """
        self.config = config
        
        if not config.airtable.personal_access_token or not config.airtable.base_id:
            raise AirtableError("Airtable PAT and Base ID are required")
        
        try:
            self.api = Api(config.airtable.personal_access_token)
            self.base = self.api.base(config.airtable.base_id)
        except Exception as e:
            raise AirtableError(f"Failed to initialize Airtable client: {e}") from e
    
    def write_heart_log(self, record: HeartLogRecord) -> str:
        """
        Write a heart rate/blood pressure record to Airtable.

        Args:
            record (HeartLogRecord): Heart measurement record.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the write operation fails.
        """
        fields = {
            "Timestamp": record.timestamp.isoformat(),
        }
        
        if record.systolic_bp is not None and record.diastolic_bp is not None:
            fields["Blood Pressure"] = f"{record.systolic_bp}/{record.diastolic_bp}"
            fields["Systolic BP"] = record.systolic_bp
            fields["Diastolic BP"] = record.diastolic_bp
        
        if record.heart_rate is not None:
            fields["Heart Rate"] = record.heart_rate
        
        if record.notes:
            fields["Notes"] = record.notes
        
        return self._create_record(self.config.airtable.heart_log_table, fields)
    
    def write_body_log(self, record: BodyLogRecord) -> str:
        """
        Write a body composition record to Airtable.

        Args:
            record (BodyLogRecord): Body measurement record.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the write operation fails.
        """
        fields = {
            "Timestamp": record.timestamp.isoformat(),
        }
        
        if record.weight is not None:
            fields["Weight (lbs)"] = record.weight
        
        if record.muscle_mass is not None:
            fields["Muscle Mass (lbs)"] = record.muscle_mass
        
        if record.body_fat_percentage is not None:
            fields["Body Fat %"] = record.body_fat_percentage
        
        if record.water_percentage is not None:
            fields["Water %"] = record.water_percentage
        
        if record.notes:
            fields["Notes"] = record.notes
        
        return self._create_record(self.config.airtable.body_log_table, fields)
    
    def write_nutrition_log(self, record: NutritionLogRecord) -> str:
        """
        Write a nutrition record to Airtable.

        Args:
            record (NutritionLogRecord): Nutrition record.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the write operation fails.
        """
        fields = {
            "Timestamp": record.timestamp.isoformat(),
            "Food Item": record.food_item,
        }
        
        if record.calories is not None:
            fields["Calories"] = record.calories
        
        if record.protein_g is not None:
            fields["Protein (g)"] = record.protein_g
        
        if record.carbs_g is not None:
            fields["Carbs (g)"] = record.carbs_g
        
        if record.fat_g is not None:
            fields["Fat (g)"] = record.fat_g
        
        if record.sodium_mg is not None:
            fields["Sodium (mg)"] = record.sodium_mg
        
        if record.fiber_g is not None:
            fields["Fiber (g)"] = record.fiber_g
        
        if record.notes:
            fields["Notes"] = record.notes
        
        return self._create_record(self.config.airtable.nutrition_log_table, fields)
    
    def write_caffeine_log(self, record: CaffeineLogRecord) -> str:
        """
        Write a caffeine consumption record to Airtable.

        Args:
            record (CaffeineLogRecord): Caffeine consumption record.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the write operation fails.
        """
        fields = {
            "Timestamp": record.timestamp.isoformat(),
            "Source": record.source,
            "Caffeine (mg)": record.caffeine_mg,
        }
        
        if record.notes:
            fields["Notes"] = record.notes
        
        return self._create_record(self.config.airtable.caffeine_log_table, fields)
    
    def write_alcohol_log(self, record: AlcoholLogRecord) -> str:
        """
        Write an alcohol consumption record to Airtable.

        Args:
            record (AlcoholLogRecord): Alcohol consumption record.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the write operation fails.
        """
        fields = {
            "Timestamp": record.timestamp.isoformat(),
            "Drink Type": record.drink_type,
        }
        
        if record.volume_oz is not None:
            fields["Volume (oz)"] = record.volume_oz
        
        if record.alcohol_content is not None:
            fields["Alcohol %"] = record.alcohol_content
        
        if record.units is not None:
            fields["Standard Units"] = record.units
        
        if record.notes:
            fields["Notes"] = record.notes
        
        return self._create_record(self.config.airtable.alcohol_log_table, fields)
    
    def write_sauna_log(self, record: SaunaLogRecord) -> str:
        """
        Write a sauna session record to Airtable.

        Args:
            record (SaunaLogRecord): Sauna session record.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the write operation fails.
        """
        fields = {
            "Timestamp": record.timestamp.isoformat(),
            "Duration (min)": record.duration_minutes,
        }
        
        if record.temperature_f is not None:
            fields["Temperature (°F)"] = record.temperature_f
        
        if record.notes:
            fields["Notes"] = record.notes
        
        return self._create_record(self.config.airtable.sauna_log_table, fields)
    
    def _create_record(self, table_name: str, fields: Dict[str, Any]) -> str:
        """
        Create a record in the specified table.

        Args:
            table_name (str): Name of the Airtable table.
            fields (Dict[str, Any]): Record fields to create.

        Returns:
            str: Record ID of the created record.

        Raises:
            AirtableError: If the create operation fails.
        """
        try:
            table = self.base.table(table_name)
            created_record = table.create(fields)
            return created_record["id"]
        except Exception as e:
            raise AirtableError(f"Failed to create record in {table_name}: {e}") from e
    
    def test_connection(self) -> bool:
        """
        Test the connection to Airtable by attempting to list tables.

        Returns:
            bool: True if connection is successful.

        Raises:
            AirtableError: If connection test fails.
        """
        try:
            # Try to access the base schema to test connection
            self.base.schema()
            return True
        except Exception as e:
            raise AirtableError(f"Airtable connection test failed: {e}") from e