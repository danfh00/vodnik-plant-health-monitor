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


def add_botanist(schema: str, data: dict) -> None:
    """Adds a new botanist to the botanists table"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    botanist = (
        data['first_name'],
        data['last_name'],
        data['email'],
        data['phone_number']
    )

    try:
        cursor.execute(
            f"""INSERT INTO {schema}.botanists (first_name, last_name, email, phone_number)
            VALUES (%s, %s, %s, %s)""", botanist)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_botanist_id(schema: str, email: str) -> int:
    """Retrieves the botanist_id for a botanist given their email"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT botanists_id FROM {schema}.botanists
                   WHERE email = %s""", (email,))
    return cursor.fetchone()[0]


def populate_botanists(botanists_df: pd.DataFrame, schema: str) -> None:
    """Populates the botanists table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.executemany(
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

    botanist_data = pd.DataFrame({
        'botanist_id': 2,
        'first_name': ['Eliza'],
        'last_name': ['Andrews'],
        'email': ['eliza.andrews@lnhm.co.uk'],
        'phone_number': ['(846)669-6651x75948'],
    },
        {
        'botanist_id': 3,
        'first_name': ['Eliza'],
        'last_name': ['Andrews'],
        'email': ['eliza.andrews@lnhm.co.uk'],
        'phone_number': ['(846)669-6651x75948'],
    })

    # location_data = pd.DataFrame({
    #     location_id SMALLINT IDENTITY(1, 1) PRIMARY KEY,
    #     location_name VARCHAR(50) NOT NULL,
    #     location_lat DECIMAL(10, 7) NOT NULL,
    #     location_lon DECIMAL(10, 7) NOT NULL,
    #     timezone_id SMALLINT NOT NULL,
    #     country_code_id SMALLINT NOT NULL, })

    reading_data = pd.DataFrame({
        "plant_id": 1,
        "reading_at": "2024-06-12 11:17:55",
        "moisture": 26.6547137768116,
        "temp": 10.588249721728,
        "watered_at": "2024-06-11 14:12:43"
    },
        {
        "plant_id": 2,
        "reading_at": "2024-06-12 11:17:55",
        "moisture": 26.6547137768116,
        "temp": 10.588249721728,
        "watered_at": "2024-06-11 14:12:43"})

    populate_readings(reading_data, DB_SCHEMA)

    populate_botanists(botanist_data, DB_SCHEMA)
