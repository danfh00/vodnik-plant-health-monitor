import requests
import asyncio
import aiohttp


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


if __name__ == '__main__':
    plant_ids = range(1, 51)
    responses = asyncio.run(get_all_responses(plant_ids))
    print(responses)

    # timezones = get_unique_timezones(responses)
    # country_codes = get_unique_countrycodes(responses)
