"""Shared Luminate Musical Rights API config/auth for scripts/*.py.

Auth flow: https://docs.luminatedata.com/docs/authentication
Account is rate-limited to 1 request/second (docs/email_thread.txt) —
callers that loop (pagination, batch claims) must throttle themselves.
"""

import os
import sys

import requests
from dotenv import load_dotenv

BASE_URL = "https://api.luminatedata.com"
AUTH_URL = f"{BASE_URL}/auth"
MUSICAL_RIGHTS_URL = f"{BASE_URL}/musical_rights"


def load_credentials() -> tuple[str, str, str]:
    load_dotenv()
    api_key = os.environ.get("LUMINATE_API_KEY")
    username = os.environ.get("LUMINATE_USERNAME")
    password = os.environ.get("LUMINATE_PASSWORD")
    if not all([api_key, username, password]):
        sys.exit("Missing credentials. Copy .env.example to .env and fill it in.")
    return api_key, username, password  # type: ignore[return-value]


def authenticate(api_key: str, username: str, password: str) -> str:
    response = requests.post(
        AUTH_URL,
        headers={"x-api-key": api_key, "accept": "application/json"},
        data={"username": username, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def auth_headers(api_key: str, token: str) -> dict[str, str]:
    return {"x-api-key": api_key, "authorization": token, "accept": "application/json"}


def get(url: str, api_key: str, token: str, **kwargs) -> requests.Response:
    return requests.get(url, headers=auth_headers(api_key, token), timeout=10, **kwargs)
