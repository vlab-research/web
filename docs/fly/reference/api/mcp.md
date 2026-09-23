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

See [Authentication](/docs/fly/reference/api/authentication/) to create a key. A
key scoped `surveys:read` can connect and list; every write tool below needs
`surveys:write`.

## The five tools

| Tool | Does |
|---|---|
| `list_surveys` | Reads back every study, form and version — call this first, since the other tools need exact names and ids from it |
| `create_typeform_form` | Authors a survey's questions, including branching logic, validation, piping and video — see below |
| `create_survey` | Registers a Typeform form with Fly under a study name |
| `create_survey_version` | Publishes an edited form as a new version of an existing study |
| `update_survey_settings` | Changes timeouts and the delayed-follow-up settings on a version |

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
