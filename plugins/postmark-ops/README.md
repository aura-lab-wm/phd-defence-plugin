# postmark-ops — Claude Code plugin

> **This file is human documentation, not skill instructions.** Claude only loads
> `postmark-ops/skills/postmark-ops/SKILL.md` when the skill runs. Edit that file to change behaviour.

Part of the `aura-se-lab-skills` marketplace (`aura-lab-wm/phd-defence-plugin`).

## What it does
End-to-end Postmark email operations:

- **Fetch the Server API token from your logged-in Chrome session** (via the `session-fetcher` skill) —
  no hand-pasting tokens into chat. Includes the exact token-extraction recipe and the Forethought
  `data-api-key` decoy warning.
- **Validate** the token and **send** a deliverability "proof" email (multipart, tracking off, RFC 8058
  one-click List-Unsubscribe) to prove `DKIM=pass` / `SPF=pass` from a sending domain.
- **Publish DKIM + Return-Path DNS** at *any* registrar / DNS provider (Cloudflare, Namecheap, Route 53,
  GoDaddy, Google/Squarespace, registrar DNS…), plus pointing a domain's apex+www at a host.

## What's inside
- `skills/postmark-ops/SKILL.md` — the skill (auto-invoked on Postmark/deliverability requests).
- `skills/postmark-ops/references/` — the runbooks: token fetch, proof send, DNS (any-provider +
  Cloudflare examples), point-domain-at-host.
- `agents/postmark-ops.md`, `agents/cloudflare-ops.md` — the two ops agents (dispatch via the Agent tool).

## Install (for coworkers)
```
/plugin marketplace add aura-lab-wm/phd-defence-plugin
/plugin install postmark-ops@aura-se-lab-skills
```
(The repo is private to the `aura-lab-wm` org — coworkers need org access + a GitHub login.)

## Requirements
- macOS + the `session-fetcher` skill (reads Chrome's cookie DB) for the token-fetch path.
- Python `requests` + `cryptography` (usually already present).
- Provider proven on `mastropaolo.dev` (2026-05-29): live send returned `ErrorCode 0`, DKIM-signed.
