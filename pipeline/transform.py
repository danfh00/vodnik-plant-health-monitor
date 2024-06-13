"This file cleans and processes plant data"
# pylint: disable=C0301, E1101
from datetime import datetime
import os
import re
from extract import extract_data
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USERNAME = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SCHEMA = os.getenv('DB_SCHEMA')
INDEX_OF_LAT = 0
INDEX_OF_LON = 1
INDEX_OF_NAME = 2
INDEX_OF_CC = 3
INDEX_OF_TIMEZONE = 4
ORIGIN_LOCATION = "origin_location"
NAME = "name"
SCIENTIFIC_NAME = "scientific_name"
PHONE = "PHONE"
ERROR = "error"
PLANT_ID = "plant_id"
EMAIL = "email"
BOTANIST = "botanist"
LAST_WATERED = "last_watered"
TEMPERATURE = "temperature"
SOIL_MOISTURE = "soil_moisture"
RECORDING_TAKEN = "recording_taken"


def format_phone_number(number: str) -> str:
    """Formats phone numbers so they consist of numbers"""
    return re.sub(r'[^\d]', "", number)


def format_recording_taken(date: str) -> datetime:
    """Converts a given date for 'record_taken' to datetime and then formats it correctly for storing it in the database"""
    parsed_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return parsed_date.strftime('%Y-%m-%d %H:%M:%S')


def format_watered_at(date: str) -> datetime:
    """Converts a given date for 'watered_at' to datetime and then formats it correctly for storing it in the database"""
    parsed_date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
    return parsed_date.strftime('%Y-%m-%d %H:%M:%S')


def apply_transformations(all_plant_data: dict) -> dict:
    """Applies transformation to plants and gets each value to the correct data type"""
    formatted_data = []

    for plant in all_plant_data:
        plant_scientific_name = plant[SCIENTIFIC_NAME][0].lower(
        ) if SCIENTIFIC_NAME in plant else None
        plant_name = plant[NAME].lower()
        current_plant_id = plant[PLANT_ID]

        plant_watered_at = format_watered_at(plant[LAST_WATERED])
        current_temp = float(plant[TEMPERATURE])
        current_moisture = float(plant[SOIL_MOISTURE])
        plant_reading_at = format_recording_taken(plant[RECORDING_TAKEN])
        lat = float(plant[ORIGIN_LOCATION][INDEX_OF_LAT])
        lon = float(plant[ORIGIN_LOCATION][INDEX_OF_LON])
        city_name = plant[ORIGIN_LOCATION][INDEX_OF_NAME]
        country_code = plant[ORIGIN_LOCATION][INDEX_OF_CC]
        timezone = plant[ORIGIN_LOCATION][INDEX_OF_TIMEZONE]

        formatted_data.append({"plant_id": current_plant_id, "name": plant_name, "scientific_name": plant_scientific_name,
                               "last_watered": plant_watered_at, "temperature": current_temp, "moisture": current_moisture,
                               "reading_at": plant_reading_at, "origin_location": [lat, lon, city_name, country_code, timezone]})

    return formatted_data
