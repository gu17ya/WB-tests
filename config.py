from utils.environment import get_string_environment

BASE_URL = get_string_environment("WB_BASE_URL", required=False, default="https://whitebit.com")
MARKET = "DBTC_DUSDT"
REQUEST_TIMEOUT = 10
MAX_RESPONSE_TIME = 0.2  # seconds
