"""Print a single right's data.
Run: python scripts/get_right.py RT17D9E97CBF1346EABE35F9244FEF0E51
"""

import json
import sys

from helpers import MUSICAL_RIGHTS_URL, authenticate, get, load_credentials
from loguru import logger


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/get_right.py <right_id>")
    right_id = sys.argv[1]

    api_key, username, password = load_credentials()
    token = authenticate(api_key, username, password)

    response = get(f"{MUSICAL_RIGHTS_URL}/rights/{right_id}", api_key, token)
    response.raise_for_status()
    logger.info(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
