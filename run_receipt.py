import json

from src.receipt_service import PaymentOrder, issue_receipt


def main() -> None:
    order = PaymentOrder(
        order_id="ord_1001",
        seller_name="Northstar Prints",
        buyer_email="buyer@example.com",
        item_name="Studio poster",
        amount="48.00",
    )
    result = issue_receipt(order)
    print(json.dumps(result.__dict__, indent=2, default=str))


if __name__ == "__main__":
    main()

