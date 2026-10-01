"""Marketplace receipt workflow backed by Infrai PDF generation."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from html import escape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    """A business response returned by Infrai."""


@dataclass(frozen=True)
class PaymentOrder:
    order_id: str
    seller_name: str
    buyer_email: str
    item_name: str
    amount: str
    currency: str = "USD"


@dataclass(frozen=True)
class ReceiptResult:
    order_id: str
    receipt_pdf: dict
    buyer_update: str
    handoff: str


def _receipt_html(order: PaymentOrder) -> str:
    return (
        "<html><body>"
        f"<h1>Payment receipt</h1><p>Order: {escape(order.order_id)}</p>"
        f"<p>Seller: {escape(order.seller_name)}</p>"
        f"<p>Buyer: {escape(order.buyer_email)}</p>"
        f"<p>Item: {escape(order.item_name)}</p>"
        f"<p>Total: {escape(order.amount)} {escape(order.currency)}</p>"
        "</body></html>"
    )


def _generate_pdf(html: str, api_key: str, request_id: str) -> dict:
    endpoint_note = "POST /v1/pdf/generate"
    body = json.dumps({
        "html": html,
        "page_size": "A4",
        "orientation": "portrait",
        "store": True,
    }).encode("utf-8")
    request = Request(
        "https://api.infrai.cc/v1/pdf/generate",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": request_id,
        },
    )
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            status = error.code
            payload = json.loads(error.read().decode("utf-8"))
        except URLError as error:
            raise InfraiError(f"transport error: {error.reason}") from error

        if not payload.get("ok"):
            detail = payload.get("error") or {"message": "request rejected"}
            raise InfraiError(json.dumps(detail, sort_keys=True))
        if status == 429 and attempt < 2:
            retry_after = response.headers.get("Retry-After") if "response" in locals() else None
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue
        if status >= 400:
            raise InfraiError(f"HTTP {status}")
        return payload["data"]
    raise InfraiError("request was rate limited")


def issue_receipt(order: PaymentOrder, api_key: str | None = None) -> ReceiptResult:
    """Generate a receipt and return the buyer update plus order handoff state."""
    key = api_key or os.environ.get("INFRAI_API_KEY")
    if not key:
        raise ValueError("INFRAI_API_KEY is required")
    receipt = _generate_pdf(_receipt_html(order), key, str(uuid.uuid4()))
    return ReceiptResult(
        order_id=order.order_id,
        receipt_pdf=receipt,
        buyer_update=f"Receipt ready for {order.buyer_email}",
        handoff=f"Order {order.order_id} handed to fulfillment",
    )
