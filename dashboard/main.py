import os
import altair as alt
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


def get_locations_data(conn: pymssql.Connection) -> pd.DataFrame:
    "Returns locations data from database as a dataframe"
    query = pd.read_sql("""SELECT p.plant_id, l.location_name, l.location_lat, l.location_lon
                FROM gamma.locations AS l
                JOIN gamma.plants AS p ON l.location_id = p.location_id
                JOIN gamma.plant_species AS ps ON ps.species_id = p.species_id
                ;""", conn)
    df = pd.DataFrame(query)
    return df


def get_readings_data(conn: pymssql.Connection) -> pd.DataFrame:
    "Returns locations data from database as a dataframe"
    query = pd.read_sql("""SELECT ps.common_name, r.reading_at, r.moisture, r.temp, r.watered_at
                    FROM gamma.readings AS r
                    JOIN gamma.plants AS p ON r.plant_id = p.plant_id
                    JOIN gamma.plant_species AS ps ON p.species_id = ps.species_id;""", conn)
    df = pd.DataFrame(query)
    return df


def get_moisture_chart(data: pd.DataFrame) -> alt.Chart:
    chart = alt.Chart(data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('moisture:Q',  axis=alt.Axis(title='Moisture'))
    ).interactive()

    return chart


def get_temperature_chart(data: pd.DataFrame) -> alt.Chart:
    chart = alt.Chart(data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('temp:Q',  axis=alt.Axis(title='Temperature'))
    ).interactive()

    return chart


def build_dashboard():
    "Builds and structures the dashboard"
    conn = create_connection()
    locations_df = get_locations_data(conn)
    readings_df = get_readings_data(conn)

    st.title("LNMH Plant Health Dashboard")

    st.header('🌡️ Temperature Readings 🌡️')

    st.header('💧 Soil Moisture Readings 💧')
    st.write(get_moisture_chart(readings_df))

    # Location Map
    st.header('🌍 Origin Locations 🌍')
    st.map(data=locations_df, latitude="location_lat",
           longitude="location_lon", size=1000, zoom=2)


if __name__ == '__main__':
    load_dotenv()
    build_dashboard()
