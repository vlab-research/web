---
title: List surveys
weight: 2
---

The response endpoints take a `survey` parameter, which is the **`survey_name`**
of a survey in your account. If you are not sure what your survey is called, list
your surveys first.

## `GET /surveys`

Returns every survey that belongs to your account, newest first. No query
parameters.

### Request

```bash
curl https://fly-dashboard-api.vlab.digital/api/v1/surveys \
  -H "Authorization: Bearer $FLY_API_KEY"
```

```python
import os
import requests

BASE = "https://fly-dashboard-api.vlab.digital/api/v1"
headers = {"Authorization": f"Bearer {os.environ['FLY_API_KEY']}"}

r = requests.get(f"{BASE}/surveys", headers=headers)
r.raise_for_status()
surveys = r.json()
for s in surveys:
    print(s["survey_name"], s["shortcode"], s["id"])
```

### Response

```json
[
  {
    "id": "00000000-0000-0000-0000-000000000000",
    "survey_name": "baseline_survey",
    "shortcode": "231",
    "title": "Baseline Survey",
    "formid": "biy23",
    "created": "2024-05-01T10:00:00.000Z",
    "metadata": {},
    "translation_conf": {},
    "off_time": null,
    "timeouts": null
  }
]
```

### Field reference

| Field | Description |
|---|---|
| `id` | Unique survey ID. |
| `survey_name` | The name you pass to the response endpoints as `survey`. A survey is a collection of [forms](/docs/fly/core-concepts/). |
| `shortcode` | Shortcode identifying one form within the survey. |
| `title` | Human-readable survey title. |
| `formid` | The underlying Typeform form ID. |
| `created` | ISO 8601 creation timestamp. |
| `metadata` | Survey metadata object. |
| `translation_conf` | Translation configuration object. |
| `off_time` | Time the survey was turned off, if any. |
| `timeouts` | Per-survey timeout settings, if any. |

Pick the `survey_name` you want and pass it to
[Get responses](/docs/fly/reference/api/responses/).
