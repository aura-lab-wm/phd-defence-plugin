---
name: postmark-ops
description: >-
  Send and verify Postmark transactional email end-to-end, including fetching the Server API token
  straight from an already-logged-in Chrome session (no hand-pasting). Use when the user wants to
  send a test/proof/deliverability email via Postmark, prove DKIM/SPF authentication for a sending
  domain works, get/locate a Postmark Server token, or check whether a Postmark sending domain is
  verified. Pairs with DNS setup (publish DKIM + Return-Path at any registrar) covered in references/.
  Triggers: "send a proof email via Postmark", "prove Postmark auth works", "get the Postmark server
  token", "is my Postmark domain verified", "Postmark deliverability check".
---

# postmark-ops

Operate Postmark for real. **Never claim a send you didn't observe** — require `ErrorCode: 0` + a
`MessageID`. **Treat the Server Token as a secret:** mask it in every output (`tok[:4]+"…"+tok[-4:]`),
write it only to a `0600` temp file, never echo/commit it, delete temp copies when done.

There are two halves; the DNS half may already be done.

## A. DNS — publish DKIM + Return-Path (any registrar)
If the sending domain isn't authenticated yet, publish the two Postmark records, then verify in
Postmark. Provider-agnostic steps: [`references/postmark-dns-any-provider.md`](references/postmark-dns-any-provider.md)
(Cloudflare worked example: [`references/postmark-dns-cloudflare.md`](references/postmark-dns-cloudflare.md)).
To point the web app's domain at a host: [`references/point-domain-at-host-any-provider.md`](references/point-domain-at-host-any-provider.md).
DNS proof is credential-free:
```bash
dig +short TXT <selector>._domainkey.<domain>   # DKIM → k=rsa;p=…
dig +short CNAME pm-bounces.<domain>            # Return-Path → pm.mtasv.net
```

## B. Fetch the Server token, then send (no hand-pasting)
The token already exists in the operator's Postmark account — harvest it from their logged-in Chrome
session via the **session-fetcher** skill instead of asking them to paste it. Full recipe with the
exact extraction regex: [`references/postmark-token-fetch.md`](references/postmark-token-fetch.md).

1. `~/.local/bin/session_fetcher register postmark --from-url 'https://account.postmarkapp.com/'` then `… refresh postmark`.
   (`requests`+`cryptography` usually already present; a `400` on `/` is AWS-WAF noise, not auth failure.)
2. With a real browser `User-Agent`, GET `https://account.postmarkapp.com/servers` → server IDs; for each,
   GET `/servers/<id>/credentials` and extract the token tied to the server by its delete link:
   `/account/api_tokens/<UUID>/confirm_destroy?server_id=<SID>`.
   ⚠️ **Decoy:** the page also has `data-api-key="<uuid>"` (Forethought chat widget, same on every server) —
   that is NOT the Postmark token. Never grab "the first UUID."
3. Validate: `GET https://api.postmarkapp.com/server` with `X-Postmark-Server-Token` → 200 + `{Name,ID}`.
4. Send: `POST https://api.postmarkapp.com/email` — multipart `HtmlBody`+`TextBody`,
   `MessageStream:"outbound"`, `TrackOpens:false`, `TrackLinks:"None"`, RFC 8058 `List-Unsubscribe`
   (`<https-url>, <mailto:…>`) + `List-Unsubscribe-Post: List-Unsubscribe=One-Click`. From any address
   `@<verified-domain>` (domain-level DKIM covers all addresses). Full payload:
   [`references/postmark-send-demo.md`](references/postmark-send-demo.md).

Interpret the response: `ErrorCode 0` + `MessageID` → accepted & DKIM-signed (success). `412`/`300` →
domain/signature not Verified in Postmark yet (finish DNS + verify). `10`/HTTP 401 → bad/expired token.

## Notes
- Listing domains/signatures needs an **Account** API token, not a Server token; with only a Server
  token the send result (`0` vs `412`) is your verification signal.
- A bundled `postmark-ops` agent (this plugin's `agents/`) encodes the same method for dispatch via the
  Agent tool; `cloudflare-ops` is its DNS-side pair.
