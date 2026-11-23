import requests

import config
from utils.logger import get_logger


class BaseApiService:
    """HTTP session, base URL and request logging shared by all API services."""

    def __init__(self, base_url: str = config.BASE_URL, timeout: float = config.REQUEST_TIMEOUT):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._logger = get_logger(type(self).__name__)

    def close(self) -> None:
        self._session.close()

    def _get(self, path: str, **params) -> requests.Response:
        return self._send("GET", path, params=params)

    def _send(self, method: str, path: str, **kwargs) -> requests.Response:
        response = self._session.request(method, self._base_url + path, timeout=self._timeout, **kwargs)
        self._logger.info("%s %s -> %s (%d ms)", method, path, response.status_code, response.elapsed.total_seconds() * 1000)
        self._logger.debug("request: %s\nresponse: %s", kwargs.get("data"), response.text)
        return response
