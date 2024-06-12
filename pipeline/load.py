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
            botanist_id = row['botanist_id']

            if not botanist_exists(schema, botanist_id):
                cursor.execute(
                    f"""INSERT INTO {schema}.botanists (first_name, last_name, email, phone_number)
                    VALUES (%s, %s, %s, %s)""", botanists_df.apply(tuple, axis=1).tolist())
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
            f"""INSERT INTO {schema}.readings (plant_id, botanist_id, reading_at, moisture, temp, watered_at)
            VALUES (%s, %s, %s, %s, %s, %s)""", readings_df.apply(tuple, axis=1).tolist())
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":

    botanist_sample_data = pd.DataFrame([{
        'botanist_id': 4,
        'first_name': ['Eliza'],
        'last_name': ['Andrews'],
        'email': ['eliza.andrews@lnhm.co.uk'],
        'phone_number': ['(846)669-6651x75948'],
    },
        {
        'botanist_id': 4,
        'first_name': ['Eliza'],
        'last_name': ['Andrews'],
        'email': ['eliza.andrews@lnhm.co.uk'],
        'phone_number': ['(846)669-6651x75948'],
    }])

    reading_sample_data = pd.DataFrame([{
        "plant_id": 1,
        "botanist_id": 2,
        "reading_at": "2024-06-12 11:17:55",
        "moisture": 26.6547137768116,
        "temp": 10.588249721728,
        "watered_at": "2024-06-11 14:12:43"
    },
        {
        "plant_id": 2,
        "botanist_id": 3,
        "reading_at": "2024-06-12 11:17:55",
        "moisture": 26.6547137768116,
        "temp": 10.588249721728,
        "watered_at": "2024-06-11 14:12:43"}])

    populate_readings(reading_sample_data, DB_SCHEMA)

    populate_botanists(botanist_sample_data, DB_SCHEMA)
