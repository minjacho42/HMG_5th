import pandas as pd
import sqlite3
import asyncio
from etl_project_gdp_api import transform
from etl_project_logger import logger
from etl_project_util import display_info_with_sqlite, read_json_file
from extractor import ExtractorWithAPI

SQL_PATH = '../data/World_Economies.db'
JSON_FILE = 'Countries_by_GDP_API.json'
API_BASE_URL = 'https://www.imf.org/external/datamapper/api/v1/'
ENDPOINTS = ['NGDPD', 'countries']

# Load the transformed data into an SQLite database using sqlite3
def load(df: pd.DataFrame, table_name: str = 'Countries_by_GDP'):
    try:
        logger('Load-SQL', 'start')
        conn = sqlite3.connect(SQL_PATH)
        df.rename(columns={'GDP': 'GDP_USD_billion', 'country': 'Country', 'region': 'Region'}, inplace=True)
        df.to_sql(table_name, con=conn, if_exists='replace')
        logger('Load-SQL', 'done')
    except Exception as e:
        logger('Load-SQL', 'ERROR: ' + str(e))
        raise e

async def main():
    extract_with_api = ExtractorWithAPI(file_path=JSON_FILE,
                           base_url=API_BASE_URL,
                           end_points=ENDPOINTS
                           )
    await extract_with_api.run()
    df = transform(read_json_file(file_name=JSON_FILE))
    load(df)
    display_info_with_sqlite(SQL_PATH)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
        exit(1)