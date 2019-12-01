import datetime
import os
import sys
from unittest import TestCase
from datetime import timedelta
from time import sleep
import json
from urllib.parse import urljoin

import requests
import responses
from api import DataProvider
from main import create_app, data_provider

CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))


class TestDataProvider(TestCase):
    def setUp(self):
        with open(os.path.join(CURRENT_FOLDER, "static_data", "valid_films_response.json"), "r") as hl:
            self.films_json = json.loads(hl.read())

        with open(os.path.join(CURRENT_FOLDER, "static_data", "valid_people_response.json"), "r") as hl:
            self.people_json = json.loads(hl.read())

    def test_films_cache_expiration(self):
        obj = DataProvider()
        obj.CACHE_EXPIRY = timedelta(seconds=2)
        _, timings1 = obj.films

        sleep(1)
        _, timings2 = obj.films

        self.assertEqual(timings1, timings2)
        sleep(1)
        _, timings3 = obj.films

        self.assertGreater(timings3, timings2)

    def test_request(self):
        obj = DataProvider()
        obj.CACHE_EXPIRY = timedelta(seconds=600)
        response1 = obj._request(DataProvider.FILMS_KEY)
        response2 = obj._request(DataProvider.FILMS_KEY)
        self.assertEqual(response1.cache_date, response2.cache_date)
        obj.CACHE_EXPIRY = timedelta(seconds=0)
        response3 = obj._request(DataProvider.FILMS_KEY)

        self.assertNotEqual(response2.cache_date, response3.cache_date)

    def test_request_with_mock(self):
        with responses.RequestsMock() as rsps:
            rsps.add("GET", urljoin(DataProvider.URL, DataProvider.FILMS_KEY), json=self.films_json)
            rsps.add("GET", urljoin(DataProvider.URL, DataProvider.PEOPLE_KEY), json=self.people_json)
            obj = DataProvider()
            films, timestamps = obj.films

            self.assertEqual(len(films), 20)

    def test_request_with_mock_with_errors(self):
        with responses.RequestsMock() as rsps:
            rsps.add("GET", urljoin(DataProvider.URL, DataProvider.FILMS_KEY), status=500)
            rsps.add("GET", urljoin(DataProvider.URL, DataProvider.PEOPLE_KEY), status=500)
            obj = DataProvider()
            with self.assertRaises(requests.exceptions.RequestException) as cm:
                films, timestamp = obj.films

            app = create_app()
            app.testing = False
            client = app.test_client()
            res = client.get("/movies")
            self.assertIn(b"No data from External API", res.data)

    def test_not_valid_text_in_templates(self):
        data_provider.clear()
        app = create_app()
        app.testing = True
        client = app.test_client()

        with responses.RequestsMock() as rsps:
            rsps.add("GET", urljoin(DataProvider.URL, DataProvider.FILMS_KEY), status=500)
            rsps.add("GET", urljoin(DataProvider.URL, DataProvider.PEOPLE_KEY), status=500)

            res = client.get("/movies")
            self.assertIn(b"No data from External API", res.data)

    def test_valid_text_in_templates(self):
        data_provider.clear()
        app = create_app()
        app.testing = True
        client = app.test_client()

        res = client.get("/movies")
        self.assertNotIn(b"No data from External API", res.data)

