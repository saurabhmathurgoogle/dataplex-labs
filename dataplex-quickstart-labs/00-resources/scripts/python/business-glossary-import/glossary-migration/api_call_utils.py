import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import google.auth
from google.auth.transport.requests import Request
import logging_utils

logger = logging_utils.get_logger()

_session = requests.Session()
_retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PATCH", "PUT"],
    backoff_factor=1
)
_adapter = HTTPAdapter(max_retries=_retry_strategy, pool_connections=10, pool_maxsize=10)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)

def _get_auth_token() -> str:
    credentials, _ = google.auth.default()
    credentials.refresh(Request())
    return credentials.token

def fetch_api_response(method: str, url: str, user_project: str, json_body: dict = None) -> dict:
    headers = {
        "Authorization": f"Bearer {_get_auth_token()}",
        "x-goog-user-project": user_project,
        "Content-Type": "application/json"
    }
    try:
        kwargs = {"headers": headers}
        if json_body is not None:
            kwargs["json"] = json_body
        response = _session.request(method, url, **kwargs)
        if response.status_code >= 400:
            return {"error_msg": f"HTTP {response.status_code}: {response.text}", "json": None}
        return {"error_msg": None, "json": response.json() if response.text else {}}
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"error_msg": str(e), "json": None}
