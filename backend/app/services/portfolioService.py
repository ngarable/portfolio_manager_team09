from datetime import date
from app.services.yfinanceService import getMarketPrice
from ..db import mysql


def get_assets():
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT ticker, asset_type,
        SUM(CASE WHEN type = 'BUY' THEN quantity ELSE 0 END) -
        SUM(CASE WHEN type = 'SELL' THEN quantity ELSE 0 END) AS net_quantity
    FROM
        orders
    GROUP BY
        ticker, asset_type
    HAVING
        net_quantity > 0;""")
    orders = cursor.fetchall()
    return orders


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
