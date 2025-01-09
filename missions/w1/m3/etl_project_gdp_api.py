import json
import requests
import pandas as pd
from etl_project_util import save_raw_data_with_backup, display_info_with_pandas, logger

JSON_FILE = 'Countries_by_GDP_API.json'
REGION_CSV_PATH = '/Users/admin/HMG_5th/missions/w1/data/region.csv'
CONTINENT_CSV_PATH = '/Users/admin/HMG_5th/missions/w1/data/continents2.csv'
API_BASE_URL = 'https://www.imf.org/external/datamapper/api/v1/'

on_memory_loaded_df = None

# Request based on url and endpoint
def request_get_url(url, endpoint):
	try:
		response = requests.get(url + endpoint)
		if response.status_code == 200:
			return response.json()
		else:
			raise requests.exceptions.RequestException
	except Exception as e:
		logger('Request-Get-URL', 'ERROR: ' + str(e))
		raise e

# Extract gdp information with imf api
def extract(end_points: tuple = ('NGDPD', 'countries')):
	try:
		logger('Extract-API', 'start')
		data = {}
		for endpoint in end_points:
			data[endpoint] = request_get_url(API_BASE_URL, endpoint)
		save_raw_data_with_backup(JSON_FILE, data)
		logger('Extract-API', 'done')
		return data
	except Exception as e:
		logger('Extract-API', 'ERROR: ' + str(e))
		raise e

def join_country_region_df(df: pd.DataFrame, country_df: pd.DataFrame, region_df: pd.DataFrame):
	df = df.join(country_df, how='left')
	df = df.join(region_df, how='left')
	return df

# Transform data extracted with imf api and return dataframe
# DataFrame columns = GDP, country, region
def transform(data: dict):
	try:
		logger('Transform-API', 'start')
		# Extract GDP DataFrame index = Country Code, columns = year, value = GDP of year
		gdp_df = pd.DataFrame(data['NGDPD']['values']['NGDPD']).T
		# Extract Country DataFrame index = Country Code, columns = label, value = Country string
		country_df = pd.DataFrame(data['countries']['countries']).T
		country_df.rename(columns={'label': 'country'}, inplace=True)
		# Extract continent info from continent csv
		region_df = pd.read_csv(CONTINENT_CSV_PATH, usecols=['alpha-3', 'region'], index_col='alpha-3')
		gdp_df = join_country_region_df(gdp_df, country_df, region_df)
		transformed_df = gdp_df[['country', '2025', 'region']].copy()
		transformed_df.rename(columns={'2025': 'GDP'}, inplace=True)
		transformed_df.dropna(subset=['country'], inplace=True)
		transformed_df.sort_values(by='GDP', ascending=False, inplace=True)
		transformed_df.reset_index(drop=True, inplace=True)
		logger('Transform-API', 'done')
		return transformed_df
	except KeyError as e:
		logger('Transform-API', 'ERROR: Not Valid RAW Data')
		raise e
	except Exception as e:
		logger('Transform-API', 'ERROR: ' + str(e))
		raise e

# Load
def load(df: pd.DataFrame):
	global on_memory_loaded_df
	try:
		logger('Load-API', 'start')
		on_memory_loaded_df = df.copy()
		logger('Load-API', 'done')
	except Exception as e:
		logger('Load-API', 'ERROR: ' + str(e))
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