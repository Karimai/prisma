import requests
import logging

from http import HTTPStatus


class API:
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    def get(self, params):
        response = requests.get(self.url, headers=self.headers, params=params)
        if response.status_code != HTTPStatus.OK:
            logging.error(f"Failed to retrieve data: {response.text}")
            raise Exception(f"Failed to retrieve data: {response.text}")
        logging.info(f"API call to {self.url} was successful")
        return response.json()
