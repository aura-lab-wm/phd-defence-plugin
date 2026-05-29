# Runbook — point a domain (+ www) at a host, at ANY registrar / DNS provider

**Authored:** 2026-05-29 · Provider- and host-agnostic generalization of `cloudflare-dns-to-fly.md`.
**Goal:** make `<domain>` and `www.<domain>` serve a deployed app on some host (Fly.io, Vercel, Render,
Railway, a raw origin IP), get the host's TLS cert to validate, then optionally retire the host's default
`*.fly.dev` / `*.vercel.app` URL.

## Step 1 — find where DNS lives (don't assume Cloudflare)
```bash
dig +short NS <domain>
```
| Nameserver pattern | Provider | DNS UI |
|---|---|---|
| `*.ns.cloudflare.com` | Cloudflare | dash.cloudflare.com → zone → DNS → Records |
| `*.registrar-servers.com` | Namecheap | Domain List → Manage → Advanced DNS |
| `ns-*.awsdns-*` | AWS Route 53 | Route 53 → Hosted zones |
| `ns*.domaincontrol.com` | GoDaddy | Domains → DNS |
| `ns*.googledomains.com` / `*.squarespace.com` | Google / Squarespace | Domains → DNS |
| registrar's own NS | the registrar | registrar control panel → DNS |
Log into the provider that actually holds the zone. Can't act there → STOP and report.

## Step 2 — get the host's target records
Ask the host what apex + www should point to:
- **Fly.io:** `fly ips list -a <app>` → an `A` (often shared anycast `66.241.124.66`) + an `AAAA`
  (`2a09:8280:1::…`). Create certs first: `fly certs add <domain> -a <app>` and `fly certs add www.<domain> -a <app>`.
- **Vercel:** add the domain in the project; Vercel gives apex `A 76.76.21.21` (or an ALIAS/ANAME) and
  `www → cname.vercel-dns.com`.
- **Render / Railway / other PaaS:** the dashboard shows a CNAME target (e.g. `*.onrender.com`,
  `*.up.railway.app`) — use ANAME/ALIAS or a CNAME at apex if the provider supports it; else the given A.
- **Raw origin:** the server's public `A` (and `AAAA` if it has one).

## Step 3 — set the records (end state)
Apex (`@`) usually needs `A`/`AAAA` (most DNS can't CNAME the apex; Cloudflare/Route 53/others offer
CNAME-flattening/ALIAS/ANAME — use it if the host gives a hostname instead of an IP).

| Type | Name | Value | Proxy / mode |
|---|---|---|---|
| A | `@` (apex) | host IPv4 | **DNS-only** if the host terminates its own TLS |
| AAAA | `@` (apex) | host IPv6 (if any) | DNS-only |
| A or CNAME | `www` | host IPv4, or host's CNAME target | DNS-only |
| AAAA | `www` | host IPv6 (if any) | DNS-only |

**TLS / proxy rule:** hosts that terminate their own TLS (Fly, Vercel, Render, Railway, raw origin)
need the record **unproxied**:
- **Cloudflare:** set the cloud **grey ("DNS only", `proxied=false`)**. Orange/proxied breaks the host's
  ACME validation unless you also set Cloudflare SSL = **Full (strict)** — simplest is grey cloud.
- **Other providers:** plain records, no CDN/proxy layer — nothing to toggle.

**Replace, don't stack:** parked/registrar landing pages often leave **two** apex `A` records. Find ALL
existing apex `A`/`AAAA` and replace/delete each so only the host's values remain. Be idempotent (upsert).

**Do NOT touch** `MX`, email `TXT` (SPF/DKIM/DMARC), or email `CNAME`s — only the apex + `www` web records.

### Cloudflare API recipe (only if the zone is on Cloudflare)
```bash
TOKEN='<CF_TOKEN_with_Zone:DNS:Edit>'; ZONE='<domain>'
ZID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=$ZONE" | jq -r '.result[0].id')
upsert(){ # $1=type $2=name $3=content  (DNS-only)
  local id body
  id=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/$ZID/dns_records?type=$1&name=$2" | jq -r '.result[0].id // empty')
  body="{\"type\":\"$1\",\"name\":\"$2\",\"content\":\"$3\",\"ttl\":300,\"proxied\":false}"
  if [ -n "$id" ]; then curl -s -X PUT  -H "Authorization: Bearer $TOKEN" -H 'content-type: application/json' \
        "https://api.cloudflare.com/client/v4/zones/$ZID/dns_records/$id" -d "$body" | jq '.success';
  else            curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'content-type: application/json' \
        "https://api.cloudflare.com/client/v4/zones/$ZID/dns_records"     -d "$body" | jq '.success'; fi; }
```
For other providers, use their API (Route 53 `change-resource-record-sets`, Namecheap API, etc.) or the
dashboard — the *values* above are identical; only the call differs.

## Step 4 — verify DNS + cert
```bash
dig +short A    <domain>          # expect the host IPv4
dig +short AAAA <domain>          # expect the host IPv6 (if any)
dig +short A    www.<domain>
# Fly: fly certs check <domain> -a <app>  → Status = Issued / Verified
curl -sI https://<domain>/<healthpath>    # expect 200 (or the app's expected code)
```
Propagation + cert issuance can take a few minutes; one edge node may briefly serve stale records.

## Step 5 — (optional) retire the host's default URL
If the app honors a canonical-host redirect (this project: `CANONICAL_HOST` env → middleware 308):
```bash
fly secrets set CANONICAL_HOST=<domain> --app <app>     # Fly example
curl -sI https://<app>.fly.dev/   # expect 308 → https://<domain>/
```

## Done when
`dig` shows the host's IPs for apex + www, the host's TLS cert is Verified/Issued,
`https://<domain>/<healthpath>` → 200, and (if configured) the default URL 308-redirects to `<domain>`.
