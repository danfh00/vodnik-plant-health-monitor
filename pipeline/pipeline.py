from extract import extract_data
from transform import transform
from load import load

if __name__ == "__main__":

    extracted_data = extract_data()

    data = transform(extracted_data)

    load(data)
