import os
import pymssql
from dotenv import load_dotenv
import pandas as pd


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


def botanist_exists(schema: str, botanist_id: int) -> bool:
    """Checks if a botanist exists in the botanists table"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {schema}.botanists WHERE botanists_id = %s", (botanist_id,))
    return cursor.fetchone()[0] > 0


def populate_botanists(botanists_df: pd.DataFrame, schema: str) -> None:
    """Populates the botanists table if botanist_id is not already present."""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        for _, row in botanists_df.iterrows():
            botanist_id = row['botanists_id']

            if not botanist_exists(schema, botanist_id):
                cursor.execute(
                    f"""INSERT INTO {schema}.botanists (first_name, last_name, phone_number, email)
                    VALUES (%s, %s, %s, %s)""", botanists_df.apply(tuple, axis=1).tolist())
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def plant_exists(schema: str, plant_id: int) -> bool:
    """Checks if a plant exists in the plants table"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT COUNT(*) FROM {schema}.plants WHERE plant_id = %s", (plant_id,))
    return cursor.fetchone()[0] > 0


def populate_plants(plants_df: pd.DataFrame, schema: str) -> None:
    """Populates the plants table if plant_id is not already present."""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        for _, row in plants_df.iterrows():
            plant_id = row['plant_id']

            if not plant_exists(schema, plant_id):
                cursor.execute(
                    f"""INSERT INTO {schema}.plants (plant_id, common_name, scientific_name)
                    VALUES (%s, %s, %s)""", plants_df.apply(tuple, axis=1).tolist())
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def populate_readings(readings_df: pd.DataFrame, schema: str) -> None:
    """Populates the readings table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
            f"""INSERT INTO {schema}.readings (plant_id, reading_at, moisture, temp, botanists_id,  watered_at)
            VALUES (%s, %s, %s, %s, 1, %s)""", readings_df.apply(tuple, axis=1).tolist())
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def load(data):

    botanists, plants, readings, locations = data

    populate_plants(plants, DB_SCHEMA)

    populate_readings(readings, DB_SCHEMA)

    populate_botanists(botanists, DB_SCHEMA)


if __name__ == "__main__":
    load()
