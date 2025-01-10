from abc import *
import asyncio
import aiohttp
import aiofiles
from datetime import datetime
import json
from etl_project_logger import logger

# Abstract Base Class for Extractor
class AbstractExtractor(ABC):
    def __init__(self, file_path:str):
        self._file_path = file_path

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def save(self):
        pass

# A concrete implementation of Extractor that scrapes data from a single web URL.
# Retries the request (`max_tries`) times with timeout.
class ExtractorWithWeb(AbstractExtractor):
    def __init__(self, file_path:str, url:str, max_tries:int=3, timeout:int=10):
        super().__init__(file_path)
        self.__url = url
        self.__max_tries = max_tries
        self.__timeout = timeout
        self._raw_data = None

    # Sends an asynchronous GET request to URL using aiohttp ClientSession.
    async def __request_get_url(self, session, url):
        async with session.get(url, ssl=False, timeout=self.__timeout) as response:
            if response.status == 200:
                return await response.text()
            else:
                response.raise_for_status()

    # Scrapping the website asynchronously.
    # Retries the request up to `max_tries` times on failure.
    async def run(self):
        trial = 1
        try:
            async with aiohttp.ClientSession() as session:
                while trial < self.__max_tries:
                    logger('Extract-Web', f'Requesting {self.__url} (Trial {trial})...')
                    try:
                        self._raw_data = await self.__request_get_url(session, self.__url)
                        break
                    except Exception as e:
                        if trial >= self.__max_tries: # If the trial reaches the 'max tries' limit, raise an error.
                            logger('Extract-Web', f'ERROR: {self.__url} (Trial {trial})')
                            raise e
                        else:
                            logger('Extract-Web', f'WARNING: {self.__url} (Trial {trial})')
                            trial += 1
        except Exception as e:
            logger('Extract-Web', 'ERROR: ' + str(e))
            print(e)
        finally: # Save the result regardless of whether the scraping succeeds or fails.
            await self.save()

    # Saves the scraped data (if successful) to the specified file path as a JSON object.
    # Includes metadata about when the data was saved and whether the operation failed.
    async def save(self):
        data = {
            'data': self._raw_data,
            'meta_data': {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'broken': self._raw_data is None,
            }
        }
        async with aiofiles.open(self._file_path, 'w') as f:
            await f.write(json.dumps(data))

# A concrete implementation of Extractor for fetching data from API endpoints.
# Handles multiple endpoints, retries failed requests, and stores the results in a JSON file.
class ExtractorWithAPI(AbstractExtractor):
    def __init__(self, file_path:str, base_url:str, end_points:list[str], max_tries:int=3, timeout:int=10):
        super().__init__(file_path)
        self._raw_data = {}
        self.__base_url = base_url
        self.__end_points = end_points
        self.__max_tries = max_tries
        self.__timeout = timeout
        self.__broken_end_points = []

    # Sends an asynchronous GET request to a specific endpoint of the base URL.
    async def __request_get_url_json(self, session, endpoint):
        async with session.get(self.__base_url + endpoint, ssl=False, timeout=self.__timeout) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()

    # Attempts to fetch data from all API endpoints.
    # Retries failed requests up to `max_tries` times and logs the results.
    # Tracks endpoints that fail consistently and stores their list in `__broken_end_points`.
    async def run(self):
        try:
            target_end_points = self.__end_points.copy()
            trial = 1
            async with aiohttp.ClientSession() as session:
                while target_end_points and trial < self.__max_tries:
                    if trial > 1:
                        logger('Extract-API', f'Retrying request...')
                    # Use `gather` to retrieve the results of multiple asynchronous requests at once.
                    results = \
                        await asyncio.gather(*[self.__request_get_url_json(session, target_end_point) for target_end_point in target_end_points],
                                       return_exceptions=True)
                    new_target_end_points = [] # Endpoints which are broken on the request above
                    for end_point, result in zip(target_end_points, results):
                        if isinstance(result, Exception): # If the request was failed
                            logger('Extract-API', f'WARNING: {end_point}' + str(result))
                            new_target_end_points.append(end_point)
                        else: # If the request success
                            self._raw_data[end_point] = result
                    trial += 1
                    target_end_points = new_target_end_points
            # Store the list of failed endpoints to include them in the metadata of the JSON file.
            self.__broken_end_points = target_end_points
        except Exception as e:
            logger('Extract-API', 'ERROR: ' + str(e))
            print(e)
        finally:
            await self.save()

    # Saves the API results (_raw_data) to the specified file path as a JSON object.
    # Includes metadata such as the timestamp, whether any endpoints failed, and broken endpoint details.
    async def save(self):
        data = {
            'data': self._raw_data,
            'meta_data': {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'broken': len(self.__broken_end_points) > 0,
                'broken_end_points': self.__broken_end_points,
            }
        }
        async with aiofiles.open(self._file_path, 'w') as f:
            await f.write(json.dumps(data))

    class BrokenEndpointExistError(Exception):
        pass