orders = [
    {
        "id": 1,
        "ticker": "AAPL",
        "type": "BUY",
        "quantity": 10,
        "buy_price": 150.00,
        "transaction_date": "2025-07-01",
        "asset_type": "stock"
    },
    {
        "id": 2,
        "ticker": "TSLA",
        "type": "BUY",
        "quantity": 5,
        "buy_price": 220.00,
        "transaction_date": "2025-07-03",
        "asset_type": "stock"
    },
    {
        "id": 3,
        "ticker": "GOOG",
        "type": "BUY",
        "quantity": 8,
        "buy_price": 100.00,
        "transaction_date": "2025-07-05",
        "asset_type": "stock"
    },
    {
        "id": 4,
        "ticker": "AAPL",
        "type": "SELL",
        "quantity": 5,
        "buy_price": 160.00,
        "transaction_date": "2025-07-08",
        "asset_type": "stock"
    },
    {
        "id": 5,
        "ticker": "TSLA",
        "type": "BUY",
        "quantity": 2,
        "buy_price": 230.00,
        "transaction_date": "2025-07-10",
        "asset_type": "stock"
    },
    {
        "id": 6,
        "ticker": "AAPL",
        "type": "BUY",
        "quantity": 3,
        "buy_price": 158.00,
        "transaction_date": "2025-07-14",
        "asset_type": "stock"
    },
    {
        "id": 7,
        "ticker": "GOOG",
        "type": "SELL",
        "quantity": 3,
        "buy_price": 110.00,
        "transaction_date": "2025-07-18",
        "asset_type": "stock"
    },
    {
        "id": 8,
        "ticker": "TSLA",
        "type": "SELL",
        "quantity": 1,
        "buy_price": 235.00,
        "transaction_date": "2025-07-22",
        "asset_type": "stock"
    },
    {
        "id": 9,
        "ticker": "AAPL",
        "type": "SELL",
        "quantity": 3,
        "buy_price": 165.00,
        "transaction_date": "2025-07-26",
        "asset_type": "stock"
    },
    {
        "id": 10,
        "ticker": "GOOG",
        "type": "BUY",
        "quantity": 4,
        "buy_price": 108.00,
        "transaction_date": "2025-07-29",
        "asset_type": "stock"
    }
]

assets = [
    {
        "id": 1,
        "ticker": "AAPL",
        "type": "stock",
        "quantity": 5,
    },
    {
        "id": 2,
        "ticker": "TSLA",
        "type": "stock",
        "quantity": 6,
    },
    {
        "id": 3,
        "ticker": "GOOG",
        "type": "stock",
        "quantity": 5,
    }
]

def get_current_assets():
  return assets