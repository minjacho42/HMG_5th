import pandas as pd
import requests
from dotenv import load_dotenv
import os
import argparse
from io import BytesIO

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

category_dict = {
    "yellow": "yellow_tripdata_{}-{}.parquet",
    "green": "green_tripdata_{}-{}.parquet",
    "fhv": "fhv_tripdata_{}-{}.parquet",
    "fhvhv": "fhvhv_tripdata_{}-{}.parquet"
}

def get_data(year, month, category):
    format_url = BASE_URL + category_dict[category]
    url = format_url.format(year, str(month).zfill(2))
    print(">>> Downloading data from: ", url)
    response = requests.get(url)
    if response.status_code == 200:
        print(">>> Loading data into memory")
        return pd.read_parquet(BytesIO(response.content))
    else:
        print(">>> Error downloading data")
        return None

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--year", type=int, required=True)
    arg_parser.add_argument("--month", type=int, required=True)
    arg_parser.add_argument("--category", type=str, required=True, choices=category_dict.keys())
    arg_parser.add_argument("--out-dir", type=str, required=True)
    args = arg_parser.parse_args()
    if not os.path.isdir(args.out_dir):
        os.makedirs(args.out_dir)
    file_name = f"{args.year}-{str(args.month).zfill(2)}-{args.category}.parquet"
    get_data(args.year, args.month, args.category).to_parquet(args.out_dir + "/" + file_name)
    print(">>> Data saved to: ", args.out_dir + "/" + file_name)