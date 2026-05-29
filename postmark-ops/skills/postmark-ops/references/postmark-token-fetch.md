# Runbook — fetch a Postmark Server API token from the logged-in Chrome session

**Authored:** 2026-05-29 · **Proven working** (sent MessageID `6db4379e-3741-497d-869b-d0a533a7fddd`).
**Goal:** obtain a Postmark **Server API token** with zero hand-pasting, by harvesting the operator's
already-authenticated `account.postmarkapp.com` session out of Chrome. Feeds `postmark-send-demo.md`.

Codified as the `postmark-ops` agent (`~/.claude/agents/postmark-ops.md`). Pairs with the DKIM/Return-Path
DNS runbooks (`postmark-dns-*.md`). Secret hygiene: mask the token in all output, write it only to a
`0600` file, never echo/commit it, delete the temp file when done.

## 1. Harvest the session (session-fetcher skill)
```bash
SF=~/.local/bin/session_fetcher     # → ~/.claude/skills/session-fetcher/scripts/session_fetcher.py
$SF register postmark --from-url 'https://account.postmarkapp.com/'   # one-time
$SF refresh postmark                                                  # reads Chrome cookie DB (Chrome may be closed)
```
- `requests` + `cryptography` are already present system-wide (skip `pip`; PEP-668 blocks `--user` here).
- The `/` probe returning **HTTP 400** is AWS-WAF / missing-User-Agent noise — **not** an auth failure.
  Presence of `user_credentials` + `_postmark_session` cookies = logged in.
- Use a real browser `User-Agent` on every request or the WAF returns 400.

## 2. List servers, then extract the RIGHT token (Python)
```python
import sys, pathlib, re; sys.path.insert(0, str(pathlib.Path.home()/".claude/skills/session-fetcher/scripts"))
import session_fetcher, requests
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 … Chrome/124.0 Safari/537.36"
for k,v in session_fetcher.load("postmark").items(): S.cookies.set(k,v)

ids = sorted(set(re.findall(r'/servers/(\d+)',
        S.get("https://account.postmarkapp.com/servers", timeout=20).text)))
for sid in ids:
    html = S.get(f"https://account.postmarkapp.com/servers/{sid}/credentials", timeout=20).text
    m = re.search(r'/account/api_tokens/([0-9a-f-]{36})/confirm_destroy\?server_id='+sid, html) \
        or re.search(r'js-token-list.*?<input value="([0-9a-f-]{36})"', html, re.S)
    token = m.group(1)   # ← the Server API token for server <sid>
```
**The token is tied to its server by the delete link** `…/api_tokens/<UUID>/confirm_destroy?server_id=<SID>`
(or the `<input value>` inside `js-token-list`/`js-token`).

⚠️ **Decoy:** the page also has `data-api-key="<uuid>"` — that's the **Forethought** support-chat widget
key, identical on every server. It is NOT the Postmark token. Never "grab the first UUID."

## 3. Validate (proves the token is live + which server)
```python
r = requests.get("https://api.postmarkapp.com/server",
      headers={"X-Postmark-Server-Token": token, "Accept":"application/json"})  # 200 → {"Name","ID","Color"}
```

## 4. Hand off
Pass `token` straight into the send in [`postmark-send-demo.md`](./postmark-send-demo.md) (don't write it to
chat). Optional: persist for the in-app route with
`fly secrets set POSTMARK_SERVER_TOKEN="$token" DEMO_FROM_EMAIL="demo@mastropaolo.dev" --app provenance-toe`.

## This workspace (2026-05-29)
- Servers: `19305833` "My First Server", `19305836` "new" (proof send used "new").
- Sending domain `mastropaolo.dev` returned `ErrorCode 0` on a live send → **Verified + DKIM-signed**.
