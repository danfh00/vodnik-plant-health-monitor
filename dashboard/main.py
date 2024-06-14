import os
import altair as alt
import pymssql
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from extract_bucket import download_historical_data

"""
TO DO: 
- Add docstrings/ pylint score
- Run with more data to see how historical data graphs look
- Dockerise : run locally, upload, run on cloud 
"""


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


def get_moisture_chart_single_plant(data: pd.DataFrame, plant_choice: str) -> alt.Chart:
    y_min = data['moisture'].min()
    y_max = data['moisture'].max()
    data['reading_at'] = pd.to_datetime(data['reading_at'])

    moisture_data = data[data["plant_id"] == plant_choice]
    chart = alt.Chart(moisture_data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('moisture:Q', scale=alt.Scale(
            domain=[y_min-1, y_max+1]), axis=alt.Axis(title='Moisture'))
    ).properties(
        width=700,
        height=600,
    ).interactive()

    return chart


def get_temperature_chart_single_plant(data: pd.DataFrame, plant_choice) -> alt.Chart:
    y_min = data['temperature'].min()
    y_max = data['temperature'].max()

    temp_data = data[data["plant_id"] == plant_choice]
    chart = alt.Chart(temp_data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('temperature:Q', scale=alt.Scale(
            domain=[y_min, y_max]), axis=alt.Axis(title='Temperature'))
    ).properties(
        width=700,
        height=600,
    ).interactive()

    return chart


def get_latest_moisture_chart(latest_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(latest_data).mark_bar().encode(
        y=alt.Y('common_name:N', sort='-x', title='Plant name'),
        x=alt.X('moisture:Q', title='Soil Moisture'),
        color=alt.Color("moisture", scale=alt.Scale(
            scheme="blues"))
    ).properties(
        width=700,
        height=600,
    ).interactive()


def get_latest_temperature_chart(latest_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(latest_data).mark_bar().encode(
        y=alt.Y('common_name:N', sort='-x', title='Plant name'),
        x=alt.X('temp:Q', title='Temperature'),
        color=alt.Color("temp", scale=alt.Scale(
            scheme="orangered"))
    ).properties(
        width=700,
        height=600,
    ).interactive()


def build_dashboard():
    "Builds and structures the dashboard"
    conn = create_connection()
    locations_df = get_locations_data(conn)
    readings_df = get_readings_data(conn)
    historical_data = download_historical_data()

    st.title("LNMH Plant Health Dashboard🍀")

    tab_location, tab_latest, tab_historical = st.tabs(
        ["Location", "Latest Analysis", "Historical Analysis"])

    with tab_historical:
        # Uses data from the s3 bucket. Currently using data from database
        st.write("Plant")
        plant_ids = historical_data['plant_id'].unique().tolist()
        plant_option = st.selectbox("Choose a plant", plant_ids)

        st.header(f'🌡️ Temperature Readings for Plant {plant_option}🌡️')
        st.write(get_temperature_chart_single_plant(
            historical_data, plant_choice=plant_option))

        st.header(f'💧 Soil Moisture Readings for Plant{plant_option}💧')

        st.write(get_moisture_chart_single_plant(
            historical_data, plant_choice=plant_option))

    with tab_location:
        # Location Map
        st.header('🌍 Origin Locations 🌍')
        st.map(data=locations_df, latitude="location_lat",
               longitude="location_lon", size=1000, zoom=2)

    with tab_latest:
        # Pulls from the database
        st.header('Latest Moisture Readings 💧 ')
        st.write(get_latest_moisture_chart(readings_df))

        st.header('Latest Temperature Readings 🌡️')
        st.write(get_latest_temperature_chart(readings_df))


if __name__ == '__main__':
    load_dotenv()
    conn = create_connection()
    locations_df = get_locations_data(conn)
    readings_df = get_readings_data(conn)

    build_dashboard()
