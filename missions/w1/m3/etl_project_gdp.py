from bs4 import BeautifulSoup
import requests
import pandas as pd
from etl_project_util import save_raw_data_with_backup, display_info_with_pandas, logger

JSON_FILE = 'Countries_by_GDP.json'
REGION_CSV_PATH = '/Users/admin/HMG_5th/missions/w1/data/region.csv'
CRAWLING_URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'

on_memory_loaded_df = None

# Extract gdp information with web scrapping
def extract():
	try:
		url = CRAWLING_URL
		logger('extract', 'start')
		response = requests.get(url)
		html = response.text
		data = {'raw_data':html}
		save_raw_data_with_backup(JSON_FILE, data)
		logger('extract', 'done')
		return data
	except Exception as e:
		logger('extract', 'ERROR: ' + str(e))
		raise e

def transform_html_tr_tags(trs: list):
	tr_dict = {}
	for tr in trs:
		cells = tr.find_all('td')  # Get all cells in the row
		if len(cells) > 1:  # Cell[0] is country name, cell[1] is GDP from IMF
			if cells[0].text.strip() == 'World': continue
			tr_dict[cells[0].text.strip()] = cells[1].text.replace(',', '').strip()
	return tr_dict

def trans_df_column_numeric(df: pd.DataFrame, column: str):
	df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
	return df

def merge_region_info_df(df: pd.DataFrame):
	region_df = pd.read_csv(REGION_CSV_PATH, usecols=['name', 'region'])
	region_df.rename(columns={'name': 'country'}, inplace=True)
	return pd.merge(df, region_df, how='left', on='country')  # Join dataframes on country column

# Transform data extracted by web scrapping using beautifulsoup
# DataFrame columns = GDP, country, region
def transform(data: dict):
	try:
		logger('Transform', 'start')
		soup = BeautifulSoup(data['raw_data'], 'html.parser')
		table_soup = soup.select('table.wikitable') # Find a table with class 'wikitable'
		if len(table_soup) < 1:
			logger('Transform', 'ERROR: No table found')
			raise Exception('No table found')
		if len(table_soup) > 1:
			logger('Transform', 'WARNNING: Multiple tables found')
		rows = table_soup[0].find_all('tr') # Get all rows in the table
		gdp_dict = transform_html_tr_tags(rows) # transform tr tags to dict
		gdp_df = pd.DataFrame(list(gdp_dict.items()), columns=['country', 'GDP'])
		gdp_df = trans_df_column_numeric(gdp_df, 'GDP') # Change datatype as int64
		gdp_df['GDP'] = gdp_df['GDP'] / 1000 # Change as billion unit.
		merged_gdp_df = merge_region_info_df(gdp_df)
		logger('Transform', 'done')
		return merged_gdp_df
	except Exception as e:
		logger('Transform', 'ERROR: ' + str(e))
		raise e

# Load
def load(df: pd.DataFrame):
	global on_memory_loaded_df
	try:
		logger('Load', 'start')
		on_memory_loaded_df = df.copy()
		logger('Load', 'done')
	except Exception as e:
		logger('Load', 'ERROR: ' + str(e))
		raise e

if __name__ == '__main__':
	try:
		data = extract()
		df = transform(data)
		load(df)
		display_info_with_pandas(on_memory_loaded_df)
	except Exception as e:
		print(e)
		exit(1)