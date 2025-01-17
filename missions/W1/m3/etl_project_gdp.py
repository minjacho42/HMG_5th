from bs4 import BeautifulSoup
import pandas as pd
import asyncio
from extractor import ExtractorWithWeb
from etl_project_util import display_info_with_pandas, read_json_file
from etl_project_logger import logger

JSON_FILE = 'Countries_by_GDP.json'
REGION_CSV_PATH = '../data/region.csv'
CRAWLING_URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'

on_memory_loaded_df = None

# Transform HTML <tr> tags to a dictionary where each row is determined by the cells
# Cell 0 represents the Country name, and Cell 1 represents the GDP value
def transform_html_tr_tags(trs: list):
	tr_dict = {}
	for tr in trs:
		cells = tr.find_all('td')  # Get all cells in the row
		if len(cells) > 1:  # Cell[0] is country name, cell[1] is GDP from IMF
			if cells[0].text.strip() == 'World': continue
			tr_dict[cells[0].text.strip()] = cells[1].text.replace(',', '').strip()
	return tr_dict

# Preprocess raw data to a dictionary using Beautiful Soup.
# Select the `table.wikitable` tag and convert tables into a dictionary
def preprocess_using_bs4(data):
	soup = BeautifulSoup(data, 'html.parser')
	table_soup = soup.select('table.wikitable')  # Find a table with class 'wikitable'
	if len(table_soup) < 1:
		logger('Transform', 'ERROR: No table found')
		raise Exception('No table found')
	if len(table_soup) > 1:
		logger('Transform', 'WARNNING: Multiple tables found')
	rows = table_soup[0].find_all('tr')  # Get all rows in the table
	gdp_dict = transform_html_tr_tags(rows)  # transform tr tags to dict
	return gdp_dict


def trans_df_column_numeric(df: pd.DataFrame, column: str):
	df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
	return df

def merge_region_info_df(df: pd.DataFrame, region_df: pd.DataFrame):
	return pd.merge(df, region_df, how='left', on='country')  # Join dataframes on country column

# Transform data extracted by web scrapping using beautifulsoup
# DataFrame columns = GDP, country, region
def transform(data: str):
	"""
	Transforms the given GDP data string into a structured and processed DataFrame. The function takes GDP data
	in string format, preprocesses it into a dictionary, converts it into a DataFrame, modifies its structure
	and data types, and merges it with regional information from a CSV file. The output is a DataFrame where
	GDP is expressed in billions and is associated with its respective regions.

	:param data: Raw GDP data in string format.
	:type data: str
	:return: A DataFrame with the processed GDP per country and associated regional information.
	:rtype: pandas.DataFrame
	:raises Exception: If any error occurs during the transformation process.
	"""
	try:
		logger('Transform', 'start')
		gdp_dict = preprocess_using_bs4(data)
		gdp_df = pd.DataFrame(list(gdp_dict.items()), columns=['country', 'GDP'])
		gdp_df = trans_df_column_numeric(gdp_df, 'GDP') # Change datatype as int64
		gdp_df['GDP'] = gdp_df['GDP'] / 1000 # Convert to the unit of billions.
		region_df = pd.read_csv(REGION_CSV_PATH, usecols=['name', 'region'])
		region_df.rename(columns={'name': 'country'}, inplace=True)
		merged_gdp_df = merge_region_info_df(gdp_df, region_df)
		logger('Transform', 'done')
		return merged_gdp_df
	except Exception as e:
		logger('Transform', 'ERROR: ' + str(e))
		raise e

# Load
def load(df: pd.DataFrame):
	"""
	Loads a DataFrame into memory. The method creates an in-memory copy of the input DataFrame
	and assigns it to the global variable `on_memory_loaded_df`. It logs the start, completion,
	and any errors encountered during the process.

	:param df: A pandas DataFrame that is to be loaded into memory.
	:type df: pd.DataFrame
	:return: None
	"""
	global on_memory_loaded_df
	try:
		logger('Load', 'start')
		on_memory_loaded_df = df.copy()
		logger('Load', 'done')
	except Exception as e:
		logger('Load', 'ERROR: ' + str(e))
		raise e

async def main():
	await ExtractorWithWeb(JSON_FILE, CRAWLING_URL).run()
	df = transform(read_json_file(JSON_FILE))
	load(df)
	display_info_with_pandas(on_memory_loaded_df)

if __name__ == '__main__':
	try:
		asyncio.run(main())
	except Exception as e:
		print(e)
		exit(1)