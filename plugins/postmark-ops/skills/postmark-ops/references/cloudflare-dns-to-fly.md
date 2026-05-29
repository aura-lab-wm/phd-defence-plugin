# Runbook — Point mastropaolo.dev (+ www) at the Fly app `provenance-toe`

**For:** an agent with Cloudflare access to the `mastropaolo.dev` zone (dashboard, or an
API token scoped `Zone:DNS:Edit` + `Zone:Read`).
**Goal:** make `mastropaolo.dev` and `www.mastropaolo.dev` serve the deployed Fly app, get
the Fly TLS cert to validate, then signal back so the coordinator retires the `*.fly.dev` URL.

## Facts (do not re-derive)
- Fly app: `provenance-toe` (region `sin`). Default URL today: `https://provenance-toe.fly.dev`.
- Zone `mastropaolo.dev` is on **Cloudflare** (NS: `may.ns.cloudflare.com`, `tate.ns.cloudflare.com`).
- **Current (wrong) apex records** point at Cloudflare proxy/parked IPs: `A 104.21.47.145`, `A 172.67.148.114`, plus matching AAAA. These must be **replaced**.
- **Fly target IPs** (certs already created for both hostnames):
  - `A    → 66.241.124.66`
  - `AAAA → 2a09:8280:1::11c:a050:0`
- Fly terminates TLS itself, so these records must be **DNS-only (grey cloud / `proxied=false`)**. Proxied/orange-cloud breaks Fly's ACME validation unless you also flip Cloudflare SSL to Full(strict) — **just use DNS-only.**

## Do NOT touch
- Any `MX`, `TXT` (SPF/DKIM/DMARC), email `CNAME`, or other subdomain records. **Only** change the apex `A`/`AAAA` and the `www` `A`/`AAAA`. (Email on this domain flows through Cloudflare — leave it intact.)

## Steps

### A. Set the records — end state (4 records, all DNS-only / not proxied)
| Type | Name | Value | Proxy |
|---|---|---|---|
| A | `mastropaolo.dev` (`@`) | `66.241.124.66` | DNS only |
| AAAA | `mastropaolo.dev` (`@`) | `2a09:8280:1::11c:a050:0` | DNS only |
| A | `www` | `66.241.124.66` | DNS only |
| AAAA | `www` | `2a09:8280:1::11c:a050:0` | DNS only |

**Dashboard:** Cloudflare → `mastropaolo.dev` → DNS → Records → replace the apex `A` records (104.21.x / 172.67.x) and apex `AAAA` with the Fly values (set the cloud icon to **grey / DNS-only**), then add the two `www` records.

**API** (token with `Zone:DNS:Edit`):
```bash
TOKEN='<CF_TOKEN>'
ZID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=mastropaolo.dev" | jq -r '.result[0].id')

upsert() { # $1=type $2=name $3=content  — DNS-only upsert
  local existing body
  existing=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "https://api.cloudflare.com/client/v4/zones/$ZID/dns_records?type=$1&name=$2" | jq -r '.result[0].id // empty')
  body="{\"type\":\"$1\",\"name\":\"$2\",\"content\":\"$3\",\"ttl\":300,\"proxied\":false}"
  if [ -n "$existing" ]; then
    curl -s -X PUT  -H "Authorization: Bearer $TOKEN" -H "content-type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$ZID/dns_records/$existing" -d "$body" | jq '.success'
  else
    curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "content-type: application/json" \
      "https://api.cloudflare.com/client/v4/zones/$ZID/dns_records" -d "$body" | jq '.success'
  fi
}
upsert A    mastropaolo.dev      66.241.124.66
upsert AAAA mastropaolo.dev      2a09:8280:1::11c:a050:0
upsert A    www.mastropaolo.dev  66.241.124.66
upsert AAAA www.mastropaolo.dev  2a09:8280:1::11c:a050:0
```
> There were TWO apex `A` records (104.21.* and 172.67.*). `upsert` updates one — DELETE any remaining apex A/AAAA still pointing at `104.21.*` / `172.67.*`.

### B. Verify DNS + cert
```bash
dig +short A    mastropaolo.dev      # expect 66.241.124.66
dig +short AAAA mastropaolo.dev      # expect 2a09:8280:1::11c:a050:0
dig +short A    www.mastropaolo.dev  # expect 66.241.124.66
fly certs check mastropaolo.dev     --app provenance-toe   # Status = Issued / Verified
fly certs check www.mastropaolo.dev --app provenance-toe   # Status = Issued / Verified
curl -sI https://mastropaolo.dev/api/health                # HTTP/2 200
```
(Propagation + Fly cert issuance can take a few minutes.)

### C. Final flip — retire fly.dev
Once `mastropaolo.dev` serves 200 and certs verify, enable the already-deployed dormant redirect:
```bash
fly secrets set CANONICAL_HOST=mastropaolo.dev --app provenance-toe
```
Middleware already ships the `*.fly.dev → CANONICAL_HOST` 308 redirect behind this env. Verify:
```bash
curl -sI https://provenance-toe.fly.dev/  # expect 308 → https://mastropaolo.dev/
curl -sI https://mastropaolo.dev/login    # expect 200
```

## Done when
`dig` shows the Fly IPs for apex + www, both Fly certs `Verified`, `https://mastropaolo.dev/login` → 200, and `*.fly.dev` 308-redirects to `mastropaolo.dev`.
