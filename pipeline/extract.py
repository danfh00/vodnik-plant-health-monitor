"""This file extracts data from a plant API."""
import asyncio
import aiohttp
import pandas as pd


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


def get_relevant_data(plant_data: dict) -> dict:
    """ Extracts all the relevant data from the API for a single plant"""
    botanists_data = plant_data.get('botanist')
    data = {
        "first_name": botanists_data.get('name').split()[0],
        "last_name": botanists_data.get('name').split()[1],
        "email": botanists_data.get('email'),
        "phone": botanists_data.get('phone'),
        "plant_id": plant_data.get('plant_id'),
        "plant_name": plant_data.get('name'),
        "scientific_name": plant_data.get('scientific_name'),
        "reading_at": plant_data.get('recording_taken'),
        "temperature": plant_data.get('temperature'),
        "moisture": plant_data.get('soil_moisture'),
        "last_watered": plant_data.get('last_watered'),
        "location_name": plant_data.get("origin_location")[2],
        "location_lat": plant_data.get("origin_location")[0],
        "location_lon": plant_data.get("origin_location")[1],
        "country_code": plant_data.get("origin_location")[3],
        "timezone": plant_data.get("origin_location")[4]
    }
    return data


def create_plants_dataframe(plants: list[dict]) -> pd.DataFrame:
    """Converts dictionary of plant data into a dataframe"""
    dataset = []
    for plant in plants:
        if not plant.get('error'):
            dataset.append(get_relevant_data(plant))
    plant_df = pd.DataFrame(dataset)
    return plant_df


if __name__ == '__main__':
    all_plant_ids = range(1, 51)
    all_plants = asyncio.run(get_all_responses(all_plant_ids))
    create_plants_dataframe(all_plants)
