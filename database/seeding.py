"""This file is responsible for seeding the database"""
# pylint: disable=C0301, E1101, C0116

import os
import asyncio
import aiohttp
import pymssql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USERNAME = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SCHEMA = os.getenv('DB_SCHEMA')


def create_connection(host: str, username: str, password: str, database_name: str) -> pymssql.Connection:
    """Creates a pymssql connection to the appropriate database"""
    return pymssql.connect(server=host,
                           user=username,
                           password=password,
                           database=database_name)


async def fetch_plant_data(session, plant_id: int) -> dict:
    "Creates all requests and fetches all of them concurrently"
    try:
        async with session.get(f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}", timeout=20) as response:
            return await response.json()
    except TimeoutError:
        return {"error": "Unable to connect to the API."}


async def get_all_responses(plant_ids: list[int]) -> list[dict]:
    "Combines all requests into a list of dicts"
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_plant_data(session, plant_id) for plant_id in plant_ids]
        responses = await asyncio.gather(*tasks)

    return responses


def get_unique_timezones(responses: list[str]) -> list[tuple]:
    "Finds all unique timezones"
    unique_timezones = set()
    for response in responses:
        if 'error' not in response:
            location_data = response.get('origin_location')
            unique_timezones.add((location_data[4],))

    return list(unique_timezones)


def get_unique_country_codes(responses: list[str]) -> list[tuple]:
    "Finds all unique country codes"
    unique_country_codes = set()
    for response in responses:
        if 'error' not in response:
            country_code_data = response.get('origin_location')
            unique_country_codes.add((country_code_data[3],))

    return list(unique_country_codes)


def get_unique_locations(responses: list[str], timezone_map: dict, country_code_map: dict) -> list[tuple]:
    "Finds all unique locations"
    unique_locations = set()
    for response in responses:
        if 'error' not in response:
            location_data = response.get('origin_location')
            if location_data:
                location_name = location_data[2]
                location_lat = float(location_data[0])
                location_lon = float(location_data[1])
                timezone = location_data[4]
                country_code = location_data[3]
                timezone_id = timezone_map.get(timezone)
                country_code_id = country_code_map.get(country_code)

                if timezone_id and country_code_id:
                    unique_locations.add(
                        (location_name, location_lat, location_lon, timezone_id, country_code_id),)

    return list(unique_locations)


def get_unique_plants(responses: list[str], locations_map: dict) -> list[tuple]:
    """Finds all the unique plants"""
    unique_plants = set()
    for response in responses:
        if 'error' not in response:
            name = response.get('name')
            scientific_name = response.get('scientific_name')
            location_data = response.get('origin_location')

            lat_and_lon_tuple = (
                float(location_data[0]), float(location_data[1]),)
            associated_location_id = locations_map.get(lat_and_lon_tuple)

            if associated_location_id:
                unique_plants.add(
                    (scientific_name[0] if scientific_name else scientific_name, name, associated_location_id),)

    return list(unique_plants)


def populate_timezones(timezone_name: list[tuple], schema: str) -> None:
    """Populates the timezones table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.timezones (timezone) VALUES (%s)", timezone_name)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def populate_country_codes(country_codes: list[tuple], schema: str) -> None:
    """Populates the timezones table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.country_codes (country_code) VALUES (%s)", country_codes)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def populate_plants(plant_data: list[tuple], schema: str) -> None:
    """Populates the timezones table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.plants (scientific_name, common_name, location_id) VALUES (%s, %s, %s)", plant_data)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_timezone_id_map(schema: str) -> dict:
    """Creates a dict of each timezone and its associated ID"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT timezone_id, timezone FROM {schema}.timezones")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[1]: row[0] for row in rows}


def get_country_code_id_map(schema: str) -> dict:
    """Creates a dict of each country code and its associated ID"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT country_code_id, country_code FROM {
                   schema}.country_codes")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[1]: row[0] for row in rows}


def get_locations_id_map(schema: str) -> dict:
    """Creates a dict of each location and its associated ID"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT location_id, location_lat, location_lon FROM {
                   schema}.locations")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {(float(row[1]), float(row[2]),): row[0] for row in rows}


def populate_locations(all_locations: list[tuple], schema: str) -> None:
    """Populates the locations table"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.locations (location_name, location_lat, location_lon, timezone_id, country_code_id) VALUES (%s, %s, %s, %s, %s)", all_locations)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    all_plant_ids = range(1, 51)
    all_responses = asyncio.run(get_all_responses(all_plant_ids))

    timezones = get_unique_timezones(all_responses)
    populate_timezones(timezones, DB_SCHEMA)

    all_country_codes = get_unique_country_codes(all_responses)
    populate_country_codes(all_country_codes, DB_SCHEMA)

    timezone_data = get_timezone_id_map(DB_SCHEMA)
    country_code_mapping = get_country_code_id_map(DB_SCHEMA)
    location_values = get_unique_locations(
        all_responses, timezone_data, country_code_mapping)
    populate_locations(location_values, DB_SCHEMA)

    location_mapping = get_locations_id_map(DB_SCHEMA)
    plant_values = get_unique_plants(all_responses, location_mapping)
    populate_plants(plant_values, DB_SCHEMA)
