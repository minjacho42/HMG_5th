import sqlite3
import pandas as pd
from etl_logger import logger
from etl_project_gdp import extract, transform
from missions.w1.m3.etl_display_info import display_info_with_sqlite

SQL_PATH = '/Users/admin/HMG_5th/missions/w1/data/World_Economies.db'

def load(df):
    logger('Load-SQL', 'start')
    conn = sqlite3.connect(SQL_PATH)
    df.rename(columns={'GDP': 'GDP_USD_billion', 'country': 'Country', 'region': 'Region'}, inplace=True)
    df.to_sql('Countries_by_GDP', con=conn, if_exists='replace')
    logger('Load-SQL', 'done')

if __name__ == '__main__':
    try:
        extract()
    except Exception as e:
        logger('Extract', 'ERROR: ' + str(e))
        print(e)
        exit(1)
    df = pd.DataFrame()
    try:
        df = transform()
    except Exception as e:
        logger('Transform', 'ERROR: ' + str(e))
        print(e)
        exit(1)
    try:
        load(df)
        display_info_with_sqlite(SQL_PATH)
    except Exception as e:
        logger('Load-SQL', 'ERROR: ' + str(e))