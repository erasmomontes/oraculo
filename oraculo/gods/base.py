import abc
import json
import requests
from .exceptions import NotFound, BadRequest, CantAuthenticate


class BaseAPIClient(abc.ABC):
    _headers_base = {'content-type': 'application/json'}
    _params_base = dict()

    @property
    @abc.abstractmethod
    def base_url(self):
        return 'Should set base_url property'

    def __init__(self):
        self.authenticate()

    @abc.abstractmethod
    def authenticate(self, exception=CantAuthenticate):
        """Method documentation"""
        return

    def get(self, url, params=None):
        if params and isinstance(params, dict):
            self._params_base.update(params)

        request = requests.get(
            self.base_url + url,
            params=self._params_base,
            headers=self._headers_base)

        if request.status_code is 200:
            return request.json()

        if request.status_code is 401:
            self.autheticate()
            self.get(url, params)

        if request.status_code is 403:
            self.authenticated()
            self.get(url, params)

        if request.status_code is 404:
            raise NotFound(request.context)

    def post(self, url, body, params=None):
        if params:
            self._params_base.update(params)
        request = requests.post(
            self.base_url + url,
            data=json.dumps(body),
            headers=self._headers_base,
            params=self._params_base)

        if request.status_code == 200:
            return request.json()

        if request.status_code == 400:
            raise BadRequest(request.json().get('message'))

        if request.status_code is 401:
            self.autheticate()
            self.get(url, params)

        if request.status_code == 403:
            self.authenticate()
            self.post(url, body)

        if request.status_code == 404:
            raise NotFound(request.context)

    def patch(self, url, pk):
        url = "{self.base_url}{url}/{pk}"
        request = requests.patch(
            url=url, headers=self._headers_base, params=self._params_base)
