DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id          VARCHAR(20) PRIMARY KEY,
    customer_name     VARCHAR(100) NOT NULL,
    status            VARCHAR(20)  NOT NULL,  -- processing, shipped, delayed, delivered
    expected_delivery DATE         NOT NULL,
    total             NUMERIC(10, 2) NOT NULL
);

-- Fake data only
INSERT INTO orders (order_id, customer_name, status, expected_delivery, total) VALUES
('ORD-1001', 'Asha Nair',    'shipped',    CURRENT_DATE + 2, 1499.00),
('ORD-1002', 'Rahul Menon',  'delayed',    CURRENT_DATE - 3, 2999.50),
('ORD-1003', 'Meera Das',    'delivered',  CURRENT_DATE - 5,  799.00),
('ORD-1004', 'Arun Kumar',   'processing', CURRENT_DATE + 5,  599.00);
