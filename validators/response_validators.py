import requests

import config
from utils.step import step


def validate_status(response: requests.Response, status: int = 200):
    """Assert the HTTP status and return the JSON body."""
    assert response.status_code == status, f"{response.request.url}: {response.status_code} {response.text}"
    return response.json()


@step("Validate response time < {limit}s")
def validate_response_time(response: requests.Response, limit: float = config.MAX_RESPONSE_TIME) -> None:
    elapsed = response.elapsed.total_seconds()
    assert elapsed < limit, f"{response.request.url}: response time {elapsed:.3f}s >= {limit}s"
