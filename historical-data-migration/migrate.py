"""A script to migrate 24 hour old day to long-term bucket storage"""
import io
import os
import logging
from datetime import datetime, timedelta, date
from os import environ as ENV
import pymssql
import pandas as pd
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
                           aws_access_key_id=ENV.get('ACCESS_KEY'),
                           aws_secret_access_key=ENV.get('SECRET_ACCESS_KEY'))
        logging.info(f"""Connected to S3 bucket {
                     ENV.get('STORAGE_BUCKET_NAME')}""")
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def get_connection():
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


def upload_historical_readings(s3: client, bucket_name: str, prefix: str,
                               filename: str, file_data: io.BytesIO) -> None:
    """uploads the historical readings in memory to the s3 bucket"""
    object_key = os.path.join(prefix, filename)
    s3.upload_fileobj(file_data, bucket_name, object_key)
    logging.info(f"csv file uploaded: {object_key}")


def fetch_historical_readings(conn, date_constraint: datetime) -> list[tuple]:
    """get 24 hour old readings from plant db"""
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT * FROM gamma.readings
                    WHERE reading_at <= %s""",
                    (date_constraint,))

        return cur.fetchall()


def create_reading_file(readings: list[tuple]) -> io.BytesIO:
    """creates in-memory byte stream of csv data"""
    readings = pd.DataFrame(readings)
    readings.columns = ['reading_id', 'plant_id', 'reading_at',
                        'moisture', 'temp', 'botanist_id', 'watered_at']

    buffer = io.BytesIO()
    readings.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


def remove_historical_readings(conn, date_constraint: datetime) -> None:
    """removes 24 hour old readings from plant db"""
    with conn.cursor() as cur:
        cur.execute("""
                    DELETE FROM gamma.readings
                    WHERE reading_at <= %s""",
                    (date_constraint,))

        conn.commit()
    logging.info("historical readings removed from database")


def handler(event=None, context=None):
    """lambda handler function"""
    load_dotenv()
    conn = get_connection()
    s3_client = get_s3_client()
    readings = fetch_historical_readings(conn, DATE_CONSTRAINT)

    if readings:
        csv_data = create_reading_file(readings)
        prefix = get_prefix(CURRENT_DATE)
        file_name = f"{CURRENT_DATE}.csv"
        upload_historical_readings(
            s3_client, ENV.get('STORAGE_BUCKET_NAME'), prefix, file_name, csv_data)
        remove_historical_readings(conn, DATE_CONSTRAINT)
    else:
        logging.info("No new historical data")

    conn.close()
    return {"success": "data migration complete"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler()
