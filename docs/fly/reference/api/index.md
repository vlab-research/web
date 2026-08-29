---
title: API
weight: 85
---

The Fly dashboard exposes a REST API that lets you programmatically download
survey response data from your own scripts and notebooks. It is the same API
the [Vlab platform](/docs/vlab/connected-accounts/fly/) uses when you
connect a Fly account to pull responses into a study.

This section covers how to authenticate and how to retrieve responses. All
endpoints are served from the dashboard API:

| Environment | Base URL |
|---|---|
| Production | `https://fly-dashboard-api.vlab.digital/api/v1` |
| Staging | `https://staging.fly-dashboard-api.vlab.digital/api/v1` |

Every request must carry a Fly API key in the `Authorization` header. See
[Authentication](/docs/fly/reference/api/authentication/) to create
one, then use [List surveys](/docs/fly/reference/api/surveys/) to find
the `survey_name` you need, and finally
[Get responses](/docs/fly/reference/api/responses/) to pull the data.
