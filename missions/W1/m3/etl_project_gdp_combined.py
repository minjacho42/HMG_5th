import etl_project_gdp
import etl_project_gdp_api
import etl_project_gdp_with_sql
import etl_project_util
import argparse
import pandas as pd

SQL_PATH = '../data/World_Economies.db'

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    # argument --api will determine to use api in extract
    arg_parser.add_argument('--api', action='store_true', help='use api in extract')
    # argument --raw-json will set the raw file as the result of extract
    arg_parser.add_argument('--raw-json', type=str, help='raw file as the result of extract', default=None)
    # argument --table-name will set the table name to load or display
    arg_parser.add_argument('--table-name', type=str, help='table name to load or display', default='Countries_by_GDP')
    args = arg_parser.parse_args()
    extract = etl_project_gdp.extract
    transform = etl_project_gdp.transform
    load = etl_project_gdp_with_sql.load
    if args.api:
        extract = etl_project_gdp_api.extract
        transform = etl_project_gdp_api.transform
    df = pd.DataFrame()
    if args.raw_json:
        data = etl_project_util.read_json_file(args.raw_json)
        df = transform(data)
    else:
        data = extract()
        df = transform(data)
    load(df, args.table_name)
    etl_project_util.display_info_with_sqlite(SQL_PATH ,table_name=args.table_name)
