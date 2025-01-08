from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
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
	except Exception as e:
		logger('extract', 'ERROR: ' + str(e))
		raise e

# Transform data extracted by web scrapping using beautifulsoup
# DataFrame columns = GDP, country, region
def transform(file_name: str = JSON_FILE):
	try:
		logger('Transform', 'start')
		data = {}
		gdp_dict = {}
		with open(file_name, 'r') as f:
			data = json.load(f)
		soup = BeautifulSoup(data['raw_data'], 'html.parser')
		table_soup = soup.select('table.wikitable')
		if len(table_soup) < 1:
			logger('Transform', 'ERROR: No table found')
			raise Exception('No table found')
		table_soup = soup.find('table', {'class': 'wikitable'}) # Find a table with class 'wikitable'
		rows = table_soup.find_all('tr') # Get all rows in the table
		for row in rows:
			cells = row.find_all('td') # Get all cells in the row
			if len(cells) > 1: # Cell[0] is country name, cell[1] is GDP from IMF
				if cells[0].text.strip() == 'World': continue
				gdp_dict[cells[0].text.strip()] = cells[1].text.replace(',', '').strip()
		gdp_df = pd.DataFrame(list(gdp_dict.items()), columns=['country', 'GDP'])
		gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce').astype('Int64') # Change datatype as int64
		gdp_df['GDP'] = gdp_df['GDP'] / 1000 # Change as billion unit.
		region_df = pd.read_csv(REGION_CSV_PATH)
		region_df = pd.DataFrame({'country' : region_df['name'], 'region':region_df['region']}) # Get region info in csv file
		merged_gdp_df = pd.merge(gdp_df, region_df, how='left', on='country') # Join dataframes on country column
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
		extract()
		df = transform()
		load(df)
		display_info_with_pandas(on_memory_loaded_df)
	except Exception as e:
		print(e)
		exit(1)