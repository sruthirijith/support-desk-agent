CREATE TABLE IF NOT EXISTS tickets (
    ticket_id  SERIAL PRIMARY KEY,
    order_id   VARCHAR(20) NOT NULL REFERENCES orders(order_id),
    issue      TEXT NOT NULL,
    status     VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
