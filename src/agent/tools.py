"""Health logging tools for the LangGraph agent."""

from datetime import datetime
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from ..utils.airtable_client import (
    AirtableClient,
    AlcoholLogRecord,
    BodyLogRecord,
    CaffeineLogRecord,
    HeartLogRecord,
    NutritionLogRecord,
    SaunaLogRecord,
)
from ..utils.datetime_utils import parse_datetime


class HeartLogInput(BaseModel):
    """Input schema for heart rate and blood pressure logging."""
    
    systolic_bp: Optional[int] = Field(default=None, description="Systolic blood pressure (mmHg)")
    diastolic_bp: Optional[int] = Field(default=None, description="Diastolic blood pressure (mmHg)")
    heart_rate: Optional[int] = Field(default=None, description="Heart rate (beats per minute)")
    timestamp: Optional[str] = Field(default=None, description="When the measurement was taken (optional, defaults to now)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the measurement")


class BodyLogInput(BaseModel):
    """Input schema for body composition logging."""
    
    weight: Optional[float] = Field(default=None, description="Weight in pounds")
    muscle_mass: Optional[float] = Field(default=None, description="Muscle mass in pounds")
    body_fat_percentage: Optional[float] = Field(default=None, description="Body fat percentage (0-100)")
    water_percentage: Optional[float] = Field(default=None, description="Water percentage (0-100)")
    timestamp: Optional[str] = Field(default=None, description="When the measurement was taken (optional, defaults to now)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the measurement")


class NutritionLogInput(BaseModel):
    """Input schema for nutrition logging."""
    
    food_item: str = Field(..., description="Name of the food or drink item")
    calories: Optional[int] = Field(default=None, description="Calories")
    protein_g: Optional[float] = Field(default=None, description="Protein in grams")
    carbs_g: Optional[float] = Field(default=None, description="Carbohydrates in grams")
    fat_g: Optional[float] = Field(default=None, description="Fat in grams")
    sodium_mg: Optional[float] = Field(default=None, description="Sodium in milligrams")
    fiber_g: Optional[float] = Field(default=None, description="Fiber in grams")
    timestamp: Optional[str] = Field(default=None, description="When the food was consumed (optional, defaults to now)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the meal/snack")


class CaffeineLogInput(BaseModel):
    """Input schema for caffeine logging."""
    
    source: str = Field(..., description="Source of caffeine (e.g., coffee, tea, energy drink)")
    caffeine_mg: float = Field(..., description="Caffeine content in milligrams")
    timestamp: Optional[str] = Field(default=None, description="When the caffeine was consumed (optional, defaults to now)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the caffeine consumption")


class AlcoholLogInput(BaseModel):
    """Input schema for alcohol logging."""
    
    drink_type: str = Field(..., description="Type of alcoholic beverage")
    volume_oz: Optional[float] = Field(default=None, description="Volume in fluid ounces")
    alcohol_content: Optional[float] = Field(default=None, description="Alcohol percentage (0-100)")
    units: Optional[float] = Field(default=None, description="Standard alcohol units")
    timestamp: Optional[str] = Field(default=None, description="When the alcohol was consumed (optional, defaults to now)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the drink")


class SaunaLogInput(BaseModel):
    """Input schema for sauna logging."""
    
    duration_minutes: int = Field(..., description="Duration of sauna session in minutes")
    temperature_f: Optional[int] = Field(default=None, description="Sauna temperature in Fahrenheit")
    timestamp: Optional[str] = Field(default=None, description="When the sauna session started (optional, defaults to now)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the sauna session")


@tool("write_heart_log", args_schema=HeartLogInput, return_direct=False)
def write_heart_log(
    systolic_bp: Optional[int] = None,
    diastolic_bp: Optional[int] = None,
    heart_rate: Optional[int] = None,
    timestamp: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Log heart rate and blood pressure measurements to the health database.
    
    Use this tool when users mention blood pressure (e.g., "120/80") or heart rate (e.g., "72 bpm").
    At least one measurement (blood pressure OR heart rate) must be provided.
    """
    try:
        # Validate that at least one measurement is provided
        if not any([systolic_bp, diastolic_bp, heart_rate]):
            return "Error: At least one measurement (blood pressure or heart rate) must be provided."
        
        # Parse timestamp
        parsed_time = parse_datetime(timestamp)
        
        # Create record
        record = HeartLogRecord(
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            heart_rate=heart_rate,
            timestamp=parsed_time,
            notes=notes,
        )
        
        # Write to Airtable
        client = AirtableClient()
        record_id = client.write_heart_log(record)
        
        # Format response
        measurements = []
        if systolic_bp and diastolic_bp:
            measurements.append(f"{systolic_bp}/{diastolic_bp} mmHg")
        if heart_rate:
            measurements.append(f"{heart_rate} bpm")
        
        return f"Successfully logged heart data: {', '.join(measurements)} at {parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (Record ID: {record_id})"
    
    except Exception as e:
        return f"Error logging heart data: {str(e)}"


@tool("write_body_log", args_schema=BodyLogInput, return_direct=False)
def write_body_log(
    weight: Optional[float] = None,
    muscle_mass: Optional[float] = None,
    body_fat_percentage: Optional[float] = None,
    water_percentage: Optional[float] = None,
    timestamp: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Log body composition measurements to the health database.
    
    Use this tool when users mention weight, body fat percentage, muscle mass, or water percentage.
    At least one measurement must be provided.
    """
    try:
        # Validate that at least one measurement is provided
        if not any([weight, muscle_mass, body_fat_percentage, water_percentage]):
            return "Error: At least one body measurement must be provided."
        
        # Parse timestamp
        parsed_time = parse_datetime(timestamp)
        
        # Create record
        record = BodyLogRecord(
            weight=weight,
            muscle_mass=muscle_mass,
            body_fat_percentage=body_fat_percentage,
            water_percentage=water_percentage,
            timestamp=parsed_time,
            notes=notes,
        )
        
        # Write to Airtable
        client = AirtableClient()
        record_id = client.write_body_log(record)
        
        # Format response
        measurements = []
        if weight:
            measurements.append(f"weight: {weight} lbs")
        if muscle_mass:
            measurements.append(f"muscle mass: {muscle_mass} lbs")
        if body_fat_percentage:
            measurements.append(f"body fat: {body_fat_percentage}%")
        if water_percentage:
            measurements.append(f"water: {water_percentage}%")
        
        return f"Successfully logged body data: {', '.join(measurements)} at {parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (Record ID: {record_id})"
    
    except Exception as e:
        return f"Error logging body data: {str(e)}"


@tool("write_nutrition_log", args_schema=NutritionLogInput, return_direct=False)
def write_nutrition_log(
    food_item: str,
    calories: Optional[int] = None,
    protein_g: Optional[float] = None,
    carbs_g: Optional[float] = None,
    fat_g: Optional[float] = None,
    sodium_mg: Optional[float] = None,
    fiber_g: Optional[float] = None,
    timestamp: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Log food and beverage consumption to the health database.
    
    Use this tool when users mention eating or drinking something with nutritional information.
    The food_item name is required, but nutritional details are optional.
    """
    try:
        # Parse timestamp
        parsed_time = parse_datetime(timestamp)
        
        # Create record
        record = NutritionLogRecord(
            food_item=food_item,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            sodium_mg=sodium_mg,
            fiber_g=fiber_g,
            timestamp=parsed_time,
            notes=notes,
        )
        
        # Write to Airtable
        client = AirtableClient()
        record_id = client.write_nutrition_log(record)
        
        # Format response
        nutrition_details = []
        if calories:
            nutrition_details.append(f"{calories} cal")
        if protein_g:
            nutrition_details.append(f"{protein_g}g protein")
        if carbs_g:
            nutrition_details.append(f"{carbs_g}g carbs")
        if fat_g:
            nutrition_details.append(f"{fat_g}g fat")
        
        details_str = f" ({', '.join(nutrition_details)})" if nutrition_details else ""
        return f"Successfully logged nutrition: {food_item}{details_str} at {parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (Record ID: {record_id})"
    
    except Exception as e:
        return f"Error logging nutrition data: {str(e)}"


@tool("write_caffeine_log", args_schema=CaffeineLogInput, return_direct=False)
def write_caffeine_log(
    source: str,
    caffeine_mg: float,
    timestamp: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Log caffeine consumption to the health database.
    
    Use this tool when users mention consuming caffeine from coffee, tea, energy drinks, supplements, etc.
    Both the source and caffeine amount in milligrams are required.
    """
    try:
        # Parse timestamp
        parsed_time = parse_datetime(timestamp)
        
        # Create record
        record = CaffeineLogRecord(
            source=source,
            caffeine_mg=caffeine_mg,
            timestamp=parsed_time,
            notes=notes,
        )
        
        # Write to Airtable
        client = AirtableClient()
        record_id = client.write_caffeine_log(record)
        
        return f"Successfully logged caffeine: {source} ({caffeine_mg}mg) at {parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (Record ID: {record_id})"
    
    except Exception as e:
        return f"Error logging caffeine data: {str(e)}"


@tool("write_alcohol_log", args_schema=AlcoholLogInput, return_direct=False)
def write_alcohol_log(
    drink_type: str,
    volume_oz: Optional[float] = None,
    alcohol_content: Optional[float] = None,
    units: Optional[float] = None,
    timestamp: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Log alcohol consumption to the health database.
    
    Use this tool when users mention consuming alcoholic beverages.
    The drink type is required, but volume, alcohol content, and units are optional.
    """
    try:
        # Parse timestamp
        parsed_time = parse_datetime(timestamp)
        
        # Create record
        record = AlcoholLogRecord(
            drink_type=drink_type,
            volume_oz=volume_oz,
            alcohol_content=alcohol_content,
            units=units,
            timestamp=parsed_time,
            notes=notes,
        )
        
        # Write to Airtable
        client = AirtableClient()
        record_id = client.write_alcohol_log(record)
        
        # Format response
        details = []
        if volume_oz:
            details.append(f"{volume_oz}oz")
        if alcohol_content:
            details.append(f"{alcohol_content}% ABV")
        if units:
            details.append(f"{units} units")
        
        details_str = f" ({', '.join(details)})" if details else ""
        return f"Successfully logged alcohol: {drink_type}{details_str} at {parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (Record ID: {record_id})"
    
    except Exception as e:
        return f"Error logging alcohol data: {str(e)}"


@tool("write_sauna_log", args_schema=SaunaLogInput, return_direct=False)
def write_sauna_log(
    duration_minutes: int,
    temperature_f: Optional[int] = None,
    timestamp: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Log sauna session to the health database.
    
    Use this tool when users mention sauna sessions or time spent in a sauna.
    The duration in minutes is required, but temperature is optional.
    """
    try:
        # Parse timestamp
        parsed_time = parse_datetime(timestamp)
        
        # Create record
        record = SaunaLogRecord(
            duration_minutes=duration_minutes,
            temperature_f=temperature_f,
            timestamp=parsed_time,
            notes=notes,
        )
        
        # Write to Airtable
        client = AirtableClient()
        record_id = client.write_sauna_log(record)
        
        # Format response
        temp_str = f" at {temperature_f}°F" if temperature_f else ""
        return f"Successfully logged sauna session: {duration_minutes} minutes{temp_str} at {parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (Record ID: {record_id})"
    
    except Exception as e:
        return f"Error logging sauna data: {str(e)}"


def get_all_tools():
    """
    Get all available health logging tools.
    
    Returns:
        list: List of all health logging tools for the agent.
    """
    return [
        write_heart_log,
        write_body_log,
        write_nutrition_log,
        write_caffeine_log,
        write_alcohol_log,
        write_sauna_log,
    ]