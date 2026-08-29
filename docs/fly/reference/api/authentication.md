---
title: Authentication
weight: 1
---

Fly API keys are bearer tokens that identify your dashboard account. Every API
request must include one in the `Authorization` header:

```http
Authorization: Bearer <your-api-key>
```

## What an API key is

A Fly API key is a JWT signed by the Fly dashboard. It encodes your account
email and the human-readable name you gave the key when you created it. You do
not need to inspect or decode the token — just send it as a bearer token.

A key grants read access to **only the surveys and responses that belong to your
account**. It cannot access other users' data.

## Create an API key

API keys are created from the Fly dashboard.

1. Sign in at [https://fly.vlab.digital](https://fly.vlab.digital).
2. Open **Connect → API Keys**.
3. Click **Create** and give the key a name (for example `nightly-export`).
4. Copy the token that appears.

::: warning

The token is shown **only once**. Store it somewhere safe — a secrets manager,
environment variable, or `.env` file that is not committed to version control.
Anyone with the token can download your survey data.
:::

Key names must be unique per account. If you reuse a name, the dashboard will
refuse with *"there is already an API Key with that name"*.

## Use the key

Send the token as a bearer token on every request. For example, to list your
surveys:

```bash
curl https://fly-dashboard-api.vlab.digital/api/v1/surveys \
  -H "Authorization: Bearer $FLY_API_KEY"
```

In Python:

```python
import os
import requests

BASE = "https://fly-dashboard-api.vlab.digital/api/v1"
headers = {"Authorization": f"Bearer {os.environ['FLY_API_KEY']}"}

r = requests.get(f"{BASE}/surveys", headers=headers)
r.raise_for_status()
print(r.json())
```

## Errors

| Status | Meaning |
|---|---|
| `401` | Missing, malformed, or invalid token. Response body: `{"error":{"message":"Invalid Token."}}` |

If you receive `401`, check that the `Authorization` header is present, starts
with `Bearer `, and contains the full token copied from the dashboard.

## Keeping your key safe

- Store the key in an environment variable (`FLY_API_KEY`) rather than
  hard-coding it into scripts.
- Do not commit the key to git or share it in chat.
- Use a distinct, named key per integration (for example `vlab-connector`,
  `analytics-notebook`) so you can tell them apart.
