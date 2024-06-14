"""This file extracts data from a plant API."""
import asyncio
import aiohttp


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


def extract_data() -> list[dict]:
    """ Extracts data for multiple plants asynchronously."""
    all_plant_ids = range(1, 51)
    return asyncio.run(get_all_responses(all_plant_ids))
