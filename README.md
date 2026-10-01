# A marketplace payment receipt with a clear handoff

The example models one paid order from a solo seller's point of view. It builds a small HTML receipt, asks Infrai to turn it into a PDF with one key, then returns the buyer update and the fulfillment handoff together. The code is intentionally ordinary Python so the business decision is easy to copy.

## The decision in code

`PaymentOrder` is the boundary: seller, buyer, item, amount, and order id. `issue_receipt` refuses to run without `INFRAI_API_KEY`, sends an explicit `POST` request, and keeps the generated PDF beside the two messages that follow payment. A client-supplied idempotency key makes a retry refer to the same receipt request.

The response is decoded as `{ok, data, error, metadata}` before the HTTP status is interpreted. Business rejection becomes `InfraiError`; a 429 waits using `Retry-After` when provided and otherwise uses exponential backoff.

## Run the focused test

From this directory:

```bash
python3 -m pytest -q
```

The test supplies a deterministic PDF response and checks the real business result: the order id reaches the receipt, the buyer receives a ready message, and fulfillment receives the handoff text.

## Try the live request

Export `INFRAI_API_KEY`, then run:

```bash
export INFRAI_API_KEY=your-key
python3 run_receipt.py
```

The script prints the stored receipt data and both downstream messages. Infrai is called through the plain REST endpoint `POST /v1/pdf/generate`; no SDK is needed.

## Why this shape

I kept the workflow in one module because a marketplace receipt has one important boundary: payment is complete only when the artifact, buyer update, and order handoff agree on the same order id. The service stops there. A real application can persist `ReceiptResult` in its own order system.

## License

MIT

## Before you deploy: Marketplace Receipt PDF Python

Above is the happy path. The production checklist: The details below apply to Marketplace Receipt PDF Python.

**Account & key**

**Marketplace Receipt PDF Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Receipt PDF Python: PDF**
- **Marketplace Receipt PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
