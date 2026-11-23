from services.base_api_service import BaseApiService
from utils.step import step


class WhiteBitPublicService(BaseApiService):
    @step("Get markets")
    def get_markets(self):
        return self._get("/api/v4/public/markets")

    @step("Get ticker")
    def get_ticker(self):
        return self._get("/api/v4/public/ticker")
