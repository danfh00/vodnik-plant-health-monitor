import requests


def get_plant_data(plant_id: int) -> dict:
    """Returns plant data in json format from an API using plant ID"""
    try:
        response = requests.get(
            f"https://data-eng-plants-api.herokuapp.com/plants/{plant_id}", timeout=20)
        json = response.json()
        return json

    except requests.exceptions.Timeout:
        return {"error": "Unable to connect to the API."}


if __name__ == '__main__':
    get_plant_data(77)
