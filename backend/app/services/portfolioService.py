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

   