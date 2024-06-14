"This script runs the entire short-term database pipeline"

from extract import extract_data
from transform import apply_transformations
from load import apply_load_process
import logging


def handler(event=None, context=None):
    logging.info("Retrieving data")
    initial_data = extract_data()
    logging.info("Data retrieved")

    logging.info("Cleaning data")
    cleaned_data = apply_transformations(initial_data)
    logging.info("Data cleaned")

    logging.info("Loading data")
    apply_load_process(cleaned_data)
    logging.info("Data loaded")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler()
