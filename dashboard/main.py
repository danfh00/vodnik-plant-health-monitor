import os
import pymssql
from dotenv import load_dotenv
import pandas as pd
import streamlit as st


def create_connection() -> pymssql.Connection:
    """Creates a pymssql connection to the appropriate database"""
    return pymssql.connect(server=os.getenv('DB_HOST'),
                           user=os.getenv('DB_USER'),
                           password=os.getenv('DB_PASSWORD'),
                           database=os.getenv('DB_NAME'))


def load_readings_data(conn: pymssql.Connection) -> pd.DataFrame:
    "Returns a data from database as a dataframe"
    with conn.cursor() as cur:
        cur.execute("""SELECT r.reading_at, r.moisture, r.temp, r.watered_at
                    FROM gamma.readings AS r
                    JOIN gamma.plants AS p ON r.plant_id = p.plant_id
                    JOIN gamma.plant_species AS sp ON ps.species_id = p.species_id;""")
        data = cur.fetchall()
        df = pd.DataFrame.from_dict(data)

    return df


def build_dashboard(data: pd.DataFrame):
    "Builds and structures the dashboard"
    st.title("LNMH Plant Health Dashboard")
    st.table(data)


if __name__ == '__main__':
    load_dotenv()
    conn = create_connection()
    df = load_readings_data(conn)

    build_dashboard(df)
