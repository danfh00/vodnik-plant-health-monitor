"This file is responsible for loading data into the database"
# pylint: disable=C0301, E1101

import os
import pymssql
from dotenv import load_dotenv
import boto3

load_dotenv()

ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
DB_HOST = os.getenv('DB_HOST')
DB_USERNAME = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SCHEMA = os.getenv('DB_SCHEMA')
INDEX_OF_LAT = 0
INDEX_OF_LON = 1
INDEX_OF_NAME = 2
INDEX_OF_CC = 3
INDEX_OF_TIMEZONE = 4
ORIGIN_LOCATION = "origin_location"
NAME = "name"
SCIENTIFIC_NAME = "scientific_name"
PHONE = "phone"
ERROR = "error"
PLANT_ID = "plant_id"
EMAIL = "email"
BOTANIST = "botanist"
LAST_WATERED = "last_watered"
TEMPERATURE = "temperature"
SOIL_MOISTURE = "soil_moisture"
RECORDING_TAKEN = "reading_at"
MIN_SOIL_MOISTURE = 21
MAX_SOIL_MOISTURE = 41
MIN_TEMP = 7
MAX_TEMP = 38
TOPIC_ARN = "arn:aws:sns:eu-west-2:129033205317:vodnik-you-got-mail"


def create_connection(host: str, username: str, password: str, database_name: str) -> pymssql.Connection:
    """Creates a pymssql connection to the appropriate database"""
    return pymssql.connect(server=host,
                           user=username,
                           password=password,
                           database=database_name)


def check_if_botanist_in_db(email: str, schema: str, cursor: pymssql.Cursor) -> tuple:
    """Checks if there is a botanist that has the provided email"""
    cursor.execute(
        f"""SELECT botanists_id FROM {schema}.botanists WHERE email=%s""", (email,))

    result = cursor.fetchone()

    return result


def add_botanist_to_db(botanist_data: dict, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the botanist to the 'botanists' table"""
    first_name, last_name = tuple(botanist_data[NAME].split())
    phone_number = botanist_data[PHONE]
    email = botanist_data[EMAIL]

    try:
        cursor.execute(f"""INSERT INTO {
            schema}.botanists (first_name, last_name, email, phone_number) VALUES (%s, %s, %s, %s)""",
            (first_name, last_name, email, phone_number,))

        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_timezone_in_db(timezone: str, schema: str, cursor: pymssql.Cursor) -> tuple:
    """Checks if the passed timezone value is in the 'timezones' table"""
    cursor.execute(
        f"""SELECT timezone_id FROM {schema}.timezones WHERE timezone=%s""", (timezone,))

    result = cursor.fetchone()

    return result


def add_timezone_to_db(timezone_name: dict, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new timezone to the 'timezones' table"""
    try:
        cursor.execute(
            f"""INSERT INTO {schema}.timezones (timezone) VALUES (%s)""", (timezone_name,))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_country_code_in_db(cc: str, schema: str, cursor: pymssql.Cursor) -> tuple:
    """Checks if the passed country code is in the 'country_codes' table"""
    cursor.execute(
        f"""SELECT country_code_id FROM {schema}.country_codes WHERE country_code=%s""", (cc,))

    result = cursor.fetchone()

    return result


def add_country_code_to_db(cc: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new country code to the 'country_codes' table"""
    try:
        cursor.execute(
            f"""INSERT INTO {schema}.country_codes (country_code) VALUES (%s)""", (cc,))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_location_in_db(city: str, lat: float, lon: float, schema: str, cursor: pymssql.Cursor) -> tuple:
    """Checks if the passed data is present in the 'locations' table"""
    cursor.execute(
        f"""SELECT location_id FROM {schema}.locations
            WHERE location_name=%s AND location_lat=%s AND location_lon=%s""", (city, lat, lon,))

    result = cursor.fetchone()

    return result


def add_location_to_db(location_data: tuple, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the new location to the 'locations' table"""
    city = location_data[INDEX_OF_NAME]
    lat = location_data[INDEX_OF_LAT]
    lon = location_data[INDEX_OF_LON]
    cc_id = check_if_country_code_in_db(
        location_data[INDEX_OF_CC], schema, cursor)[0]
    timezone_id = check_if_timezone_in_db(
        location_data[INDEX_OF_TIMEZONE], schema, cursor)[0]

    try:
        cursor.execute(
            f"""INSERT INTO {schema}.locations
                (location_name, location_lat, location_lon,
                 timezone_id, country_code_id)
                VALUES (%s, %s, %s, %s, %s)""", (city, lat, lon, timezone_id, cc_id,))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_species_in_db(common_name: str, scientific_name: str, schema: str, cursor: pymssql.Cursor) -> tuple:
    """Checks if there exists a species with the given name in the 'plant_species' table"""
    if scientific_name is None:
        cursor.execute(
            f"""SELECT species_id FROM {schema}.plant_species WHERE common_name=%s AND scientific_name IS NULL""", (common_name,))
    else:
        cursor.execute(
            f"""SELECT species_id FROM {schema}.plant_species WHERE common_name=%s AND scientific_name=%s""", (common_name, scientific_name,))

    result = cursor.fetchone()

    return result


def add_species_to_db(common_name: str, scientific_name: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the provided species to the 'plant_species' table"""
    try:
        cursor.execute(
            f"""INSERT INTO {
                schema}.plant_species (common_name, scientific_name) VALUES (%s, %s)""",
            (common_name, scientific_name))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def check_if_plant_in_db(plant_id: int, schema: str, cursor: pymssql.Cursor) -> tuple:
    """Checks if there is a plant with the passed plant_id"""
    cursor.execute(f"""SELECT plant_id FROM {
                   schema}.plants WHERE plant_id = %s""", (plant_id,))

    result = cursor.fetchone()

    return result


def add_plant_to_db(plant_id: int, common_name: str, scientific_name: str, location_data: list, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the plant to the 'plants' table"""
    plant_species_id = check_if_species_in_db(
        common_name, scientific_name, schema, cursor)[0]
    location_id = check_if_location_in_db(
        location_data[INDEX_OF_NAME], location_data[INDEX_OF_LAT], location_data[INDEX_OF_LON], schema, cursor)[0]

    try:
        cursor.execute(
            f"""INSERT INTO {schema}.plants (plant_id, species_id, location_id) VALUES (%s, %s, %s)""", (plant_id, plant_species_id, location_id))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def botanist_checks(botanist_data: dict, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> tuple:
    """The logic for checking if a given botanist exists, and if it doesn't then adding it"""
    botanist_email = botanist_data[EMAIL]
    botanist_id = check_if_botanist_in_db(botanist_email, schema, cursor)

    if botanist_id:
        return botanist_id[0]

    add_botanist_to_db(botanist_data, schema, conn, cursor)
    return check_if_botanist_in_db(botanist_email, schema, cursor)[0]


def timezone_checks(timezone_name: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """The logic for checking if a given timezone exists in the database, and if it doesn't then adding it"""
    if not check_if_timezone_in_db(timezone_name, schema, cursor):
        add_timezone_to_db(timezone_name, schema, conn, cursor)


def country_code_checks(cc: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """The logic for checking if a given country code exists in the database, and if it doesn't then adding it"""
    if not check_if_country_code_in_db(cc, schema, cursor):
        add_country_code_to_db(cc, schema, conn, cursor)


def location_checks(location_data: list, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """The logic for checking if a given location exists in the database, and if it doesn't then adding it"""
    if not check_if_location_in_db(
            location_data[INDEX_OF_NAME], location_data[INDEX_OF_LAT], location_data[INDEX_OF_LON], schema, cursor):
        add_location_to_db(location_data, schema, conn, cursor)


def plant_species_checks(common_name: str, scientific_name: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """The logic for checking if a given species exists in the database, and if it doesn't then adding it"""
    if not check_if_species_in_db(common_name, scientific_name, schema, cursor):
        add_species_to_db(common_name, scientific_name, schema, conn, cursor)


def plant_checks(plant_id: int, common_name: str, scientific_name: str, location_data: list, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """The logic for checking if a given plant and location combination exists in the database, and if it doesn't then adding it"""
    if not check_if_plant_in_db(plant_id, schema, cursor):
        add_plant_to_db(plant_id, common_name,
                        scientific_name, location_data, schema, conn, cursor)


def add_reading_to_db(plant_id: int, reading_at: str, moisture: float, temp: float, botanist_id: int, watered_at: str, schema: str, conn: pymssql.Connection, cursor: pymssql.Cursor) -> None:
    """Adds the plant reading to the readings table"""
    try:
        cursor.execute(
            f"""INSERT INTO {schema}.readings (plant_id, reading_at, moisture, temp, botanist_id, watered_at)
                VALUES (%s, %s, %s, %s, %s, %s)""", (plant_id, reading_at, moisture, temp, botanist_id, watered_at))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()


def send_notification(boto_client: 'boto3.client.SNS', subject: str, body: str) -> None:
    """Sends a notification using AWS SNS"""
    boto_client.publish(
        TopicArn=TOPIC_ARN,
        Message=body,
        Subject=subject
    )


def check_for_abnormal_levels(email_client: 'boto3.client.SNS', cursor: pymssql.Cursor, plant_data: dict) -> None:
    """Checks if the plant temperature and soil moisture is abnormal, and sends an email if necessary"""
    cursor.execute(f"""SELECT TOP 1 temp, moisture FROM readings WHERE plant_id = {
                   plant_data[PLANT_ID]} ORDER BY reading_at DESC;""")

    most_recent_reading = cursor.fetchone()
    current_soil_moisture = plant_data[SOIL_MOISTURE]
    current_temp = plant_data[TEMPERATURE]
    if most_recent_reading:
        previous_soil_moisture = float(most_recent_reading[1])
        previous_temp = float(most_recent_reading[0])

        if not MIN_SOIL_MOISTURE < current_soil_moisture < MAX_SOIL_MOISTURE and not MIN_SOIL_MOISTURE < previous_soil_moisture < MAX_SOIL_MOISTURE:
            send_notification(email_client, "Issue with moisture",
                              "Good day to you, there seems to be an issue with moisture levels, please check it")

        if not MIN_TEMP < current_temp < MAX_TEMP and not MIN_TEMP < previous_temp < MAX_TEMP:
            send_notification(email_client, "Issue with temperature",
                              "Good day to you, there seems to be an issue with temperature levels, please check it")


def apply_load_process(all_plant_data: dict) -> None:
    """Adds all information into their relevant table in the database"""
    con = create_connection(DB_HOST, DB_USERNAME,
                            DB_PASSWORD, DB_NAME)
    cur = con.cursor()

    sns_client = boto3.client(
        'sns', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)

    for plant in all_plant_data:
        if ERROR not in plant:
            current_botanist_id = botanist_checks(
                plant[BOTANIST], DB_SCHEMA, con, cur)
            timezone_checks(plant[ORIGIN_LOCATION]
                            [INDEX_OF_TIMEZONE], DB_SCHEMA, con, cur)
            country_code_checks(
                plant[ORIGIN_LOCATION][INDEX_OF_CC], DB_SCHEMA, con, cur)
            location_checks(plant[ORIGIN_LOCATION], DB_SCHEMA, con, cur)
            plant_species_checks(
                plant[NAME], plant[SCIENTIFIC_NAME], DB_SCHEMA, con, cur)
            plant_checks(plant[PLANT_ID], plant[NAME],
                         plant[SCIENTIFIC_NAME], plant[ORIGIN_LOCATION], DB_SCHEMA, con, cur)

            check_for_abnormal_levels(sns_client, cur, plant)

            add_reading_to_db(plant[PLANT_ID], plant[RECORDING_TAKEN], plant[SOIL_MOISTURE],
                              plant[TEMPERATURE], current_botanist_id, plant[LAST_WATERED], DB_SCHEMA, con, cur)

    cur.close()
    con.close()
