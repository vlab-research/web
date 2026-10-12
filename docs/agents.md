---
title: "Connecting an Agent"
weight: 3
---

An AI agent — Claude Code, Codex, Open Code, or any other client that speaks the
**Model Context Protocol** (MCP) — can run a study end to end: build the
recruitment campaign, author and publish the survey, and watch both while they
run. This page connects one.

There is no "MCP" button in either dashboard. Connecting an agent is two API
keys and a few lines of configuration.

## Two servers, two keys

Virtual Lab and Fly are separate services, and each has its own MCP server and
its own key. Connect both to run a whole study; connect one if you only use one
of the tools.

| | Virtual Lab — recruitment | Fly — surveys |
|---|---|---|
| Does | studies, ads, strata, the optimisation loop | survey authoring, versions, participants, responses, messages |
| Server | `https://vlab-study-conf-api.toixo.vlab.digital/mcp` | `https://fly-dashboard-api.vlab.digital/api/v1/mcp` |
| Key from | Virtual Lab dashboard: **Connected Accounts → Add Connected Account → API Key** | Fly dashboard ([fly.vlab.digital](https://fly.vlab.digital)): **Connect → API Keys → Create** |
| Environment variable used below | `VLAB_API_KEY` | `FLY_API_KEY` |
| Full reference | [Virtual Lab MCP](/docs/vlab/reference/mcp/) | [Fly MCP](/docs/fly/reference/api/mcp/) |

::: warning

Each key is shown **only once**, when you create it. Copy it somewhere safe — a
password manager, or a `.env` file that is not committed to version control.
Anyone holding a key can act as you. A lost key cannot be recovered; create a
new one and revoke the old.
:::

Put both keys in your shell before starting the agent:

```
export VLAB_API_KEY="<your Virtual Lab key>"
export FLY_API_KEY="<your Fly key>"
```

## Claude Code

```
claude mcp add --transport http vlab https://vlab-study-conf-api.toixo.vlab.digital/mcp \
  --header "Authorization: Bearer $VLAB_API_KEY"

claude mcp add --transport http fly https://fly-dashboard-api.vlab.digital/api/v1/mcp \
  --header "Authorization: Bearer $FLY_API_KEY"
```

## Codex

In `~/.codex/config.toml`:

```toml
[mcp_servers.vlab]
url = "https://vlab-study-conf-api.toixo.vlab.digital/mcp"
bearer_token_env_var = "VLAB_API_KEY"

[mcp_servers.fly]
url = "https://fly-dashboard-api.vlab.digital/api/v1/mcp"
bearer_token_env_var = "FLY_API_KEY"
```

## Open Code

In `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "vlab": {
      "type": "remote",
      "url": "https://vlab-study-conf-api.toixo.vlab.digital/mcp",
      "headers": { "Authorization": "Bearer {env:VLAB_API_KEY}" }
    },
    "fly": {
      "type": "remote",
      "url": "https://fly-dashboard-api.vlab.digital/api/v1/mcp",
      "headers": { "Authorization": "Bearer {env:FLY_API_KEY}" }
    }
  }
}
```

Any other client takes the same two things per server: the URL, and an
`Authorization: Bearer <key>` header. Both servers are stateless streamable HTTP
with no OAuth step. The Virtual Lab server can also run on your own machine
instead, so its key never leaves it — see
[Virtual Lab MCP](/docs/vlab/reference/mcp/).

## Check it worked

Start the agent and ask:

> List my Virtual Lab organisations and studies, and list my Fly surveys.

In Claude Code, `/mcp` also shows both servers as connected. An authentication
error almost always means the key was not exported in the shell that started the
agent, or was copied incompletely.

## Before you let it spend money

On Virtual Lab, one call reaches the outside world: **`apply_instruction`**
changes your live campaigns on Meta and spends your ad budget. Reading,
validating, diffing and planning a study are all safe. Tell the agent to show you the plan and wait for
your approval before applying, or create the Virtual Lab key with scopes that
cannot apply at all — see [Getting a key](/docs/vlab/reference/mcp/#getting-a-key).

On Fly, published survey versions reach every new participant from the moment
they are created, and an enabled bail keeps moving participants until it is
turned off. Ask the agent to run `preview_bail` before creating one.
