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

