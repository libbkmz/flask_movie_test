from datetime import datetime, timedelta
from urllib.parse import urljoin
import requests as req


class DataProvider:
    URL = "https://ghibliapi.herokuapp.com/"
    CACHE_EXPIRY = timedelta(seconds=60)

    FILMS_KEY = "films"
    PEOPLE_KEY = "people"

    def __init__(self):
        self.req_cache = {}

    def clear(self):
        self.req_cache = {}

    # simple implementation of requests with cache
    def _request(self, key):
        # @TODO: key more reliable in case of hash collisions
        if key in self.req_cache:
            resp = self.req_cache[key]
            if resp.cache_date + self.CACHE_EXPIRY >= datetime.now():
                resp.from_cache = True
                return resp

        url = urljoin(self.URL, key)
        # @TODO: for better performance we can load the data in background
        #  while return the user cached version
        resp = req.get(url)
        resp.cache_date = datetime.now()
        resp.from_cache = False

        self.req_cache[key] = resp
        return resp

    @property
    def films(self):
        films_res = self._request("films")
        people_res = self._request("people")
        if not films_res.ok or not people_res.ok:
            raise req.exceptions.RequestException

        films = films_res.json()
        people = people_res.json()

        films = {x["id"]: x for x in films}
        for f in films.values():
            f["people"] = []

        for person in people:
            for film in person["films"]:
                film_id = film.rsplit("/", 1)[-1]
                films[film_id]["people"].append(person)

        return list(films.values()), (
            films_res.cache_date,
            people_res.cache_date,
        )
