---
title: MCP
weight: 1
---

Virtual Lab exposes the same operations the `vlab` CLI and the study configuration
API use as a **Model Context Protocol** server, so an agent — Claude Code, Codex,
Open Code, or any other MCP client — can create a study, edit its configuration,
run whole-study validation, and step through the plan/apply optimisation loop by
calling tools directly, instead of you writing the requests yourself.

There is no new capability here beyond the CLI and the HTTP API: every tool calls
the same route the matching `vlab` command calls, so the same rules apply —
`study_confs` is append-only, writing a section replaces it whole, and
`apply_instruction` is the one call that spends money on Meta.

## Two ways to connect

| | Local — `vlab mcp` | Remote — `POST /mcp` |
|---|---|---|
| Runs | on your own machine, started by your MCP client | on Virtual Lab's servers |
| Needs | Python 3.10+ and the `vlab` SDK installed (`pip install "adopt[sdk]"` from the repository) | nothing but an HTTP client |
| Your API key | stays on your machine | sent as a bearer token on every call |

Prefer `vlab mcp` if you can install it — the key never leaves your machine, and
every tool goes through the same routes as the CLI against any deployment.
`POST /mcp` exists for a client that cannot install anything.

### Claude Code, with `vlab mcp`

```
claude mcp add vlab -e VLAB_API_KEY=$VLAB_API_KEY -- vlab mcp
```

### Claude Desktop, or any client that launches a local server

```json
{
  "mcpServers": {
    "vlab": {
      "command": "/absolute/path/to/vlab",
      "args": ["mcp"],
      "env": {
        "VLAB_API_KEY": "your-api-key"
      }
    }
  }
}
```

Use the absolute path from `which vlab` for `command` — Claude Desktop launches
the server without a login shell, so a bare `"vlab"` may not be found on `PATH`.

### Or, without installing anything

```
claude mcp add --transport http vlab https://vlab-study-conf-api.toixo.vlab.digital/mcp \
  --header "Authorization: Bearer $VLAB_API_KEY"
```

## Getting a key

From the Virtual Lab dashboard, open **Connected Accounts**, click **Add
Connected Account**, and choose **API Key** as the account type. The token is
shown once — copy it somewhere safe before closing the dialog. The same page
lists and revokes keys you have already created.

A key can be scoped to only what the agent needs. For a study-authoring agent
that should not spend money, a reasonable set is `studies:write`, `meta:read`
and `optimize:read` — it can build, check and plan a study, and cannot launch
an ad. Add `optimize:write` only when you mean to let the agent apply changes
on Meta.

## The tools

Tool names match the CLI command they call, so a run through them reads the
same way as the [tutorials](/docs/vlab/tutorials/): `create_study` →
`push_study` → `validate_study` → `plan_study` → `apply_instruction`.

| Tool | Equivalent to |  |
|---|---|---|
| `create_study` | `vlab create` | creates a study |
| `pull_study` | `vlab pull` | reads a study's configuration |
| `validate_study` | `vlab validate` | checks configuration sections against each other |
| `diff_study` | `vlab diff` | shows what a write would change |
| `push_study` | `vlab push` | writes a configuration section |
| `compile_strata` | `vlab strata generate` | builds strata from your variables |
| `extract_targeting` | `vlab strata extract-targeting` | reads targeting off a template ad set |
| `plan_study` | `vlab plan` | previews the next optimisation step |
| `apply_instruction` | `vlab apply` | applies one optimisation instruction on Meta |
| `meta_credentials`, `meta_adaccounts`, `meta_campaigns`, `meta_adsets`, `meta_ads` | `vlab meta …` | read-only lookups against your connected Meta account |
| `list_api_keys`, `revoke_api_key` | `vlab keys …` | manage your own API keys |

Every [study configuration section](/docs/vlab/study-configuration/) — including
strata, the piece that programs how the recruitment budget moves between the
groups you're targeting — is written the same way an agent would write any
other: read it back with `pull_study`, change it, check it with `validate_study`,
then `push_study`.
