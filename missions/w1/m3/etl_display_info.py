import pandas as pd
import sqlite3

def display_info_with_pandas(df: pd.DataFrame):
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

def display_info_with_sqlite(sql_path: str):
    conn = sqlite3.connect(sql_path)
    cursor = conn.cursor()
    query_100B = """SELECT * FROM Countries_by_GDP WHERE GDP_USD_billion >= 100"""
    cursor.execute(query_100B)
    result_100B = cursor.fetchall()
    print("\033[31m--- Country have more than 100B GDP ---\033[0m")
    print(f'{"RANK":4} | {"COUNTRY":30} | {"GDP":8} | {"REGION":8}')
    for idx, country, gdp, region in result_100B:
        print(f'{int(idx) + 1:4} | {country:30} | {gdp:8.2f} | {region}')
    print()
    query_region_list = """SELECT DISTINCT Region FROM Countries_by_GDP WHERE Region IS NOT NULL"""
    cursor.execute(query_region_list)
    result_region_list = cursor.fetchall()
    query_region_top5_mean = """SELECT Region, AVG(GDP_USD_billion) AS Mean_GDP_USD_billion
                                FROM (
                                SELECT Region, GDP_USD_billion FROM Countries_by_GDP
                                WHERE Region == ?
                                ORDER BY GDP_USD_billion DESC
                                LIMIT 5
                                )
                                """
    print("\033[31m--- Each region's mean GDP of top 5 country ---\033[0m")
    for idx, region in enumerate(result_region_list):
        cursor.execute(query_region_top5_mean, region)
        region, mean = cursor.fetchall()[0]
        print(f"""\033[{32 + idx}m{region.upper():8}\033[0m : {mean:.2f}""")

if __name__ == '__main__':
    display_info_with_sqlite('/Users/admin/HMG_5th/missions/w1/data/World_Economies.db')