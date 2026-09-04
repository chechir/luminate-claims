#!/usr/bin/env python3
"""Validate: "once we authenticate there should be an interface that is
straightforward" (docs/slack_meessages.txt).

Auths against the Musical Rights API, then walks the read-only endpoints
with the resulting token — no undocumented steps in between — logging
full response bodies so the actual data shape is visible, not just
pass/fail. Run: python scripts/validate_auth_interface.py
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass

import requests
from helpers import AUTH_URL, MUSICAL_RIGHTS_URL, load_credentials
from loguru import logger

# Provided by Luminate for review, see docs/email_thread.txt.
SAMPLE_CLAIM_REQUEST_ID = "CRF7671AB5D62D44DABF6414CA3A0B9499"


@dataclass
class StepResult:
    name: str
    ok: bool
    status_code: int | None
    detail: str


def main() -> None:
    api_key, username, password = load_credentials()

    start = time.monotonic()
    auth_result = authenticate(api_key, username, password)
    if isinstance(auth_result, StepResult):
        report([auth_result])
        sys.exit(1)
    token = auth_result

    results = [
        StepResult("authenticate", True, 200, f"{time.monotonic() - start:.2f}s")
    ]
    results.append(
        get("business_units", f"{MUSICAL_RIGHTS_URL}/business_units", api_key, token)
    )
    results.append(
        get(
            "claim_requests (list)",
            f"{MUSICAL_RIGHTS_URL}/claim_requests",
            api_key,
            token,
        )
    )
    results.append(
        get(
            "claim_requests/{id}",
            f"{MUSICAL_RIGHTS_URL}/claim_requests/{SAMPLE_CLAIM_REQUEST_ID}",
            api_key,
            token,
        )
    )
    report(results)
    sys.exit(0 if all(r.ok for r in results) else 1)


def authenticate(api_key: str, username: str, password: str) -> StepResult | str:
    logger.info("POST /auth")
    response = requests.post(
        AUTH_URL,
        headers={"x-api-key": api_key, "accept": "application/json"},
        data={"username": username, "password": password},
        timeout=10,
    )
    log_response(response)
    import pdbp

    pdbp.set_trace()

    if not response.ok:
        return StepResult("authenticate", False, response.status_code, response.text)
    token = response.json().get("access_token")
    if not token:
        return StepResult(
            "authenticate", False, response.status_code, "no access_token in response"
        )
    logger.success("authenticated, access_token acquired")
    return token


def get(name: str, url: str, api_key: str, token: str) -> StepResult:
    logger.info(f"GET {url}")
    response = requests.get(
        url,
        headers={
            "x-api-key": api_key,
            "authorization": token,
            "accept": "application/json",
        },
        timeout=10,
    )

    log_response(response)
    detail = response.text[:200] if not response.ok else f"{len(response.text)} bytes"
    return StepResult(name, response.ok, response.status_code, detail)


def log_response(response: requests.Response) -> None:
    """Dump the full body — this script exists to see the data, not just pass/fail."""
    level = logger.debug if response.ok else logger.warning
    try:
        level(f"{response.status_code} <- {json.dumps(response.json(), indent=2)}")
    except ValueError:
        level(f"{response.status_code} <- {response.text}")


def report(results: list[StepResult]) -> None:
    for r in results:
        print(f"[{'OK' if r.ok else 'FAIL'}] {r.name} ({r.status_code}) — {r.detail}")

    all_ok = all(r.ok for r in results)
    print()
    if all_ok:
        print(
            "Assumption holds: auth -> access_token -> authenticated GET calls worked "
            "with no undocumented steps, using only the auth + api-reference pages."
        )
    else:
        print(
            "Assumption doesn't hold as-is: at least one call failed. See FAIL lines "
            "for the gap between the docs and what the API actually needs."
        )


if __name__ == "__main__":
    main()
