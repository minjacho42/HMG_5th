import os
import json
from datetime import datetime
import pandas as pd
import sqlite3

LOG_FILE = 'etl_project_log.txt'

def display_info_with_pandas(df: pd.DataFrame):
    try:
        print("\033[31m--- Country have more than 100B GDP ---\033[0m")
        pd.options.display.float_format = "{:.2f}".format  # 소수점 둘째자리 까지 프린트
        pd.options.display.max_rows = 100  # 최대 row 개수 조정
        print(f'{"RANK":4} | {"COUNTRY":30} | {"GDP":8} | {"REGION":8}')
        for row in df[df['GDP'] >= 100].itertuples():
            print(f'{int(row.Index) + 1:4} | {row.country:30} | {row.GDP:8.2f} | {row.region}')
        print()
        print("\033[31m--- Each region's mean GDP of top 5 country ---\033[0m")
        for idx, region in enumerate(df['region'].unique()):
            if pd.notna(region):
                print(f"""\033[{32 + idx}m{region.upper():8}\033[0m : {df[df['region'] == region]
                      .sort_values(ascending=False, by='GDP')
                      .head(5)['GDP'].mean():.2f}""")
    except Exception as e:
        logger('Display-Info', 'ERROR: ' + str(e))
        raise e

def display_info_with_sqlite(sql_path: str, table_name: str = 'Countries_by_GDP'):
    try:
        conn = sqlite3.connect(sql_path)
        cursor = conn.cursor()
        query_100B = f"""SELECT * FROM {table_name} WHERE GDP_USD_billion >= 100"""
        cursor.execute(query_100B)
        result_100B = cursor.fetchall()
        print("\033[31m--- Country have more than 100B GDP ---\033[0m")
        print(f'{"RANK":4} | {"COUNTRY":30} | {"GDP":8} | {"REGION":8}')
        for idx, country, gdp, region in result_100B:
            print(f'{int(idx) + 1:4} | {country:30} | {gdp:8.2f} | {region}')
        print()
        query_region_top5_mean = f"""
                                    WITH regionRankTable(Region, GDP_USD_billion, Rank) AS (
                                    SELECT Region, GDP_USD_billion, ROW_NUMBER() OVER (
                                    PARTITION BY Region
                                    ORDER BY GDP_USD_billion DESC
                                    ) AS Rank
                                    FROM {table_name}
                                    )
                                    SELECT Region, AVG(GDP_USD_billion) AS Mean_GDP FROM regionRankTable
                                    WHERE Rank <= 5
                                    GROUP BY Region
                                    ORDER BY Mean_GDP DESC
                                    """
        print("\033[31m--- Each region's mean GDP of top 5 country ---\033[0m")
        cursor.execute(query_region_top5_mean)
        region_top5_mean = cursor.fetchall()
        for idx, pair in enumerate(region_top5_mean):
            region, mean = pair
            if pd.notna(region):
                print(f"""\033[{32 + idx}m{region.upper():8}\033[0m : {mean:.2f}""")
    except Exception as e:
        logger('Display-Info-SQL', 'ERROR: ' + str(e))
        raise e

# If data already exist and data wasn't changed, renew json file's meta data.
# If data already exist and data changed, rename old data and store new json data.from
# If data doesn't exist, save current data.
def save_raw_data_with_backup(file_name, data):
    if os.path.exists(file_name):  # If file exists
        old_data = {}
        with open(file_name, 'r') as f:
            old_data_with_meta = json.load(f)
            old_data = old_data_with_meta['data']
        if old_data == data:  # compare old data and new data
            logger('Extract-Save', 'No update in raw data')
        else: # if old data and new data are different, rename old data.
            os.rename(file_name, file_name.split('.')[0] + datetime.now().strftime('%Y%m%d%H%M%S') + '.json')
            logger('Extract-Save', 'Update raw data')
    with open(file_name, 'w') as f:
        data_with_meta = {'data': data, 'meta_data': {'date': datetime.now().strftime('%Y-%B-%d %H:%M:%S')}}
        json.dump(data_with_meta, f)

def read_json_file(file_name):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
            print(f'Data Successfully Loaded meta_data:{data['meta_data']}')
        return data['data']
    except FileNotFoundError:
        print(f'File not found: {file_name}')
        return None

# log etl step with msg
def logger(step: str, msg: str):
    with open(LOG_FILE, 'a') as file:
        now = datetime.now()
        timestamp = now.strftime("%Y-%B-%d %H:%M:%S") #formatting the timestamp
        file.write(f'{timestamp}, [{step.upper()}] {msg}\n')