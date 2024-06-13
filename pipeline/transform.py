"This file cleans and processes plant data into a DataFrame "
import os
import pandas as pd
import re
import pymssql
from extract import extract_data
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USERNAME = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SCHEMA = os.getenv('DB_SCHEMA')


def format_phone_number(number: str) -> str:
    """Formats phone numbers so they consist of numbers"""
    return re.sub(r'[^\d]', "", number)


def create_connection(host: str, username: str, password: str, database_name: str) -> pymssql.Connection:
    """Creates a pymssql connection to the appropriate database"""
    return pymssql.connect(server=host,
                           user=username,
                           password=password,
                           database=database_name)


def check_if_botanist_in_db(email: str, schema: str, cursor: pymssql.Cursor) -> bool:
    cursor.execute(
        f"""SELECT botanists_id FROM {schema}.botanists WHERE email=%s""", (email,))

    result = cursor.fetchone()

    return result


def add_botanist_to_db(botanist_data: dict, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    first_name, last_name = tuple(botanist_data["name"].split())
    phone_number = format_phone_number(botanist_data["phone"])
    email = botanist_data["email"]

    try:
        cursor.execute(f"""INSERT INTO {
            schema}.botanists (first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s)""",
            (first_name, last_name, email, phone_number, ))

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_timezone_in_db(timezone: str, schema: str, cursor: pymssql.Cursor) -> bool:
    cursor.execute(
        f"""SELECT timezone_id FROM {schema}.timezones WHERE timezone=%s""", (timezone,))

    result = cursor.fetchone()

    return result


def add_timezone_to_db(timezone_name: dict, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new timezone to the timezones table"""
    try:
        cursor.execute(
            f"""INSERT INTO {schema}.timezones (timezone) VALUES (%s)""", timezone_name)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_country_code_in_db(cc: str, schema: str, cursor: pymssql.Cursor) -> bool:
    cursor.execute(
        f"""SELECT country_code_id FROM {schema}.country_codes WHERE country_code=%s""", (cc,))

    result = cursor.fetchone()

    return result


def add_country_code_to_db(cc: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new country code to the country_codes table"""
    try:
        cursor.execute(
            f"""INSERT INTO {schema}.country_codes (country_code) VALUES (%s)""", cc)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_location_in_db(city: str, lat: float, lon: float, schema: str, cursor: pymssql.Cursor) -> bool:
    cursor.execute(
        f"""SELECT location_id FROM {schema}.locations WHERE location_name=%s AND location_lat=%s AND location_lon=%s""", (city, lat, lon))

    result = cursor.fetchone()

    return result


def add_location_to_db(location_data: tuple, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new location to the locations table"""
    city = location_data[2]
    lat = float(location_data[0])
    lon = float(location_data[1])
    cc_id = check_if_country_code_in_db(location_data[3], schema, cursor)[0]
    timezone_id = check_if_timezone_in_db(location_data[4], schema, cursor)[0]

    try:
        cursor.execute(
            f"""INSERT INTO {
                schema}.locations (location_name, location_lat, location_lon, timezone_id, country_code_id) VALUES (%s, %s, %s, %s, %s)""",
            (city, lat, lon, timezone_id, cc_id))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_species_in_db(common_name: str, scientific_name: str, schema: str, cursor: pymssql.Cursor) -> bool:
    if scientific_name is None:
        cursor.execute(
            f"""SELECT species_id FROM {schema}.plant_species WHERE common_name=%s AND scientific_name IS NULL""", (common_name,))
    else:
        cursor.execute(
            f"""SELECT species_id FROM {schema}.plant_species WHERE common_name=%s AND scientific_name=%s""", (common_name, scientific_name))

    result = cursor.fetchone()

    return result


def add_species_to_db(common_name: str, scientific_name: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new location to the locations table"""
    try:
        cursor.execute(
            f"""INSERT INTO {
                schema}.plant_species (common_name, scientific_name) VALUES (%s, %s)""",
            (common_name, scientific_name))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_plant_in_db(plant_id: int, schema: str, cursor: pymssql.Cursor) -> bool:
    cursor.execute(f"""SELECT plant_id FROM {
                   schema}.plants WHERE plant_id = %s""", (plant_id,))

    result = cursor.fetchone()

    return result


def add_plant_to_db(plant_id: int, common_name: str, scientific_name: str, location_data: list, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new location to the locations table"""
    plant_species_id = check_if_species_in_db(
        common_name, scientific_name, schema, cursor)[0]
    location_id = check_if_location_in_db(location_data[2], float(
        location_data[0]), float(location_data[1]), schema, cursor)[0]

    try:
        cursor.execute(
            f"""INSERT INTO {schema}.plants (plant_id, species_id, location_id) VALUES (%s, %s, %s)""", (plant_id, plant_species_id, location_id))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def botanist_checks(botanist_data: dict, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    is_botanist_in_db = check_if_botanist_in_db(
        botanist_data["email"], schema, cursor)

    if is_botanist_in_db:
        return is_botanist_in_db[0]

    add_botanist_to_db(botanist_data, schema, conn, cursor)
    return check_if_botanist_in_db(
        botanist_data["email"], schema, cursor)[0]


def timezone_checks(timezone_name: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    is_timezone_in_db = check_if_timezone_in_db(timezone_name, schema, cursor)

    if not is_timezone_in_db:
        add_timezone_to_db(timezone_name, schema, conn, cursor)


def country_code_checks(cc: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    is_country_code_in_db = check_if_country_code_in_db(cc, schema, cursor)

    if not is_country_code_in_db:
        add_country_code_to_db(cc, schema, conn, cursor)


def location_checks(location_data: list, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    is_location_in_db = check_if_location_in_db(
        location_data[2], location_data[0], location_data[1], schema, cursor)

    if not is_location_in_db:
        add_location_to_db(location_data, schema, conn, cursor)


def plant_species_checks(common_name: str, scientific_name: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    is_plant_species_in_db = check_if_species_in_db(
        common_name, scientific_name, schema, cursor)

    if not is_plant_species_in_db:
        add_species_to_db(common_name, scientific_name, schema, conn, cursor)


def plant_checks(plant_id: int, common_name: str, scientific_name: str, location_data: list, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    is_plant_in_db = check_if_plant_in_db(plant_id, schema, cursor)

    if is_plant_in_db:
        return is_plant_in_db[0]

    add_plant_to_db(plant_id, common_name,
                    scientific_name, location_data, schema, conn, cursor)
    return check_if_plant_in_db(plant_id, schema, cursor)[0]


def format_recording_taken(date: str) -> datetime:
    parsed_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return parsed_date.strftime('%Y-%m-%d %H:%M:%S')


def format_watered_at(date: str) -> datetime:
    parsed_date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
    return parsed_date.strftime('%Y-%m-%d %H:%M:%S')


def add_reading_to_db(plant_id: int, reading_at: str, moisture: float, temp: float, botanist_id: int, watered_at: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the plant reading to the readings table"""
    try:
        cursor.execute(
            f"""INSERT INTO {schema}.readings (plant_id, reading_at, moisture, temp, botanist_id, watered_at) VALUES (%s, %s, %s, %s, %s, %s)""", (plant_id, reading_at, moisture, temp, botanist_id, watered_at))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


if __name__ == '__main__':
    plants = extract_data()
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    for plant in plants:
        if 'error' not in plant:
            scientific_name = plant.get("scientific_name")
            botanist_id = botanist_checks(
                plant["botanist"], DB_SCHEMA, conn, cursor)
            watered_at = plant.get("last_watered")
            temp = float(plant.get("temperature"))
            moisture = float(plant.get("soil_moisture"))
            reading_at = plant.get("recording_taken")

            timezone_checks(plant["origin_location"][4],
                            DB_SCHEMA, conn, cursor)
            country_code_checks(
                plant["origin_location"][3], DB_SCHEMA, conn, cursor)
            location_checks(plant["origin_location"], DB_SCHEMA, conn, cursor)
            plant_species_checks(plant["name"].lower(
            ), scientific_name[0].lower() if scientific_name else None, DB_SCHEMA, conn, cursor)

            plant_id = plant_checks(plant["plant_id"], plant["name"].lower(),
                                    scientific_name[0].lower() if scientific_name else None, plant["origin_location"], DB_SCHEMA, conn, cursor)

            add_reading_to_db(plant["plant_id"],
                              format_recording_taken(plant["recording_taken"]), plant["soil_moisture"], plant["temperature"], botanist_id, format_watered_at(plant["last_watered"]), DB_SCHEMA, conn, cursor)

    cursor.close()
    conn.close()
