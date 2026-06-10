import google.auth
from google.auth.transport.requests import Request
import logging_utils

logger = logging_utils.get_logger()

def _get_auth_token() -> str:
    credentials, _ = google.auth.default()
    credentials.refresh(Request())
    return credentials.token

def fetch_api_response(request_func, url: str, user_project: str, json_body: dict = None) -> dict:
    headers = {
        "Authorization": f"Bearer {_get_auth_token()}",
        "x-goog-user-project": user_project,
        "Content-Type": "application/json"
    }
    try:
        kwargs = {"headers": headers}
        if json_body is not None:
            kwargs["json"] = json_body
        response = request_func(url, **kwargs)
        if response.status_code >= 400:
            return {"error_msg": f"HTTP {response.status_code}: {response.text}", "json": None}
        return {"error_msg": None, "json": response.json() if response.text else {}}
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"error_msg": str(e), "json": None}
