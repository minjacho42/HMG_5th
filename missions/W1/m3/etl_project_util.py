import json
import pandas as pd
import sqlite3
from extractor import ExtractorWithAPI
from etl_project_logger import logger


# Display two result with pandas
# 1. Display Rank, Country, GDP, and Region for countries with GDP greater than 100B in descending order
# 2. Display the mean GDP of the top 5 countries in each region
def display_info_with_pandas(df: pd.DataFrame):
    try:
        # 1
        print("\033[31m--- Country have more than 100B GDP ---\033[0m")
        pd.options.display.float_format = "{:.2f}".format  # 소수점 둘째자리 까지 프린트
        pd.options.display.max_rows = 100  # 최대 row 개수 조정
        print(f'{"RANK":4} | {"COUNTRY":30} | {"GDP":8} | {"REGION":8}')
        for row in df[df['GDP'] >= 100].itertuples():
            print(f'{int(row.Index) + 1:4} | {row.country:30} | {row.GDP:8.2f} | {row.region}')
        print()

        # 2
        print("\033[31m--- Each region's mean GDP of top 5 country ---\033[0m")
        for idx, region in enumerate(df['region'].unique()):
            if pd.notna(region):
                print(f"""\033[{32 + idx}m{region.upper():8}\033[0m : {df[df['region'] == region]
                      .sort_values(ascending=False, by='GDP')
                      .head(5)['GDP'].mean():.2f}""")
    except Exception as e:
        logger('Display-Info', 'ERROR: ' + str(e))
        raise e

# Display two result with SQL query
# 1. Display Rank, Country, GDP, and Region for countries with GDP greater than 100B in descending order
# 2. Display the mean GDP of the top 5 countries in each region
def display_info_with_sqlite(sql_path: str, table_name: str = 'Countries_by_GDP'):
    try:
        conn = sqlite3.connect(sql_path)
        cursor = conn.cursor()

        # Query for #1
        query_100B = f"""SELECT * FROM {table_name} WHERE GDP_USD_billion >= 100"""
        cursor.execute(query_100B)
        result_100B = cursor.fetchall()
        print("\033[31m--- Country have more than 100B GDP ---\033[0m")
        print(f'{"RANK":4} | {"COUNTRY":30} | {"GDP":8} | {"REGION":8}')
        for idx, country, gdp, region in result_100B:
            print(f'{int(idx) + 1:4} | {country:30} | {gdp:8.2f} | {region}')
        print()

        # Query for #2
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

# Read Json file.
# If 'broken' field in 'meta_data' of json file is True, raise File broken exception
# Else, return 'data' field of json file
def read_json_file(file_name):
    """
    Reads a JSON file specified by the file_name parameter and returns the "data" portion
    of the JSON object. The function also validates whether the metadata in the file indicates
    a broken endpoint or not. If the file contains a 'meta_data' section with the 'broken' flag
    set to True, the function raises a custom error indicating the file needs re-extraction.

    Errors encountered during file operations such as file not existing are handled
    internally, logging relevant information without terminating execution.

    :param file_name: Path to the JSON file to be read
    :type file_name: str
    :return: The 'data' dictionary from the JSON file if read successfully; otherwise, None.
    :rtype: dict | None
    :raises BrokenEndpointExistError: If the file contains a 'meta_data' section with the 'broken' flag set to True.
    """
    try:
        data = None
        with open(file_name, 'r') as f:
            data = json.load(f)
            print(f'Data Successfully Loaded meta_data:{data['meta_data']}')
        if data['meta_data']['broken']:
            raise ExtractorWithAPI.BrokenEndpointExistError(f'File is broken have to re-extract {data["meta_data"]}')
        return data['data']
    except FileNotFoundError:
        print(f'File not found: {file_name}')
        return None
