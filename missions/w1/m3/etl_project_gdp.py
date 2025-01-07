from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
from etl_logger import logger
from etl_display_info import display_info_with_pandas

JSON_FILE = 'Countries_by_GDP.json'
REGION_CSV_PATH = '/Users/admin/HMG_5th/missions/w1/data/region.csv'

# Extract gdp information with web scrapping
def extract():
	gdp_dict = {}
	url = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
	logger('extract', 'start')
	response = requests.get(url)
	html = response.text
	with open(JSON_FILE, 'w') as f:
		json.dump({'raw_data':html}, f)
	logger('extract', 'done')

# Transform data extracted by web scrapping using beautifulsoup
# DataFrame columns = GDP, country, region
def transform():
	logger('Transform', 'start')
	data = {}
	gdp_dict = {}
	with open(JSON_FILE, 'r') as f:
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

# Load
def load(df: pd.DataFrame):
	logger('Load', 'start')
	display_info_with_pandas(df)
	logger('Load', 'done')

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
	except Exception as e:
		logger('Load', 'ERROR: ' + str(e))
		print(e)
		exit(1)