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

class ExtractorWithWeb(AbstractExtractor):
    """
    Handles web scraping functionality by performing asynchronous HTTP GET requests to a given URL.
    Extracts and saves the data to a specified file path in JSON format.

    This class is designed to retry the web scraping operation a specified number of times
    in case of failures. It leverages aiohttp for asynchronous HTTP requests and aiofiles
    for non-blocking file I/O operations.

    :ivar _raw_data: Raw data extracted from the URL.
    :type _raw_data: Optional[str]
    :ivar __url: Target URL to scrape content from.
    :type __url: str
    :ivar __max_tries: Maximum number of retry attempts to fetch the URL.
    :type __max_tries: int
    :ivar __timeout: Timeout duration in seconds for HTTP requests.
    :type __timeout: int
    """
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

    async def run(self):
        """
        Performs an asynchronous attempt to retrieve data from the given URL with a specified
        number of retry attempts in case of failure. If the maximum number of retries is reached
        and all attempts to retrieve the data fail, an exception will be raised. Upon completion,
        regardless of success or failure, the function ensures that the result is saved.
        """
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

    async def save(self):
        """
        Asynchronously saves the current object's raw data and metadata to a file.
        The method collects the raw data and constructs metadata including the
        current date and time, and a flag indicating whether the raw data is null.
        These are then written to a specified file in JSON format.
        """
        data = {
            'data': self._raw_data,
            'meta_data': {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'broken': self._raw_data is None,
            }
        }
        async with aiofiles.open(self._file_path, 'w') as f:
            await f.write(json.dumps(data))

class ExtractorWithAPI(AbstractExtractor):
    """
    This class is designed to extract data from APIs by making asynchronous
    GET requests to the specified endpoints. It retries failed requests
    up to a configurable number of attempts and stores data in a structured
    file format. Additionally, it tracks consistently failing endpoints for
    reporting or further analysis.

    The class is initialized with the essential parameters required for HTTP
    communication, such as base URL, endpoints, and timeout configurations. Upon
    execution, it fetches data asynchronously from the endpoints and saves the
    results along with metadata.

    :ivar _raw_data: Stores the successfully fetched data categorized by endpoints.
    :type _raw_data: dict
    :ivar __base_url: Base URL to which the endpoints are appended to form full URLs.
    :type __base_url: str
    :ivar __end_points: List of relative API endpoints to fetch data from.
    :type __end_points: list of str
    :ivar __max_tries: Maximum number of retry attempts for failed endpoints.
    :type __max_tries: int
    :ivar __timeout: Timeout duration in seconds for API requests.
    :type __timeout: int
    :ivar __broken_end_points: List of endpoints that failed after all retry attempts.
    :type __broken_end_points: list of str
    """
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

    async def run(self):
        """
        Executes the asynchronous logic to perform HTTP GET requests against multiple target endpoints and
        collects their JSON responses. The method retries failed requests up to a predefined maximum number
        of attempts, and logs warnings for individual endpoint failures. It tracks successfully retrieved
        data and endpoints that eventually failed after all retry attempts. Finally, it invokes the save
        method to store the results.
        """
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

    async def save(self):
        """
        Save the current state of the object to a file asynchronously.

        This method writes the object's raw data and metadata to a specified file
        in JSON format. The metadata includes the current date and time, a flag
        indicating whether there are broken endpoints, and a list of the broken
        endpoints.
        """
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