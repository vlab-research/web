---
title: Get responses
weight: 3
---

Use the `/responses` endpoints to download survey response data. There are three
of them:

| Endpoint | Format | Use when |
|---|---|---|
| `GET /responses` | JSON, paginated | You want to stream responses into a script or notebook and control paging. |
| `GET /responses/csv` | CSV download | You want the full dataset as a single CSV file. |
| `GET /responses/form-data` | CSV download | You want the form/version metadata for a survey. |

All three require a `survey` query parameter set to the `survey_name` from
[List surveys](/docs/fly/reference/api/surveys/), and all are scoped to
your account — you will only ever receive your own data.

## `GET /responses`

Returns responses as a paginated JSON array.

### Query parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `survey` | yes | — | The `survey_name` of the survey to fetch. |
| `after` | no | — | A cursor token from the last row of the previous page. Omit on the first request. |
| `pageSize` | no | `25` | Maximum number of rows to return per page. |

### Response

```json
{
  "responses": [
    {
      "parent_surveyid": "00000000-0000-0000-0000-000000000000",
      "parent_shortcode": "231",
      "shortcode": "231",
      "surveyid": "00000000-0000-0000-0000-000000000000",
      "flowid": "100001",
      "userid": "127",
      "question_ref": "ref",
      "question_idx": "10",
      "question_text": "text",
      "response": "last",
      "timestamp": "2022-06-06T09:58:00.000Z",
      "metadata": null,
      "pageid": null,
      "translated_response": null,
      "token": "MjAyMi0wNi0wNiAwOTo1ODowMCsxNjQsMTI3LHJlZg=="
    }
  ]
}
```

### Field reference

| Field | Description |
|---|---|
| `parent_surveyid` | ID of the parent survey (for stitched form chains). |
| `parent_shortcode` | Shortcode of the parent form. |
| `shortcode` | Shortcode of the form that produced this response. |
| `surveyid` | ID of the form that produced this response. |
| `flowid` | ID of the conversation flow this response belongs to. |
| `userid` | The participant identifier — a Facebook page-scoped id on Messenger, a phone number on WhatsApp. |
| `question_ref` | Reference of the question that was answered. |
| `question_idx` | Index of the question within the form. |
| `question_text` | The text of the question. |
| `response` | The participant's raw answer. |
| `timestamp` | ISO 8601 timestamp of the response. |
| `metadata` | The hidden fields the participant carries — everything their recruitment reference brought, plus `platform`, `pageid`, `seed` and, where applicable, `ad_id` and `vt`. See [Hidden Fields](/docs/fly/reference/hidden/#what-a-respondent-arrives-with). |
| `pageid` | The messaging account involved, if applicable — a Facebook Page ID on Messenger, or the WhatsApp number's account id on WhatsApp. |
| `translated_response` | The response translated into the survey's core language, if a translation config is set. |
| `token` | **Cursor.** Pass this as `after` to fetch the next page. |

### Pagination

Responses are ordered by `(timestamp, userid, question_ref)`. Each row carries a
`token` cursor. To fetch the next page, take the `token` from the **last row** of
the current page and pass it as the `after` query parameter on the next request.
When the `responses` array comes back empty, you have reached the end.

### Examples

```bash
# First page
curl "https://fly-dashboard-api.vlab.digital/api/v1/responses?survey=baseline_survey&pageSize=100" \
  -H "Authorization: Bearer $FLY_API_KEY"

# Next page — use the token from the last row of the previous response
curl "https://fly-dashboard-api.vlab.digital/api/v1/responses?survey=baseline_survey&pageSize=100&after=$AFTER_TOKEN" \
  -H "Authorization: Bearer $FLY_API_KEY"
```

This Python example walks every page and collects all responses into a list:

```python
import os
import requests

BASE = "https://fly-dashboard-api.vlab.digital/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['FLY_API_KEY']}"}
SURVEY = "baseline_survey"

all_rows = []
after = None

while True:
    params = {"survey": SURVEY, "pageSize": 100}
    if after:
        params["after"] = after

    r = requests.get(f"{BASE}/responses", headers=HEADERS, params=params)
    r.raise_for_status()
    rows = r.json()["responses"]

    if not rows:
        break

    all_rows.extend(rows)
    after = rows[-1]["token"]

print(f"Fetched {len(all_rows)} responses")
```

## `GET /responses/csv`

Streams every response for the survey as a single CSV file. The response sets
`Content-Type: text/csv` and a `Content-Disposition` attachment header, so a
browser or `curl -O` will save it as `responses_<timestamp>.csv`.

### Query parameters

| Parameter | Required | Description |
|---|---|---|
| `survey` | yes | The `survey_name` of the survey, URL-encoded. |

### Examples

```bash
curl -O -J \
  "https://fly-dashboard-api.vlab.digital/api/v1/responses/csv?survey=baseline_survey" \
  -H "Authorization: Bearer $FLY_API_KEY"
```

```python
import os
import requests

BASE = "https://fly-dashboard-api.vlab.digital/api/v1"
headers = {"Authorization": f"Bearer {os.environ['FLY_API_KEY']}"}

with requests.get(
    f"{BASE}/responses/csv",
    headers=headers,
    params={"survey": "baseline_survey"},
    stream=True,
) as r:
    r.raise_for_status()
    with open("responses.csv", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
```

If your `survey_name` contains spaces or special characters, URL-encode it (the
Python `requests` example does this automatically via `params`).

## `GET /responses/form-data`

Downloads form metadata for a survey as CSV — one row per form version, with a
`version` number that orders the versions of each shortcode by creation time.
Useful when a shortcode has been republished multiple times and you need to tell
versions apart in analysis.

### Query parameters

| Parameter | Required | Description |
|---|---|---|
| `survey` | yes | The `survey_name` of the survey, URL-encoded. |

### CSV columns

| Column | Description |
|---|---|
| `surveyid` | Form ID. |
| `shortcode` | Shortcode of the form. |
| `survey_name` | The survey name. |
| `version` | 1-based version number of this shortcode, ordered by creation time. |
| `survey_created` | ISO 8601 creation timestamp of this form version. |
| `metadata` | Form metadata. |

### Example

```bash
curl -O -J \
  "https://fly-dashboard-api.vlab.digital/api/v1/responses/form-data?survey=baseline_survey" \
  -H "Authorization: Bearer $FLY_API_KEY"
```

## Errors

| Status | When | Body |
|---|---|---|
| `400` | The `survey` parameter is missing. | `{"error":{"message":"No user, no responses!"}}` |
| `401` | Missing or invalid API key. | `{"error":{"message":"Invalid Token."}}` |
| `500` | The `survey_name` does not exist under your account, or the survey has no responses yet. | `{"error":{"message":"No responses were found for survey: <name> for user: <email>"}}` |

::: note

A survey that has not collected any responses yet returns a `500` with a "No
responses were found" message rather than an empty list. Double-check the
`survey_name` against the output of
[List surveys](/docs/fly/reference/api/surveys/) if you see this.
:::
