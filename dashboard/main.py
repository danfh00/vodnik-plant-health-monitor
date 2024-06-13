import os
import altair as alt
import pymssql
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from boto3 import client


def create_connection() -> pymssql.Connection:
    """Creates a pymssql connection to the appropriate database"""
    return pymssql.connect(server=os.getenv('DB_HOST'),
                           user=os.getenv('DB_USER'),
                           password=os.getenv('DB_PASSWORD'),
                           database=os.getenv('DB_NAME'))


def get_aws_client() -> client:
    "Returns an s3 client"
    return client('s3',
                  aws_access_key_id=os.get("ACCESS_KEY"),
                  aws_secret_access_key=os.get("SECRET_ACCESS_KEY")
                  )


def get_bucket(s3: client, bucket_name: str):
    """ Returns the bucket contents """
    return s3.list_objects(Bucket=bucket_name)


def get_latest_file(files: list) -> str:
    """ Filters for last modified sjogren files """
    max_modified = max([file['LastModified'] for file in files])
    latest = [file for file in files if file['LastModified'] == max_modified]
    return latest[0]


def get_historical_data():
    client = get_aws_client()
    csv_files = get_bucket(client, "vodnik-historical-plant-readings")
    latest_file = get_latest_file(csv_files)
    client.download_file(
        "vodnik-historical-plant-readings", latest_file['Key'], "historical_data.csv")
    # Read csv into a dataframe
    df = pd.read_csv("historical_data")
    return df


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

    moisture_data = data[data["common_name"] == plant_choice]
    chart = alt.Chart(moisture_data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('moisture:Q', scale=alt.Scale(
            domain=[y_min, y_max]), axis=alt.Axis(title='Moisture'))
    ).properties(
        width=700,
        height=600,
    ).interactive()

    return chart


def get_temperature_chart_single_plant(data: pd.DataFrame, plant_choice) -> alt.Chart:
    y_min = data['temp'].min()
    y_max = data['temp'].max()

    temp_data = data[data["common_name"] == plant_choice]
    chart = alt.Chart(temp_data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('temp:Q', scale=alt.Scale(
            domain=[y_min, y_max]), axis=alt.Axis(title='Temperature'))
    ).properties(
        width=700,
        height=600,
    ).interactive()

    return chart


def get_latest_moisture_chart(latest_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(latest_data).mark_bar().encode(
        y=alt.Y('common_name:N', title='Plant name'),
        x=alt.X('moisture:Q', title='Soil Moisture')
    ).properties(
        width=700,
        height=600,
    ).interactive()


def get_latest_temperature_chart(latest_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(latest_data).mark_bar().encode(
        y=alt.Y('common_name:N', sort='-x', title='Plant name'),
        x=alt.X('temp:Q', title='Temperature')
    ).properties(
        width=700,
        height=600,
    ).interactive()


def build_dashboard():
    "Builds and structures the dashboard"
    conn = create_connection()
    locations_df = get_locations_data(conn)
    readings_df = get_readings_data(conn)

    st.title("LNMH Plant Health Dashboard🍀")

    tab_location, tab_latest, tab_historical = st.tabs(
        ["Location", "Latest Analysis", "Historical Analysis"])

    with tab_historical:
        # Uses data from the s3 bucket. Currently using data from database
        plant_names = readings_df['common_name'].unique().tolist()
        plant_option = st.selectbox("Choose a plant", plant_names)

        st.header('🌡️ Temperature Readings 🌡️')
        st.write(get_temperature_chart_single_plant(
            readings_df, plant_choice=plant_option))

        st.header('💧 Soil Moisture Readings 💧')

        st.write(get_moisture_chart_single_plant(
            readings_df, plant_choice=plant_option))

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
    build_dashboard()
