"This file cleans and processes plant data into a DataFrame "
import pandas as pd
import re


def extract_plant_data(plant_data: dict) -> dict:
    """ Extracts all the relevant data from the API for a single plant"""
    botanists_info = plant_data.get('botanist')
    location_info = plant_data.get('origin_location')
    scientific_name = plant_data.get('scientific_name')
    data = {
        "first_name": botanists_info.get('name').split()[0],
        "last_name": botanists_info.get('name').split()[1],
        "email": botanists_info.get('email'),
        "phone_number": botanists_info.get('phone'),
        "plant_id": plant_data.get('plant_id'),
        "common_name": plant_data.get('name'),
        "scientific_name": scientific_name[0] if scientific_name else None,
        "reading_at": plant_data.get('recording_taken'),
        "temperature": plant_data.get('temperature'),
        "moisture": plant_data.get('soil_moisture'),
        "watered_at": plant_data.get('last_watered'),
        "location_name": location_info[2],
        "location_lat": location_info[0],
        "location_lon": location_info[1],
        "country_code": location_info[3],
        "timezone": location_info[4]
    }
    return data


def create_plants_df(plants: list[dict]) -> pd.DataFrame:
    """Created a DataFrame from a list of plant dictionaries"""
    dataset = []
    for plant in plants:
        if not plant.get('error'):
            dataset.append(extract_plant_data(plant))
    plant_df = pd.DataFrame(dataset)
    return plant_df


def format_phone_number(number: str) -> str:
    """Formats phone numbers so they consist of numbers"""
    return re.sub(r'[^\d]', "", number)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the data by changing to appropriate data types"""
    string_cols = ["first_name", "last_name", "email",
                   "phone_number", "common_name", "scientific_name"]
    df[string_cols] = df[string_cols].astype(str)
    df['watered_at'] = pd.to_datetime(df['watered_at'])
    df['reading_at'] = pd.to_datetime(df['reading_at'])
    df['phone_number'] = df['phone_number'].apply(format_phone_number)
    return df


def transform(plants: list[dict]) -> tuple:
    """Transforms plant data into a clean and useable DataFrame """

    df = create_plants_df(plants)
    plants_df = clean_data(df)

    botanists = plants_df[['first_name', 'last_name', 'phone_number', 'email']]
    plants = plants_df[['plant_id', 'common_name', 'scientific_name']]
    readings = plants_df[['plant_id', 'reading_at', 'moisture',
                         'temperature', 'watered_at', 'email']]
    locations = plants_df[['location_name', 'location_lat',
                          'location_lon', 'country_code', 'timezone']]

    return botanists, plants, readings, locations


if __name__ == '__main__':
    data = transform()
    print(data)
