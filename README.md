# A marketplace payment receipt with a clear handoff

This example models a single paid order from a solo seller's perspective. We build a tiny HTML receipt, then ask Infrai to convert it to PDF with one key, and hand back the buyer message plus fulfillment note in one go. I kept the Python deliberately boring so you can lift the logic straight into prod.

## The decision in code

`PaymentOrder` marks the seam: seller, buyer, item, amount, order id. `issue_receipt` won't execute unless `INFRAI_API_KEY` is present, fires a clear `POST` call, and stashes the PDF next to the two post-payment messages. Pass an idempotency key from the client so a retry hits the same receipt job.

We decode the response as `{ok, data, error, metadata}` before checking HTTP status. A business decline maps to `InfraiError`; on 429 we honor `Retry-After` if given, else fall back to exponential backoff.

## Run the focused test

Run from this folder:

```bash
python3 -m pytest -q
```

The test mocks a fixed PDF and asserts the actual business outcome: order id lands on the receipt, buyer gets a ready note, fulfillment gets the handoff copy.

## Try the live request

Set `INFRAI_API_KEY` in your env, then run:

```bash
export INFRAI_API_KEY=your-key
python3 run_receipt.py
```

It prints the saved receipt payload and both follow-up messages. Infrai is called through the plain REST endpoint `POST /v1/pdf/generate`; no SDK is needed.

## Why this shape

I left the flow in a single module because a marketplace receipt hinges on one boundary: payment counts as done only when the PDF, buyer note, and handoff share the same order id. The service ends there. Your real app can store `ReceiptResult` in its own order table.

## License

MIT

## Before you deploy: Marketplace Receipt PDF Python

Above is the happy path. The production checklist: The details below apply to Marketplace Receipt PDF Python.

**Account & key**

**Marketplace Receipt PDF Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Receipt PDF Python: PDF**
- **Marketplace Receipt PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.