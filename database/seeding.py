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
ORIGIN_LOCATION = 'origin_location'
INDEX_OF_LAT = 0
INDEX_OF_LON = 1
INDEX_OF_NAME = 2
INDEX_OF_CC = 3
INDEX_OF_TIMEZONE = 4
NAME = 'name'
SCIENTIFIC_NAME = 'scientific_name'
ERROR = 'error'
PLANT_ID = 'plant_id'


def create_connection(host: str, username: str, password: str, database_name: str) -> pymssql.Connection:
    """Creates a pymssql connection to the appropriate database"""
    return pymssql.connect(server=host,
                           user=username,
                           password=password,
                           database=database_name)


async def fetch_plant_data(session, plant_id: int) -> dict:
    """Creates all requests and fetches all of them concurrently"""
    try:
        async with session.get(f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}", timeout=35) as response:
            return await response.json()
    except TimeoutError:
        return {"error": "Unable to connect to the API."}


async def get_all_responses(plant_ids: list[int]) -> list[dict]:
    """Combines all requests into a list of dicts"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_plant_data(session, plant_id) for plant_id in plant_ids]
        responses = await asyncio.gather(*tasks)

    return responses


def get_unique_timezones(responses: list[str]) -> list[tuple]:
    """Finds all unique timezones"""
    unique_timezones = set()

    for response in responses:
        if ERROR not in response:
            try:
                location_data = response[ORIGIN_LOCATION]
                unique_timezones.add((location_data[INDEX_OF_TIMEZONE],))
            except (KeyError, IndexError):
                continue

    return list(unique_timezones)


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


def get_unique_country_codes(responses: list[str]) -> list[tuple]:
    """Finds all unique country codes"""
    unique_country_codes = set()
    for response in responses:
        if ERROR not in response:
            try:
                location_data = response[ORIGIN_LOCATION]
                unique_country_codes.add((location_data[INDEX_OF_CC],))
            except (KeyError, IndexError):
                continue

    return list(unique_country_codes)


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


def get_unique_locations(responses: list[str], timezone_map: dict, country_code_map: dict) -> list[tuple]:
    """Finds all unique locations"""
    unique_locations = set()
    for response in responses:
        if ERROR not in response:
            try:
                location_data = response[ORIGIN_LOCATION]
                location_name = location_data[INDEX_OF_NAME]
                location_lat = float(location_data[INDEX_OF_LAT])
                location_lon = float(location_data[INDEX_OF_LON])
                timezone = location_data[INDEX_OF_TIMEZONE]
                country_code = location_data[INDEX_OF_CC]
                timezone_id = timezone_map.get(timezone)
                country_code_id = country_code_map.get(country_code)

                if timezone_id and country_code_id:
                    unique_locations.add(
                        (location_name, location_lat, location_lon, timezone_id, country_code_id),)
            except (KeyError, IndexError):
                continue

    return list(unique_locations)


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


def extract_name_and_scientific_name(plant_data: dict) -> tuple:
    """Extracts the name and scientific name from the data and formats it"""
    return (plant_data[NAME].lower(), plant_data.get(SCIENTIFIC_NAME)[0].lower() if plant_data.get(SCIENTIFIC_NAME) else None)


def get_unique_plant_names(responses: list[str]) -> list[tuple]:
    """Finds all the unique plant names"""
    unique_plant_names = set()
    for response in responses:
        if 'error' not in response and NAME in response:
            unique_plant_names.add(extract_name_and_scientific_name(response))

    return list(unique_plant_names)


def populate_plant_species(all_plant_names: list[tuple], schema: str) -> None:
    """Populates the plan_names table with the provided names"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.plant_species (common_name, scientific_name) VALUES (%s, %s)", all_plant_names)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def combine_plant_and_location_id(request_data: list[dict], plant_name_ids: dict, location_ids: dict) -> None:
    """For each plant it find its associated ID for each name and location"""
    full_data_for_plants = set()
    for plant in request_data:
        if ERROR not in plant and NAME in plant and PLANT_ID in plant:
            combined_names = extract_name_and_scientific_name(plant)
            associated_name_id = plant_name_ids.get(combined_names)

            location_data = plant.get(ORIGIN_LOCATION)
            lat_and_lon = (
                float(location_data[INDEX_OF_LAT]), float(location_data[INDEX_OF_LON]),)
            associated_location_id = location_ids.get(lat_and_lon)

            if associated_location_id and associated_name_id:
                full_data_for_plants.add(
                    (plant[PLANT_ID], associated_name_id, associated_location_id),)

    return list(full_data_for_plants)


def populate_plants(plants_data: list[tuple], schema: str) -> None:
    """Populates the plants table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.plants (plant_id, naming_id, location_id) VALUES (%s, %s, %s)", plants_data)
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
    return {(float(row[1]), float(row[2])): row[0] for row in rows}


def get_plant_names_id_map(schema: str) -> dict:
    """Creates a dict of each plant name and its associated ID"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT species_id, common_name, scientific_name FROM {
                   schema}.plant_species")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {(row[1], row[2]): row[0] for row in rows}


if __name__ == '__main__':
    all_plant_ids = range(0, 51)
    all_responses = asyncio.run(get_all_responses(all_plant_ids))

    timezones = get_unique_timezones(all_responses)
    populate_timezones(timezones, DB_SCHEMA)

    all_country_codes = get_unique_country_codes(all_responses)
    populate_country_codes(all_country_codes, DB_SCHEMA)

    timezone_mapping = get_timezone_id_map(DB_SCHEMA)
    country_code_mapping = get_country_code_id_map(DB_SCHEMA)
    location_values = get_unique_locations(
        all_responses, timezone_mapping, country_code_mapping)
    populate_locations(location_values, DB_SCHEMA)

    plant_names = get_unique_plant_names(all_responses)
    populate_plant_species(plant_names, DB_SCHEMA)

    plant_names_mapping = get_plant_names_id_map(DB_SCHEMA)
    location_mapping = get_locations_id_map(DB_SCHEMA)
    data_to_add_to_plants = combine_plant_and_location_id(
        all_responses, plant_names_mapping, location_mapping)
    populate_plants(data_to_add_to_plants, DB_SCHEMA)
