import asyncio
import aiohttp
import os
import requests
import pymssql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USERNAME = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SCHEMA = os.getenv('DB_SCHEMA')


def create_connection(host: str, username: str, password: str, database_name: str) -> pymssql.Connection:
    return pymssql.connect(server=host,
                           user=username,
                           password=password,
                           database=database_name)


def get_plant_data(plant_id: int) -> dict:
    """Returns plant data in json format from an API using plant ID"""
    try:
        response = requests.get(
            f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}", timeout=20)
        json = response.json()
        return json

    except requests.exceptions.Timeout:
        return {"error": "Unable to connect to the API."}


async def fetch_plant_data(session, plant_id: int) -> list[dict]:
    try:
        async with session.get(f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}", timeout=20) as response:
            return await response.json()
    except TimeoutError:
        return {"error": "Unable to connect to the API."}


async def get_all_responses(plant_ids: list[int]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_plant_data(session, plant_id) for plant_id in plant_ids]
        responses = await asyncio.gather(*tasks)

    return responses


def get_unique_timezones(responses: list[str]) -> list[tuple]:
    unique_timezones = set()
    for response in responses:
        if 'error' not in response:
            location_data = response.get('origin_location')
            unique_timezones.add((location_data[4],))

    return list(unique_timezones)


def get_unique_country_codes(responses: list[str]) -> list[tuple]:
    unique_country_codes = set()
    for response in responses:
        if 'error' not in response:
            country_code_data = response.get('origin_location')
            unique_country_codes.add((country_code_data[3],))

    return list(unique_country_codes)


def get_unique_locations(responses: list[str], timezone_map: dict, country_code_map: dict) -> list[tuple]:
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
                        (location_name, location_lat, location_lon, timezone_id, country_code_id))

    return list(unique_locations)


def populate_timezones(timezone_name: list[tuple], schema: str) -> None:
    """Populates the timezones table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"INSERT INTO {schema}.timezones VALUES (%s)", timezone_name)
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
            f"INSERT INTO {schema}.country_codes VALUES (%s)", country_codes)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_timezone_id_map(schema: str) -> dict:
    '''Creates a dict of each timezone and its associated ID'''
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT timezone_id, timezone FROM {schema}.timezones")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[1]: row[0] for row in rows}


def get_country_code_id_map(schema: str) -> dict:
    '''Creates a dict of each country code and its associated ID'''
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT country_code_id, country_code FROM {
                   schema}.country_codes")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[1]: row[0] for row in rows}


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
    plant_ids = range(1, 51)
    responses = asyncio.run(get_all_responses(plant_ids))

    # timezones = get_unique_timezones(responses)
    # populate_timezones(timezones, DB_SCHEMA)

    # all_country_codes = get_unique_country_codes(responses)
    # populate_country_codes(all_country_codes, DB_SCHEMA)

    timezone_data = get_timezone_id_map(DB_SCHEMA)
    country_code_data = get_country_code_id_map(DB_SCHEMA)

    data = get_unique_locations(responses, timezone_data, country_code_data)

    populate_locations(data, DB_SCHEMA)

    # for id in range(1, 51):
    #     json = get_plant_data(id)

    #     lat = json.get('origin_location')[0]
    #     lon = json.get('origin_location')[1]
    #     city = json.get('origin_location')[2]
    #     country_code = json.get('origin_location')[3]
    #     timezones.append(json.get('origin_location')[4])

    #     name = json.get('name')
    #     scientific_name = json.get('scientific_name')

    #     reading_at = json.get('recording_taken')
    #     moisture = json.get('soil_moisture')
    #     temp = json.get('temperature')
    #     watered_at = json.get('last_watered')
