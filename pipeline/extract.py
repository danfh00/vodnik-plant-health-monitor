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
    # Botanists data
    botanists_data = plant_data.get('botanist')
    fname, lname = botanists_data.get('name').split()
    email = botanists_data.get('email')
    phone = botanists_data.get('phone')

    # Plant data
    plant_id = plant_data.get('plant_id')
    plant_name = plant_data.get('name')
    scientific_name = plant_data.get('scientific_name')

    # Reading data
    reading_at = plant_data.get('recording_taken')
    moisture = plant_data.get('soil_moisture')
    temperature = plant_data.get('temperature')
    last_watered = plant_data.get('last_watered')

    # Location data
    location_name = plant_data.get("origin_location")[2]
    latitude = plant_data.get("origin_location")[0]
    longitude = plant_data.get("origin_location")[1]
    country_code = plant_data.get("origin_location")[3]
    timezone = plant_data.get("origin_location")[4]

    data = {
        "first_name": fname,
        "last_name": lname,
        "email": email,
        "phone": phone,
        "plant_id": plant_id,
        "plant_name": plant_name,
        "scientific_name": scientific_name,
        "reading_at": reading_at,
        "temperature": temperature,
        "moisture": moisture,
        "last_watered": last_watered,
        "location_name": location_name,
        "location_lat": latitude,
        "location_lon": longitude,
        "country_code": country_code,
        "timezone": timezone
    }
    return data


def create_dataframe(plants: list[dict]) -> pd.DataFrame:
    dataset = []
    for plant in plants:
        if not plant.get('error'):
            dataset.append(get_relevant_data(plant))
    df = pd.DataFrame(dataset)
    print(df)
    # return df


if __name__ == '__main__':
    all_plant_ids = range(1, 51)
    all_responses = asyncio.run(get_all_responses(
        all_plant_ids))  # returns a list of dicts
    create_dataframe(all_responses)
