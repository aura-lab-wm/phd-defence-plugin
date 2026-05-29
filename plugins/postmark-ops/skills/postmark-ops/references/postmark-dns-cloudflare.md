# Runbook — add Postmark DNS in Cloudflare (browser-agent / claude-chrome)

Operating plan for a browser-driving agent to add the two outstanding Postmark
records for **mastropaolo.dev** in the **Cloudflare** dashboard, then verify in
Postmark. Live DNS check (2026-05-29) confirmed: SPF + DMARC already present;
**DKIM and Return-Path are missing** and must be added.

## Preconditions (the human does these, once)

**Both** browser sessions must already be signed in before the agent runs — it
**cannot** clear a login / MFA / SSO wall; if one appears it pauses and hands
control back to the human.

- **REQUIRED — Postmark** (the source of truth in Part 0):
  `https://account.postmarkapp.com/signature_domains/6117578`. This is the
  non-negotiable login — without it the agent has no records to read. Confirm
  the domain's **DNS Settings** are visible here.
- **The DNS provider that hosts `mastropaolo.dev`** — here that's **Cloudflare**
  (`https://dash.cloudflare.com`, with the `mastropaolo.dev` zone visible). If
  the zone actually lives elsewhere (registrar, Route 53, Namecheap, etc.), log
  into *that* instead: Part A's clicks are written for Cloudflare, but the field
  values (Type, Host, Value, and "DNS only / unproxied") are provider-agnostic —
  adapt the clicks to whatever DNS UI you're in.

## Hard guardrails (read before acting)
- **Do NOT modify or delete** the existing `SPF` (`v=spf1 …`) or `DMARC`
  (`_dmarc`) TXT records. Only ADD the two new records below.
- **Do NOT create duplicates** — before adding each record, scan the existing
  DNS list; if a record with the same Name already exists, stop and report.
- The **Return-Path CNAME must be "DNS only" (grey cloud), NOT proxied
  (orange).** A proxied bounce CNAME breaks Postmark. This is the #1 mistake.
- TXT values: paste **exactly**, no surrounding quotes (Cloudflare adds its own).

---

## Part 0 — Postmark: read the records (source of truth)

Postmark's DNS page is the authority — selectors and key values are
account/domain-specific and can change. The agent **reads the records from
Postmark first**, captures them into variables, and uses those captured values
in Part A. The values printed in Part A are the last-known snapshot (2026-05-29)
— **if Postmark shows anything different, Postmark wins.**

1. Open the domain DNS page:
   `https://account.postmarkapp.com/signature_domains/6117578`
   (Postmark → **Sending → Domains → mastropaolo.dev → DNS Settings**).
2. Locate the **DKIM** block. Read and capture **verbatim** (use each field's
   "Copy" button when present; otherwise select the displayed text):
   - `DKIM_TYPE` — the record type Postmark shows: **`TXT`** *or* **`CNAME`**
     (varies by account — do not assume).
   - `DKIM_HOST` — the Hostname, e.g. `20260529133549pm._domainkey`
     *(strip a trailing `.mastropaolo.dev` if Postmark shows the FQDN — Cloudflare
     re-appends the zone; keep only the left-hand label).*
   - `DKIM_VALUE` — the full value: the `k=rsa;p=…` public key (if `TXT`) **or**
     the `<selector>.dkim.mtasv.net` target (if `CNAME`). Copy the entire string;
     do not truncate.
3. Locate the **Return-Path** block (a.k.a. "Custom Return-Path"). Capture:
   - `RP_HOST` — the Hostname, e.g. `pm-bounces` (strip a trailing
     `.mastropaolo.dev`).
   - `RP_VALUE` — the CNAME target, expected `pm.mtasv.net`.
4. **Sanity check before leaving Postmark:** `DKIM_VALUE` is non-empty and
   (if TXT) starts with `k=rsa;p=`; `RP_VALUE` ends in `mtasv.net`. If a field is
   blank or the page shows an error, stop and report — do not guess.
5. Note each record's current Postmark status (likely "Pending"/"unverified");
   these flip to **Verified** in Part C after Cloudflare + propagation.

Carry `DKIM_TYPE / DKIM_HOST / DKIM_VALUE` and `RP_HOST / RP_VALUE` into Part A.

---

## Part A — Cloudflare: add the two records

> Use the values captured in **Part 0**. The literals below are the 2026-05-29
> snapshot — if Part 0 read something different, use Part 0's values.

Navigate: `dash.cloudflare.com` → click the **mastropaolo.dev** zone → left nav
**DNS** → **Records**.

### A1. DKIM (TXT)
1. Click **Add record**.
2. **Type**: select `TXT`.
3. **Name**: type `20260529133549pm._domainkey`
   *(enter only this — Cloudflare appends `.mastropaolo.dev` automatically; do not type the full domain).*
4. **Content**: paste exactly:
   ```
   k=rsa;p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCS8dSx/tE/YNlgrF77Yhl1xQSa5fyO0DRncs3ERAbiGrr7pwXrlLjAkZewZhRtWp7m0qtSV4q8U1XEHuiXvDcNOcihfzQ6qlR7TRlogDBQ6w6IRbD7EE/+C8qkbNJ7FF8zsDDcv7smNASm3XSsI44dBbB++2GMdJN5Xwx4dfpN4QIDAQAB
   ```
5. **TTL**: leave `Auto`.
6. Click **Save**.
7. **Verify in the list**: a `TXT` row for `20260529133549pm._domainkey` now shows,
   content starting `k=rsa;p=MIGf…`. If not, report and stop.

### A2. Return-Path (CNAME)
1. Click **Add record**.
2. **Type**: select `CNAME`.
3. **Name**: type `pm-bounces`
   *(Cloudflare appends the zone → `pm-bounces.mastropaolo.dev`).*
4. **Target** (a.k.a. "Content"): type `pm.mtasv.net`
5. **Proxy status**: ensure the cloud is **grey = "DNS only"**. If it shows
   orange ("Proxied"), click it to toggle to DNS only. *(Critical.)*
6. **TTL**: leave `Auto`.
7. Click **Save**.
8. **Verify in the list**: a `CNAME` row `pm-bounces` → `pm.mtasv.net`,
   Proxy = **DNS only**. If proxied (orange), open it, set DNS only, Save again.

### A3. (Optional, skip unless asked) SPF merge
The zone already has `v=spf1 include:_spf.mx.cloudflare.net ~all`, and Postmark
self-manages SPF. **Do nothing here.** Only if explicitly told to add Postmark
SPF: EDIT the existing SPF record (do not add a second `v=spf1`) to
`v=spf1 include:_spf.mx.cloudflare.net include:spf.mtasv.net ~all`.

---

## Part B — wait for propagation
Cloudflare usually propagates in **under 5 minutes** (often seconds). Before
verifying in Postmark, confirm the records resolve. Either:
- open `https://www.whatsmydns.net/#TXT/20260529133549pm._domainkey.mastropaolo.dev`
  and `…/#CNAME/pm-bounces.mastropaolo.dev` and confirm they show, **or**
- hand back to the human/CLI to run:
  `dig +short TXT 20260529133549pm._domainkey.mastropaolo.dev` and
  `dig +short CNAME pm-bounces.mastropaolo.dev` (both should return values).

If empty, wait ~5 min and re-check (do not loop more than ~6 times / 30 min).

---

## Part C — Postmark: verify
1. Go to `https://account.postmarkapp.com/signature_domains/6117578`.
2. For **DKIM**: click **Verify** (or "Recheck"). Expect it to flip to a green
   **Verified**. If still pending, propagation isn't done — wait and retry.
3. For **Return-Path**: click **Verify**. Expect green **Verified**.
4. (Optional) Set the **Custom Return-Path** to `pm-bounces.mastropaolo.dev` if
   Postmark prompts.
5. **Success state**: the domain page shows DKIM ✅ and Return-Path ✅ (green).
   Report this back — that's the signal the operator can set the token and the
   `/api/admin/send-demo` route will deliver to the inbox instead of 503/spam.

---

## What this does NOT cover (human/operator)
- Generating/installing the **`POSTMARK_SERVER_TOKEN`** (Settings → API keys, or
  `fly secrets set`) and `DEMO_FROM_EMAIL=demo@mastropaolo.dev` — separate step,
  done after the two records are green.
- Solving any login / MFA prompt — pause and return control to the human.
