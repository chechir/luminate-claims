# Luminate Musical Rights API

Scripts for querying Luminate's Musical Rights API. No UI — everything here is a
command you run and JSON you read. Background/credentials: `docs/email_thread.txt`,
`docs/slack_meessages.txt`. API docs: https://docs.luminatedata.com/docs/musical-rights-api

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with the API key, username, and password from the Luminate onboarding
email (`docs/email_thread.txt`). `.env` is gitignored — never commit it.

## Scripts

**Get details on a specific right** (ownership/distribution record, including
conflicts if any):

```bash
python scripts/get_right.py RT17D9E97CBF1346EABE35F9244FEF0E51
```

**Export all business units to parquet** (`data/business_units.parquet`) — the
label/sublabel hierarchy Luminate has configured, including Firebird's:

```bash
python scripts/export_business_units.py
```

`scripts/validate_auth_interface.py` is a dev script for exercising the API
end-to-end (auth → business units → claims list → claim detail); it currently has
debugger breakpoints in it, so don't run it expecting clean output.

## What the API can do

- Query a specific claim (`GET /claim_requests/{id}`)
- List all our claims (`GET /claim_requests`)
- Get business units (`GET /business_units`)
- List rights (`GET /rights`)
- Get right details, including conflicts (`GET /rights/{id}`)
- Submit a claim (`POST /claim_requests`) — not yet exercised; claims can't be
  reversed today (no test/sandbox environment), so treat this as a real write.

## Known limits

- **Rate limit: 1 request/second.** Loop tighter than that and calls 404 instead
  of a clean 429 — see `REQUEST_INTERVAL_SECONDS` in `export_business_units.py`.
- **10,000 requests/month** total on this account.
- Claims process in batches every 30 min, 5am–4:30pm PT / 8am–7:30pm ET only;
  outside that window requests queue.

## Layout

- `scripts/helpers.py` — shared auth (`load_credentials`, `authenticate`, `get`)
  and base URLs. Everything else imports from here.
- `data/` — script output (gitignored contents aside from what you choose to commit).
