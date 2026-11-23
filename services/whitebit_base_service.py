import base64
import hashlib
import hmac
import json
import time

import requests

from services.base_api_service import BaseApiService
from utils.environment import get_string_environment


class WhiteBitBaseService(BaseApiService):
    """Signed POST requests to the private API (X-TXC-APIKEY / X-TXC-PAYLOAD / X-TXC-SIGNATURE)."""

    def __init__(self):
        super().__init__()
        self._api_key = get_string_environment("WB_API_KEY")
        self._api_secret = get_string_environment("WB_API_SECRET").encode()
        self._last_nonce = 0

    def _post(self, path: str, **params) -> requests.Response:
        body = json.dumps(
            {**params, "request": path, "nonce": self._next_nonce(), "nonceWindow": True}, separators=(",", ":")
        )
        return self._send("POST", path, data=body, headers=self._sign(body))

    def _sign(self, body: str) -> dict:
        payload = base64.b64encode(body.encode()).decode()
        return {
            "Content-Type": "application/json",
            "X-TXC-APIKEY": self._api_key,
            "X-TXC-PAYLOAD": payload,
            "X-TXC-SIGNATURE": hmac.new(self._api_secret, payload.encode(), hashlib.sha512).hexdigest(),
        }

    def _next_nonce(self) -> int:
        self._last_nonce = max(int(time.time() * 1000), self._last_nonce + 1)
        return self._last_nonce
