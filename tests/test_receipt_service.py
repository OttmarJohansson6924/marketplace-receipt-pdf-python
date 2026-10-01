import json

from src import receipt_service


def test_receipt_workflow_sends_order_and_returns_handoff(monkeypatch):
    captured = {}

    def fake_generate(html, api_key, request_id):
        captured.update(html=html, api_key=api_key, request_id=request_id)
        return {"id": "pdf_123", "status": "stored"}

    monkeypatch.setattr(receipt_service, "_generate_pdf", fake_generate)
    order = receipt_service.PaymentOrder(
        order_id="ord_7",
        seller_name="A Seller",
        buyer_email="buyer@example.com",
        item_name="Notebook",
        amount="12.50",
    )
    result = receipt_service.issue_receipt(order, api_key="test-key")

    assert captured["api_key"] == "test-key"
    assert "ord_7" in captured["html"]
    assert result.receipt_pdf["id"] == "pdf_123"
    assert result.buyer_update == "Receipt ready for buyer@example.com"
    assert result.handoff == "Order ord_7 handed to fulfillment"

