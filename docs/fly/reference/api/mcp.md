---
title: MCP
weight: 4
---

`POST /api/v1/mcp` exposes survey authoring and monitoring as a **Model Context
Protocol** server, so an agent — Claude Code, Codex, Open Code, or any other MCP
client — can create and edit a survey by calling tools directly, instead of you
writing the requests in [Creating a survey](/docs/fly/reference/creating-a-survey/)
by hand.

It is the same account and the same operations as the REST API above: one bearer
token, the same rows, no separate credential.

## Connecting

The server is remote only — there is no local process to install. It is
**stateless streamable HTTP**: one request per call, no session to keep open.

Claude Code:

```
claude mcp add --transport http fly https://fly-dashboard-api.vlab.digital/api/v1/mcp \
  --header "Authorization: Bearer $FLY_API_KEY"
```

Any client that reads a `.mcp.json` (or Claude Desktop's config) in JSON form:

```json
{
  "mcpServers": {
    "fly": {
      "type": "http",
      "url": "https://fly-dashboard-api.vlab.digital/api/v1/mcp",
      "headers": {
        "Authorization": "Bearer ${FLY_API_KEY}"
      }
    }
  }
}
```

Codex, in `~/.codex/config.toml`, with `FLY_API_KEY` exported in the shell
that starts Codex:

```toml
[mcp_servers.fly]
url = "https://fly-dashboard-api.vlab.digital/api/v1/mcp"
bearer_token_env_var = "FLY_API_KEY"
```

See [Authentication](/docs/fly/reference/api/authentication/) to create a key —
in the Fly dashboard under **Connect → API Keys**. There is no separate "MCP"
setting anywhere in the dashboard: the API key is the whole of the setup.

To drive recruitment as well as surveys, connect the
[Virtual Lab MCP server](/docs/vlab/reference/mcp/) alongside this one; it takes
its own key, from the Virtual Lab dashboard. [Connecting an agent](/docs/agents/)
walks through both together.

## The tools

Each tool needs the scope of the area it belongs to, and a write scope implies
read on the same area. A key with no scopes can call everything; a missing scope
comes back as a tool error naming it.

**Surveys** — `surveys:read` / `surveys:write`

| Tool | Does |
|---|---|
| `list_surveys` | Reads back every study, form and version — call this first, since the other tools need exact names and ids from it |
| `list_typeform_forms` | Lists the forms in your connected Typeform account, to find the `formid` `create_survey` takes |
| `create_typeform_form` | Authors a survey's questions, including branching logic, validation, piping and video — see below |
| `create_survey` | Registers a Typeform form with Fly under a study name |
| `create_survey_version` | Publishes an edited form as a new version of an existing study |
| `update_survey_settings` | Changes timeouts and the delayed-follow-up settings on a version |

**Monitoring** — `surveys:read`, plus `platform:read` for notices

| Tool | Does |
|---|---|
| `get_states_summary` | Counts of participants in each state for a survey — start here |
| `list_states` | Who is in a given state or error, 200 rows at a time |
| `get_participant_state` | One participant's full context |
| `get_survey_health` | The same 24-hour findings as the dashboard's Monitor tab |
| `get_platform_notices` | Problems on Fly's side that affect every survey — a messaging channel down, provider errors |

**Data** — `exports:*` and `responses:read`

| Tool | Does |
|---|---|
| `start_export` | Starts an asynchronous export of a survey's data |
| `list_exports` | Export status, and a download link once it has finished |
| `get_responses` | Pages through answers for a look; use an export for bulk |

**Messages and media** — `templates:*` and `media:*`

| Tool | Does |
|---|---|
| `list_message_templates`, `get_message_template` | Reads your WhatsApp message templates and their approval status |
| `create_message_template`, `delete_message_template` | Submits a template to Meta for approval, or removes one |
| `list_media`, `upload_media` | Media to reference from questions, each with a permanent public URL |

**Bails** — `users:read` / `users:write`. See [Bails](/docs/fly/reference/bails/).

| Tool | Does |
|---|---|
| `preview_bail` | Counts who a bail would move, before anything is created — always run it first |
| `create_bail`, `update_bail`, `delete_bail` | Manages a bail |
| `list_bails`, `get_bail` | Reads your bails |
| `list_bail_events` | The audit trail of who was actually moved |

**Accounts** — `credentials:read`

| Tool | Does |
|---|---|
| `list_messaging_accounts` | Your connected Messenger pages and WhatsApp numbers, with the `account_id` the template tools take |
| `get_whatsapp_health` | A WhatsApp number's quality rating and sending status, read live from Meta |

No tool creates or revokes an API key or a connected account: those stay in the
dashboard.

## Programming a survey's logic through `create_typeform_form`

This is the one tool with no REST equivalent — it authors the form in your own
Typeform account and hands back a `formid` for `create_survey` to register.
Each field is `{type, ref, title, description?, choices?, properties?,
validations?}`, and **`description` is where a survey's logic is actually
written**: conditional branching, piping earlier answers into later questions,
validation rules, video, and incentive triggers are all authored as the YAML
vocabulary documented in full in [Questions](/docs/fly/reference/questions/).
Two conveniences the tool adds on top of Typeform:

- `choices: ["Yes", "No"]` renders as lettered options (`A`/`B`, …) — the way a
  respondent typing in a chat window answers, rather than typing out a whole
  phrase. Up to 13; pass `properties.choices` yourself to opt out.
- A hidden field named `seed_N` is how a survey randomises respondents into
  arms.

An agent can therefore write a study's entire questionnaire — the ordinary
question types, the branches, the piped values, the arm randomisation — as tool
calls, the same instrument a researcher would otherwise build by hand in
Typeform.

## Failure

A missing scope, a bad argument, or a name that does not resolve comes back as
a normal tool result naming the problem, not an HTTP error — read the result
rather than retrying blind.
