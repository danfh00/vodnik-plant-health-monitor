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


def fetch_botanists_data() -> pd.DataFrame:
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    """Fetch botanists data from the database and return it as a DataFrame"""
    cursor.execute(
        "SELECT botanists_id AS botanist_id, email FROM gamma.botanists")
    botanists_data = cursor.fetchall()
    return pd.DataFrame(botanists_data, columns=['botanist_id', 'email'])


def insert_new_botanists(new_botanists_df: pd.DataFrame) -> None:
    """Inserts new botanists into the database"""
    conn = create_connection(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()
    new_botanists_df = new_botanists_df[[
        'first_name', 'last_name', 'phone_number', 'email']].dropna().drop_duplicates()
    print(new_botanists_df)
    cursor.executemany(
        """INSERT INTO gamma.botanists (first_name, last_name, phone_number, email)
        VALUES (%s, %s, %s, %s)""", new_botanists_df.apply(tuple, axis=1).tolist())
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


def check_for_new_plants():
    ...


def check_for_new_botanist(readings_df: pd.DataFrame, botanists: pd.DataFrame):
    "Checks if there are any new botanists in the dataframe and not in the database, adding any new ones"
    botanists_id_df = fetch_botanists_data()

    new_botanists_df = pd.merge(readings_df[['email']].drop_duplicates(
    ), botanists_id_df, on='email', how='left', indicator=True)

    new_botanists_df = new_botanists_df[new_botanists_df['_merge'] == 'left_only'].drop(columns=[
                                                                                        '_merge'])

    new_botanists_df = pd.merge(
        new_botanists_df, botanists, on='email', how='left')
    print(new_botanists_df)

    if not new_botanists_df.empty:
        insert_new_botanists(new_botanists_df)


def populate_readings(readings_df: pd.DataFrame, botanists: pd.DataFrame, schema: str) -> None:
    """Populates the readings table"""
    conn = create_connection(DB_HOST, DB_USERNAME,
                             DB_PASSWORD, DB_NAME)
    cursor = conn.cursor()

    try:
        # check_for_new_botanist(readings_df, botanists)

        botanists_id_df = fetch_botanists_data()

        merged_df = pd.merge(readings_df, botanists_id_df,
                             on='email', how='left')
        merged_df = merged_df.rename(columns={'temperature': 'temp'})
        readings_data = merged_df[['plant_id', 'reading_at', 'moisture', 'temp', 'botanist_id',
                                   'watered_at']]

        cursor.executemany(
            f"""INSERT INTO {schema}.readings (plant_id, reading_at, moisture, temp, botanist_id, watered_at)
            VALUES (%s, %s, %s, %s, %s, %s)""", readings_data.apply(tuple, axis=1).tolist())
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def load(data):

    botanists, plants, readings, locations = data

    populate_readings(readings, botanists, DB_SCHEMA)


if __name__ == "__main__":

    load()
