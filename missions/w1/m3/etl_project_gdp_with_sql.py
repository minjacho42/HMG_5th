import sqlite3
from etl_logger import logger
from etl_project_gdp import extract, transform
from etl_display_info import display_info_with_sqlite

SQL_PATH = '/Users/admin/HMG_5th/missions/w1/data/World_Economies.db'

def load(df):
    try:
        logger('Load-SQL', 'start')
        conn = sqlite3.connect(SQL_PATH)
        df.rename(columns={'GDP': 'GDP_USD_billion', 'country': 'Country', 'region': 'Region'}, inplace=True)
        df.to_sql('Countries_by_GDP', con=conn, if_exists='replace')
        logger('Load-SQL', 'done')
    except Exception as e:
        logger('Load-SQL', 'ERROR: ' + str(e))
        raise e

if __name__ == '__main__':
    try:
        extract()
        df = transform()
        load(df)
        display_info_with_sqlite(SQL_PATH)
    except Exception as e:
        print(e)
        exit(1)