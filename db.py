import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


def get_order(order_id: str) -> dict | None:
    """Return one order as a dict, or None if it doesn't exist."""
    with psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as conn:
        row = conn.execute(
            """
            SELECT order_id, customer_name, status, expected_delivery, total
            FROM orders
            WHERE order_id = %s
            """,
            (order_id.strip().upper(),),
        ).fetchone()
    return row


if __name__ == "__main__":
    # Quick manual test: python db.py
    print(get_order("ORD-1002"))
    print(get_order("ORD-9999"))
