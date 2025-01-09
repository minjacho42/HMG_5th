import pandas as pd
import sqlite3
from etl_project_gdp import extract, transform
from etl_project_util import display_info_with_sqlite, logger

SQL_PATH = '/Users/admin/HMG_5th/missions/w1/data/World_Economies.db'

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

if __name__ == '__main__':
    try:
        data = extract()
        df = transform(data)
        load(df)
        display_info_with_sqlite(SQL_PATH)
    except Exception as e:
        print(e)
        exit(1)