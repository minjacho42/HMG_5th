import json
import requests
import pandas as pd
from etl_logger import logger
from etl_display_info import display_info_with_pandas

JSON_FILE = 'Countries_by_GDP_API.json'
REGION_CSV_PATH = '/Users/admin/HMG_5th/missions/w1/data/region.csv'

# Extract gdp information with imf api
def extract():
	try:
		logger('Extract-API', 'start')
		ngdpd_url = "https://www.imf.org/external/datamapper/api/v1/NGDPD"
		country_url = "https://www.imf.org/external/datamapper/api/v1/countries"
		ngdpd_response = requests.get(ngdpd_url)
		country_response = requests.get(country_url)
		with open(JSON_FILE, 'w') as f:
			json.dump({'ngdpd':ngdpd_response.json(), 'country':country_response.json()}, f)
		logger('Extract-API', 'done')
	except Exception as e:
		logger('Extract-API', 'ERROR: ' + str(e))
		raise e

# Transform data extracted with imf api and return dataframe
# DataFrame columns = GDP, country, region
def transform():
	try:
		logger('Transform-API', 'start')
		with open(JSON_FILE, 'r') as f: # get extracted data by json
			data = json.load(f)
		gdp_df = pd.DataFrame(data['ngdpd']['values']['NGDPD']).T
		country_df = pd.DataFrame(data['country']['countries']).T
		continent_df = pd.read_csv('/Users/admin/HMG_5th/missions/w1/data/continents2.csv')
		region_df = continent_df[['alpha-3', 'region']].set_index('alpha-3')
		gdp_df = gdp_df.join(country_df)
		gdp_df = gdp_df.join(region_df)
		transformed_df = gdp_df[['label', '2025', 'region']].copy()
		transformed_df.rename(columns={'2025': 'GDP', 'label': 'country'}, inplace=True)
		transformed_df.dropna(subset=['country', 'region'], inplace=True)
		transformed_df.sort_values(by='GDP', ascending=False, inplace=True)
		transformed_df.reset_index(drop=True, inplace=True)
		logger('Transform-API', 'done')
		return transformed_df
	except Exception as e:
		logger('Transform-API', 'ERROR: ' + str(e))
		raise e

# Load
def load(df: pd.DataFrame):
	try:
		logger('Load-API', 'start')
		logger('Load-API', 'done')
	except Exception as e:
		logger('Load-API', 'ERROR: ' + str(e))
		raise e

if __name__ == '__main__':
	try:
		extract()
		df = transform()
		load(df)
		display_info_with_pandas(df)
	except Exception as e:
		print(e)
		exit(1)