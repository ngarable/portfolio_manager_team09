from datetime import date
from app.services.yfinanceService import getMarketPrice
from ..db import mysql


def get_assets():
  cursor = mysql.connection.cursor()
  cursor.execute("""SELECT ticker, asset_type, sum(remaining_quantity) as net_quantity
    FROM orders
    WHERE remaining_quantity > 0
    GROUP BY ticker, asset_type;""")
  orders = cursor.fetchall()
  return orders

def get_remaining_asset_batches(ticker):
    cursor = mysql.connection.cursor()
    query = """
        SELECT id, remaining_quantity, price
        FROM orders
        WHERE ticker = %s AND type = 'BUY' AND remaining_quantity > 0
        ORDER BY date ASC;
    """
    cursor.execute(query, (ticker,))
    asset_batches = cursor.fetchall()
    data = []
    for batch in asset_batches:
        data.append({
            "id": batch[0],
            "remaining_quantity": batch[1],
            "buy_price": batch[2]
        })
    return data

def update_order_quantity(order_id, new_quantity):
    cursor = mysql.connection.cursor()
    query = "UPDATE orders SET remaining_quantity = %s WHERE id = %s"
    cursor.execute(query, (new_quantity, order_id))
    mysql.connection.commit()
    cursor.close()
    return True

def sell_asset(ticker, quantity, market_price, asset_type):
    cursor = mysql.connection.cursor()

    # Insert SELL order
    query = """
        INSERT INTO orders (type, ticker, asset_type, quantity, price, remaining_quantity)
        VALUES (%s, %s, %s, %s, %s, NULL)
    """

    cursor.execute(query, ('SELL', ticker, asset_type, quantity, market_price))

    mysql.connection.commit()
    cursor.close()
    return True

   

def get_asset_allocation():
    cursor = mysql.connection.cursor()
    cursor.execute("""
            SELECT
                asset_type,
                SUM(CASE WHEN type = 'BUY'  THEN quantity ELSE 0 END)
              - SUM(CASE WHEN type = 'SELL' THEN quantity ELSE 0 END) AS net_quantity
            FROM orders
            GROUP BY asset_type
            HAVING net_quantity > 0;
        """)
    rows = cursor.fetchall()
    return rows


def buy_asset(ticker: str, asset_type: str, quantity: int) -> dict:
    market_price = getMarketPrice(ticker)
    if market_price is None:
        buy_price = 0
    else:
        buy_price = round(market_price, 2)
    today = date.today()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO orders
            (date, type, ticker, asset_type, quantity, buy_price, remaining_quantity)
        VALUES
            (%s, 'BUY', %s, %s, %s, %s, %s)
    """, (today, ticker, asset_type, quantity, buy_price, quantity))
    mysql.connection.commit()
    order_id = cursor.lastrowid
    return {
        "id":                 order_id,
        "ticker":             ticker,
        "asset_type":         asset_type,
        "quantity":           quantity,
        "buy_price":          buy_price,
        "remaining_quantity": quantity,
        "date":               today.isoformat()
    }
