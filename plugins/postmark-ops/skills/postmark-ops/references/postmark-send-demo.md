# Runbook — send the Postmark deliverability proof email (direct API)

**Authored:** 2026-05-29 · **Status:** ready to run once `POSTMARK_SERVER_TOKEN` is supplied.
**Goal:** prove `mastropaolo.dev` Postmark authentication (DKIM / SPF / DMARC) works end-to-end
by sending one clearly-labelled demo email and confirming the recipient sees `DKIM=pass`.

This bypasses the app, the Fly secret, and the admin-login gate — it talks straight to the
Postmark HTTP API, mirroring the body shape of `packages/outreach/src/email/send.ts`
(multipart HtmlBody+TextBody, tracking off, RFC 8058 one-click List-Unsubscribe).

## Preconditions
- DKIM TXT published & resolving:
  `dig +short TXT 20260529133549pm._domainkey.mastropaolo.dev` → returns `k=rsa;p=…`. (confirmed 2026-05-29)
- Postmark domain `mastropaolo.dev` (signature_domains/6117578) shows **Verified** for DKIM.
  Return-Path (`pm-bounces.mastropaolo.dev` CNAME → `pm.mtasv.net`) is optional for the send to
  succeed but improves DMARC alignment; as of 2026-05-29 it is **not yet published**.
- A **Postmark Server Token** (Postmark → Servers → <server> → API Tokens). This is the only
  missing input; it is NOT stored in any repo file, env, Fly secret, or the DB.

## Send (parameterise TOKEN; never echo it)
```bash
TOKEN="$POSTMARK_SERVER_TOKEN"          # supply out-of-band; do not commit
FROM='"Provenance Demo" <demo@mastropaolo.dev>'
TO='amastro1996@gmail.com'
UNSUB="https://mastropaolo.dev/api/unsubscribe/demo-proof"

curl -sS https://api.postmarkapp.com/email \
  -H "X-Postmark-Server-Token: $TOKEN" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "$(cat <<JSON
{
  "From": "$FROM",
  "To": "$TO",
  "ReplyTo": "demo@mastropaolo.dev",
  "Subject": "[DEMO] Postmark authentication check for mastropaolo.dev",
  "HtmlBody": "<!doctype html><html><body style=\"font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a1a1a\"><p><strong>This is a demo deliverability check.</strong> No real prospect was contacted.</p><p>If you are reading this in Gmail, open <em>Show original</em> and confirm <strong>DKIM: PASS</strong>, <strong>SPF: PASS</strong>, signed-by <code>mastropaolo.dev</code>.</p><hr/><p style=\"font-size:12px;color:#888\">Sent via Postmark from mastropaolo.dev. <a href=\"$UNSUB\">Unsubscribe</a>.</p></body></html>",
  "TextBody": "This is a DEMO deliverability check. No real prospect was contacted.\n\nIn Gmail, open 'Show original' and confirm DKIM: PASS, SPF: PASS, signed-by mastropaolo.dev.\n\nSent via Postmark from mastropaolo.dev. Unsubscribe: $UNSUB",
  "MessageStream": "outbound",
  "TrackOpens": false,
  "TrackLinks": "None",
  "Headers": [
    { "Name": "List-Unsubscribe", "Value": "<$UNSUB>, <mailto:unsubscribe@mastropaolo.dev>" },
    { "Name": "List-Unsubscribe-Post", "Value": "List-Unsubscribe=One-Click" }
  ]
}
JSON
)"
```

## Expected result
- Success: JSON with `"ErrorCode": 0` and a `"MessageID"`. The email lands in
  amastro1996@gmail.com; **Show original** shows `DKIM: PASS` / `SPF: PASS` / signed-by
  `mastropaolo.dev` → authentication proven.
- `ErrorCode 412` / `300` → the Postmark Sender Signature / domain isn't Verified yet
  (finish DKIM verify in Postmark first — see `postmark-dns-cloudflare.md`).
- `ErrorCode 10` / 401 → bad/expired Server Token.

## Productionising (optional, after proof)
Install the token so the in-app `/api/admin/send-demo` route works too:
```bash
fly secrets set POSTMARK_SERVER_TOKEN="…" DEMO_FROM_EMAIL="demo@mastropaolo.dev" --app provenance-toe
```
(Note: `POSTMARK_SERVER_TOKEN` resolves from the process env only — it is intentionally NOT in
the `PROVIDER_SECRETS` DB catalog, so a Fly secret / env var is the only supported source.)
