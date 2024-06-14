"This script runs the entire short-term database pipeline"

from extract import extract_data
from transform import apply_transformations
from load import apply_load_process

if __name__ == "__main__":
    print("Retrieving data")
    initial_data = extract_data()
    print("Data retrieved")

    print("Cleaning data")
    cleaned_data = apply_transformations(initial_data)
    print("Data cleaned")

    print("Loading data")
    apply_load_process(cleaned_data)
    print("Data loaded")
