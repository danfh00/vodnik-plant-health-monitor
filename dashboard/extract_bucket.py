"""Extracts from s3 bucket"""
import os
from boto3 import client
import pandas as pd
from dotenv import load_dotenv


def get_aws_client() -> client:
    "Returns an s3 client"
    return client('s3',
                  aws_access_key_id=os.getenv("ACCESS_KEY"),
                  aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY")
                  )


def get_bucket(s3: client, bucket_name: str):
    """ Returns the bucket contents """
    return s3.list_objects(Bucket=bucket_name)['Contents']


def get_latest_file(files: list) -> str:
    """ Filters for last modified sjogren files """
    max_modified = max([file['LastModified'] for file in files])
    latest = [file for file in files if file['LastModified'] == max_modified]
    return latest[0]


def download_files(s3: client, file: str, bucket_name: str) -> None:
    """ Downloads files from bucket """
    s3.download_file(
        bucket_name, file['Key'], "historical_data.csv")


def download_historical_data() -> pd.DataFrame:
    """Downloads the latest data from the s3 bucket and converts it into a df"""
    client = get_aws_client()
    bucket_name = "vodnik-historical-plant-readings"
    objects = get_bucket(client, bucket_name)
    latest_files = get_latest_file(objects)
    download_files(client, latest_files, bucket_name)

    # Read csv into a dataframe
    df = pd.read_csv("historical_data.csv")
    return df


if __name__ == '__main__':
    download_historical_data(client)
