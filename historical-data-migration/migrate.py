"""A script to migrate 24 hour old day to long-term bucket storage"""
import os
import logging
import pymssql
import pandas as pd
from datetime import datetime, timedelta, date
from os import environ
from os import environ as ENV
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import NoCredentialsError

DATE_CONSTRAINT = datetime.now() - timedelta(hours=24)
WEEKDAY_INDEX = datetime.today().weekday()
CURRENT_DATE = date.today()
TEMPORARY_DATA_FOLDER = "data/"


def get_s3_client() -> client:
    """Returns input s3 client"""
    try:
        s3_client = client('s3',
                           aws_access_key_id=environ.get('ACCESS_KEY'),
                           aws_secret_access_key=environ.get('SECRET_ACCESS_KEY'))
        logging.info(f"""Connected to S3 bucket {
                     environ.get('STORAGE_BUCKET_NAME')}""")
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def get_connection() -> pymssql.Connection:
    """returns a pymssql connection to the plants database"""
    return pymssql.connect(server=ENV["DB_HOST"],
                           user=ENV["DB_USER"],
                           password=ENV["DB_PASSWORD"],
                           database=ENV["DB_NAME"])


def get_prefix(current_date: date) -> str:
    """creates object prefix for s3 bucket"""
    weekday = current_date.weekday()
    if weekday == 0:
        return f"wc-{current_date.strftime("%d-%m-%Y")}/"

    monday = current_date - timedelta(weekday)
    return f"wc-{monday.strftime("%d-%m-%Y")}/"


def upload_historical_readings(s3: client, bucket_name: str, prefix: str, filepath: str) -> None:
    """uploads the historical readings to the s3 bucket"""
    object_key = os.path.join(prefix, filepath.split('/')[1])
    s3.upload_file(filepath, bucket_name, object_key)
    logging.info(f"csv file uploaded: {object_key}")


def fetch_historical_readings(conn: pymssql.Connection, date_constraint: datetime) -> list[tuple]:
    """get 24 hour old readings from plant db"""
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT * FROM gamma.readings
                    WHERE reading_at <= %s""",
                    (date_constraint,))

        return cur.fetchall()


def create_reading_file(readings: list[tuple], current_date: datetime, folder_path: str) -> None:
    """creates .csv file of historical readings"""
    readings = pd.DataFrame(readings)
    readings.columns = ['reading_id', 'plant_id', 'reading_at',
                        'moisture', 'temp', 'botanist_id', 'watered_at']

    return readings.to_csv(f"{folder_path}{current_date}.csv", index=False)


def get_upload_file(folder_path: str) -> str:
    """gets file path to upload to output bucket"""
    all_files = os.listdir(folder_path)
    return [os.path.join(folder_path, file)
            for file in all_files if file.endswith('.csv')][0]


def create_data_folder(folder_path: str) -> None:
    """Creates temporary data_store"""
    folder_name = folder_path
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def remove_historical_readings(conn: pymssql.Connection, date_constraint: datetime) -> None:
    """removes 24 hour old readings from plant db"""
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM gamma.readings
                    WHERE reading_at <= %s""",
                    (date_constraint,))

    conn.commit()
    logging.info("historical readings removed from database")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    conn = get_connection()
    s3_client = get_s3_client()
    create_data_folder(TEMPORARY_DATA_FOLDER)

    readings = fetch_historical_readings(conn, DATE_CONSTRAINT)

    if readings:
        create_reading_file(readings, CURRENT_DATE, TEMPORARY_DATA_FOLDER)
        prefix = get_prefix(CURRENT_DATE)
        file_path = get_upload_file(TEMPORARY_DATA_FOLDER)
        upload_historical_readings(
            s3_client, environ.get('STORAGE_BUCKET_NAME'), prefix, file_path)
        os.remove(file_path)
        logging.info("temporary file deleted")
        remove_historical_readings(conn, DATE_CONSTRAINT)
    else:
        logging.info("No new historical data")
