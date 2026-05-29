# Runbook — add Postmark DNS at ANY registrar / DNS provider

**Authored:** 2026-05-29 · Provider-agnostic generalization of `postmark-dns-cloudflare.md`.
**Goal:** publish the two outstanding Postmark records (**DKIM** + **Return-Path**) for a sending
domain in *whatever* DNS provider hosts the zone, then flip the domain to **Verified** in Postmark.

This is for a browser-driving or API agent. The clicks differ per provider; the **field values are
provider-agnostic**. Postmark is always the source of truth — read the records from Postmark first.

## Preconditions (the human does these once)
- **Signed into Postmark** for the sending domain → Sending → Domains → `<domain>` → **DNS Settings**.
  Without this the agent has no records to read. (Worked example domain: `mastropaolo.dev`,
  `https://account.postmarkapp.com/signature_domains/6117578`.)
- **Signed into the zone's DNS provider** — see "Find where DNS lives" below. The agent cannot
  clear a login / MFA / SSO wall; if one appears it pauses and hands control back.

## Find where the domain's DNS lives (do this, don't assume Cloudflare)
The authoritative nameservers tell you which provider's UI/API to use:
```bash
dig +short NS <domain>
```
Map the answer to a provider and log into *that*:
| Nameserver pattern | Provider | Where you add records |
|---|---|---|
| `*.ns.cloudflare.com` | **Cloudflare** | dash.cloudflare.com → zone → DNS → Records |
| `*.registrar-servers.com` | **Namecheap** | Namecheap → Domain List → Manage → Advanced DNS |
| `ns-*.awsdns-*` | **AWS Route 53** | Route 53 → Hosted zones → `<domain>` |
| `ns*.domaincontrol.com` | **GoDaddy** | GoDaddy → Domains → DNS |
| `ns*.googledomains.com` / `*.squarespace.com` | **Google / Squarespace** | Domains → DNS |
| `ns*.dnsimple.com`, `dns*.p0*.nsone.net`, … | DNSimple / NS1 / other | that provider's DNS UI/API |
If NS points at the **registrar's own** nameservers, manage DNS in the registrar's control panel.
If you can't act on that provider, STOP and report which provider holds the zone.

## Hard guardrails (read before acting)
- **Do NOT modify or delete** existing `SPF` (`v=spf1 …`) or `DMARC` (`_dmarc`) TXT records. Only ADD.
- **Do NOT create duplicates** — scan the existing records first; if the same Name exists, stop & report.
- The **Return-Path CNAME must NOT be proxied/aliased through a CDN.** On Cloudflare set the cloud
  **grey ("DNS only")**; on other providers just use a plain CNAME. A proxied bounce CNAME breaks Postmark.
- Paste TXT values **exactly**, no surrounding quotes you add yourself (some UIs add their own).

## Part 0 — read the records from Postmark (source of truth)
On the domain's **DNS Settings** page, capture verbatim (use each "Copy" button):
- **DKIM** — `DKIM_TYPE` (**TXT** *or* **CNAME** — varies by account, don't assume),
  `DKIM_HOST` (e.g. `<selector>._domainkey`; strip a trailing `.<domain>` — most UIs re-append the zone),
  `DKIM_VALUE` (the full `k=rsa;p=…` public key if TXT, **or** the `<selector>.dkim.mtasv.net` target if CNAME).
- **Return-Path** — `RP_HOST` (e.g. `pm-bounces`), `RP_VALUE` (the CNAME target, typically `pm.mtasv.net`).
- Sanity check: `DKIM_VALUE` non-empty (TXT starts `k=rsa;p=`); `RP_VALUE` ends in `mtasv.net`.
  Blank/error → stop and report; don't guess.

## Part A — add the two records (provider-agnostic field values)
Add EACH record using the values captured in Part 0:

| Record | Type | Name / Host | Value / Target | Notes |
|---|---|---|---|---|
| DKIM | `DKIM_TYPE` (TXT *or* CNAME) | `DKIM_HOST` | `DKIM_VALUE` | enter host label only; provider re-appends the zone |
| Return-Path | CNAME | `RP_HOST` (e.g. `pm-bounces`) | `RP_VALUE` (e.g. `pm.mtasv.net`) | **plain / unproxied / DNS-only**; TTL Auto/300 |

Provider quirks:
- **Trailing dot:** Route 53 / BIND-style zone files want the CNAME target as a FQDN with a trailing
  dot (`pm.mtasv.net.`). Most web UIs (Cloudflare, Namecheap, GoDaddy) do not — enter `pm.mtasv.net`.
- **`@` / apex:** not needed here (these are subdomain records), but if a provider demands a full host,
  use `<host>.<domain>` (e.g. `pm-bounces.mastropaolo.dev`).
- **Proxy/CDN toggle:** only Cloudflare has the orange/grey cloud — set **grey** for the CNAME.
- **SPF:** Postmark self-manages SPF in most setups. Do **not** add a second `v=spf1`. Only if explicitly
  told to add Postmark SPF, EDIT the single existing record to include `include:spf.mtasv.net`.

## Part B — wait for propagation, then verify resolution
```bash
dig +short TXT  <DKIM_HOST>.<domain>      # DKIM TXT  → k=rsa;p=…   (if DKIM_TYPE=TXT)
dig +short CNAME <DKIM_HOST>.<domain>     # DKIM CNAME → …dkim.mtasv.net (if DKIM_TYPE=CNAME)
dig +short CNAME <RP_HOST>.<domain>       # Return-Path → pm.mtasv.net
```
(Or check `whatsmydns.net`.) Empty → wait ~5 min and re-check; don't loop more than ~6×/30 min.

## Part C — verify in Postmark
On the domain's DNS Settings page, click **Verify / Recheck** for DKIM and Return-Path until both show
green **Verified**. Success state: DKIM ✅ + Return-Path ✅. That's the signal the operator can install
`POSTMARK_SERVER_TOKEN` and the send path will deliver to the inbox.

## Not covered (human/operator)
- Generating/installing the **Postmark Server Token** + sender From address — separate step
  (see `postmark-send-demo.md`).
- Solving any login / MFA prompt — pause and return control to the human.
