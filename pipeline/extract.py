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


def create_connection(host: str, username: str, password: str, database_name: str, schema: str) -> pymssql.Connection:
    return pymssql.connect(server=host,
                           user=username,
                           password=password,
                           database=f"{database_name}.{schema}")


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


def get_timezone(location_data: list) -> str:
    """returns timezone from a json response object"""
    if location_data:
        return (location_data[-1])


def get_country_code(location_data: list) -> str:
    """returns timezone from a json response object"""
    if location_data:
        return (location_data[-2])


def get_unique_timezones(responses: list[str]) -> list[tuple]:
    unique_timezones = set()
    for response in responses:
        location_data = response.get('origin_location')
        unique_timezones.add(get_timezone(location_data))

    return list(unique_timezones)


def get_unique_countrycodes(responses: list[str]) -> list[tuple]:
    unique_countrycodes = set()
    for response in responses:
        location_data = response.get('origin_location')
        unique_countrycodes.add(get_timezone(location_data))

    return list(unique_countrycodes)


def populate_timezones(timezone_name: list) -> None:
    """Populates the timezones table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME, DB_SCHEMA)
    cursor = conn.cursor()

    cursor.execute()


if __name__ == '__main__':
    timezones = []
    for id in range(1, 51):
        json = get_plant_data(id)

        lat = json.get('origin_location')[0]
        lon = json.get('origin_location')[1]
        city = json.get('origin_location')[2]
        country_code = json.get('origin_location')[3]
        timezones.append(json.get('origin_location')[4])

        name = json.get('name')
        scientific_name = json.get('scientific_name')

        reading_at = json.get('recording_taken')
        moisture = json.get('soil_moisture')
        temp = json.get('temperature')
        watered_at = json.get('last_watered')
