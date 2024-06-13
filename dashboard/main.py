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


def get_moisture_chart(data: pd.DataFrame, plant_choice: str) -> alt.Chart:
    y_min = data['moisture'].min()
    y_max = data['moisture'].max()
    data['reading_at'] = pd.to_datetime(data['reading_at'])

    moisture_data = data[data["common_name"] == plant_choice]
    chart = alt.Chart(moisture_data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time (Hour)')),
        y=alt.Y('moisture:Q', scale=alt.Scale(
            domain=[y_min, y_max]), axis=alt.Axis(title='Moisture'))
    ).interactive()

    return chart


def get_temperature_chart(data: pd.DataFrame, plant_choice) -> alt.Chart:
    y_min = data['temp'].min()
    y_max = data['temp'].max()

    temp_data = data[data["common_name"] == plant_choice]
    chart = alt.Chart(temp_data).mark_line().encode(
        x=alt.X('reading_at:T', axis=alt.Axis(title='Time')),
        y=alt.Y('temp:Q', scale=alt.Scale(
            domain=[y_min, y_max]), axis=alt.Axis(title='Temperature'))
    ).interactive()

    return chart


def get_plant_names(df: pd.DataFrame) -> list[str]:
    return df['common_name'].unique().tolist()


def build_dashboard():
    "Builds and structures the dashboard"
    conn = create_connection()
    locations_df = get_locations_data(conn)
    readings_df = get_readings_data(conn)

    st.title("LNMH Plant Health Dashboard")

    # Sidebar:
    st.sidebar.title('Select a Plant')

    plant_names = get_plant_names(readings_df)
    plant_option = st.sidebar.selectbox("Choose a plant", plant_names)
    selected_plant = plant_option

    st.header('🌡️ Temperature Readings 🌡️')
    st.write(get_temperature_chart(readings_df, plant_choice=plant_option))

    st.header('💧 Soil Moisture Readings 💧')

    st.write(get_moisture_chart(readings_df, plant_choice=plant_option))

    # Location Map
    st.header('🌍 Origin Locations 🌍')
    st.map(data=locations_df, latitude="location_lat",
           longitude="location_lon", size=1000, zoom=2)


if __name__ == '__main__':
    load_dotenv()
    build_dashboard()
