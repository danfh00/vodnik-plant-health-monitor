"This script runs the entire short-term database pipeline"

from extract import extract_data
from transform import apply_transformations
from load import apply_load_process

if __name__ == "__main__":
    initial_data = extract_data()
    cleaned_data = apply_transformations(initial_data)
    apply_load_process(cleaned_data)
