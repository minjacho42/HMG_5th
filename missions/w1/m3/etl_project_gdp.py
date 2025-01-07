from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import json

LOG_FILE = 'etl_project_log.txt'
JSON_FILE = 'Countries_by_GDP.json'
REGION_CSV_PATH = '/Users/admin/HMG_5th/missions/w1/data/region.csv'

# log etl step with msg
def logger(step: str, msg: str):
	with open(LOG_FILE, 'a') as file:
		now = datetime.now()
		timestamp = now.strftime("%Y-%B-%d-%H-%M-%S") #formatting the timestamp
		file.write(f'{timestamp}, [{step.upper()}] {msg}\n')


def extract():
	gdp_dict = {}
	url = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
	logger('extract', 'start')
	response = requests.get(url)
	html = response.text
	with open(JSON_FILE, 'w') as f:
		json.dump({'raw_data':html}, f)
	logger('extract', 'done')


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
		raise
	table_soup = soup.find('table', {'class': 'wikitable'}) # Find a table with class 'wikitable'
	rows = table_soup.find_all('tr') # Get all rows in the table
	for row in rows:
		cells = row.find_all('td') # Get all cells in the row
		if len(cells) > 1: # Cell[0] is country name, cell[1] is GDP from IMF
			if cells[0].text.strip() == 'World': continue
			gdp_dict[cells[0].text.strip()] = cells[1].text.replace(',', '').strip()
	gdp_df = pd.DataFrame(list(gdp_dict.items()), columns=['Country', 'GDP'])
	gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce').astype('Int64') # Change datatype as int64
	gdp_df['GDP'] = gdp_df['GDP'] / 1000 # Change as billion unit.
	region_df = pd.read_csv(REGION_CSV_PATH)
	region_df = pd.DataFrame({'Country' : region_df['name'], 'Region':region_df['region']}) # Get region info in csv file
	merged_gdp_df = pd.merge(gdp_df, region_df, how='left', on='Country') # Join dataframes on country column
	logger('Transform', 'done')
	return merged_gdp_df

def load(gdp_df: pd.DataFrame):
	logger('Load', 'start')
	print("\033[31m--- Country have more than 100B GDP ---\033[0m")
	pd.options.display.float_format = "{:.2f}".format # 소수점 둘째자리 까지 프린트
	pd.options.display.max_rows = 100 # 최대 row 개수 조정
	print(gdp_df[gdp_df['GDP'] >= 100])
	print()
	print("\033[31m--- Each Region's mean GDP of top 5 country ---\033[0m")
	for idx, region in enumerate(gdp_df['Region'].unique()):
		if pd.notna(region):
			print(f"\033[{32+idx}m{region.upper():8}\033[0m : {gdp_df[gdp_df['Region'] == region].sort_values(ascending=False, by='GDP').head(5)['GDP'].mean():.2f}")
	logger('Load', 'done')

if __name__ == '__main__':
	extract()
	load(transform())
