import pandas as pd
import asyncio
from etl_project_logger import logger
from etl_project_util import display_info_with_pandas, read_json_file
from extractor import ExtractorWithAPI

JSON_FILE = 'Countries_by_GDP_API.json'
REGION_CSV_PATH = '../data/region.csv'
CONTINENT_CSV_PATH = '../data/continents2.csv'
API_BASE_URL = 'https://www.imf.org/external/datamapper/api/v1/'

on_memory_loaded_df = None

def join_country_region_df(df: pd.DataFrame, country_df: pd.DataFrame, region_df: pd.DataFrame):
	df = df.join(country_df, how='left')
	df = df.join(region_df, how='left')
	return df

# Transform data extracted from the IMF API and return a DataFrame
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

async def main():
	# Use ExtractorWithAPI to extract data from api
	extractor_with_api = ExtractorWithAPI(JSON_FILE, API_BASE_URL, ['NGDPD', 'countries'])
	await extractor_with_api.run()
	df = transform(read_json_file(JSON_FILE))
	load(df)
	display_info_with_pandas(on_memory_loaded_df)

if __name__ == '__main__':
	try:
		asyncio.run(main())
	except Exception as e:
		print(e)
		exit(1)