from datetime import date
from decimal import Decimal
from app.services.yfinanceService import getMarketPrice
from ..db import mysql


def get_assets():
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT ticker, asset_type,
            ROUND(SUM(price * quantity) / NULLIF(SUM(quantity), 0),2) AS weighted_avg_price,
            SUM(remaining_quantity) AS net_quantity
            FROM orders
            WHERE remaining_quantity > 0
            GROUP BY ticker, asset_type;""")
    orders = cursor.fetchall()
    return orders


def get_recent_orders():
    sql = """SELECT date, ticker, type, quantity, price FROM portfolio_db.orders
    ORDER BY id DESC;"""
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    orders = cursor.fetchall()
    data = []
    for order in orders:
        date_str = order[0].strftime('%Y-%m-%d')
        data.append({
            "date": date_str,
            "ticker": order[1],
            "type": order[2],
            "quantity": order[3],
            "price": order[4]
        })
    return data


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


def get_asset_value_allocation() -> list[dict]:
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT
            ticker,
            asset_type,
            SUM(remaining_quantity) AS quantity
        FROM orders
        WHERE remaining_quantity > 0
        GROUP BY ticker, asset_type
    """)
    rows = cursor.fetchall()
    cursor.close()

    totals_by_type: dict[str, float] = {}
    overall_total = 0.0

    for ticker, asset_type, quantity in rows:
        price = getMarketPrice(ticker) or 0.0
        value = price * float(quantity)
        totals_by_type.setdefault(asset_type, 0.0)
        totals_by_type[asset_type] += value
        overall_total += value

    result = []
    for asset_type, value in totals_by_type.items():
        pct = round((value / overall_total) * 100,
                    2) if overall_total > 0 else 0.0
        result.append({
            "asset_type": asset_type,
            "value":       round(value, 2),
            "percent":     pct
        })

    return result


def buy_asset(ticker: str, asset_type: str, quantity: int) -> dict:
    market_price = getMarketPrice(ticker)
    if market_price is None:
        buy_price = 0
    else:
        buy_price = round(market_price, 2)

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO orders
            (type, ticker, asset_type, quantity, price, remaining_quantity)
        VALUES
            ('BUY', %s, %s, %s, %s, %s)
    """, (ticker, asset_type, quantity, buy_price, quantity))
    mysql.connection.commit()
    order_id = cursor.lastrowid
    return {
        "id":                 order_id,
        "ticker":             ticker,
        "asset_type":         asset_type,
        "quantity":           quantity,
        "buy_price":          buy_price,
        "remaining_quantity": quantity,
    }


def get_cash_balance():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT cash_balance
        FROM snapshots
        WHERE date <= %s
        ORDER BY date DESC
        LIMIT 1
    """, (date.today(),))
    row = cursor.fetchone()
    cursor.close()
    return float(row[0]) if row else 0.0


def set_cash_balance(new_balance):
    today = date.today()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT 1 FROM snapshots WHERE date = %s", (today,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE snapshots
            SET cash_balance = %s,
                net_worth = total_invested_value + %s
            WHERE date = %s
        """, (new_balance, new_balance, today))
    else:
        cursor.execute("""
            INSERT INTO snapshots (date, total_invested_value, cash_balance, net_worth)
            VALUES (%s, %s, %s, %s)
        """, (today, 0, new_balance, new_balance))

    mysql.connection.commit()
    cursor.close()


def get_latest_snapshot():
    cursor = mysql.connection.cursor()
    query = """
        SELECT date, total_invested_value, cash_balance, net_worth
        FROM snapshots
        ORDER BY date DESC
        LIMIT 1
    """
    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return None

    date_str = row[0].strftime('%Y-%m-%d')
    return {
        "date": date_str,
        "total_invested_value": float(row[1]),
        "cash_balance": float(row[2]),
        "net_worth": float(row[3])
    }


def update_snapshot():
    today = date.today()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT ticker, SUM(remaining_quantity) AS quantity
        FROM orders
        WHERE remaining_quantity > 0
        GROUP BY ticker
    """)
    holdings = cursor.fetchall()

    total_invested_value = 0.0
    for ticker, quantity in holdings:
        price = getMarketPrice(ticker) or 0.0
        total_invested_value += price * float(quantity)

    cash_balance = get_cash_balance()

    net_worth = total_invested_value + cash_balance

    cursor.execute("SELECT 1 FROM snapshots WHERE date = %s", (today,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE snapshots
            SET total_invested_value = %s,
                cash_balance = %s,
                net_worth = %s
            WHERE date = %s
        """, (total_invested_value, cash_balance, net_worth, today))
    else:
        cursor.execute("""
            INSERT INTO snapshots (date, total_invested_value, cash_balance, net_worth)
            VALUES (%s, %s, %s, %s)
        """, (today, total_invested_value, cash_balance, net_worth))

    mysql.connection.commit()
    cursor.close()


def get_snapshot_history():
    cursor = mysql.connection.cursor()
    query = """
        SELECT date, net_worth
        FROM snapshots
        ORDER BY date ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "date": row[0].strftime('%Y-%m-%d'),
            "net_worth": float(row[1])
        }
        for row in rows
    ]


def add_cash_balance(amount: float):
    """Increment today’s cash_balance by `amount` (and update net_worth),
       without ever touching total_invested_value."""
    today = date.today()
    amount_dec = Decimal(str(amount))
    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT total_invested_value, cash_balance FROM snapshots WHERE date = %s",
        (today,),
    )
    row = cursor.fetchone()

    if row:
        invested_value = Decimal(str(row[0]))
        old_cash = Decimal(str(row[1]))

        new_cash = old_cash + amount_dec
        new_net = invested_value + new_cash

        cursor.execute(
            "UPDATE snapshots "
            "SET cash_balance = %s, net_worth = %s "
            "WHERE date = %s",
            (new_cash, new_net, today),
        )

    else:
        cursor.execute(
            "SELECT total_invested_value, cash_balance "
            "FROM snapshots WHERE date < %s "
            "ORDER BY date DESC LIMIT 1",
            (today,),
        )
        prev = cursor.fetchone()
        if prev:
            invested_value = Decimal(str(prev[0]))
            old_cash = Decimal(str(prev[1]))
        else:
            invested_value = Decimal("0")
            old_cash = Decimal("0")

        new_cash = old_cash + amount_dec
        new_net = invested_value + new_cash

        cursor.execute(
            "INSERT INTO snapshots "
            "(date, total_invested_value, cash_balance, net_worth) "
            "VALUES (%s, %s, %s, %s)",
            (today, invested_value, new_cash, new_net),
        )

    mysql.connection.commit()
    cursor.close()


def process_buy_flow(amount: float):
    today = date.today()
    amt = Decimal(str(amount))
    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT total_invested_value, cash_balance "
        "FROM snapshots WHERE date = %s",
        (today,),
    )
    row = cursor.fetchone()

    if row:
        invested = Decimal(str(row[0]))
        cash = Decimal(str(row[1]))
    else:
        cursor.execute(
            "SELECT total_invested_value, cash_balance "
            "FROM snapshots WHERE date < %s "
            "ORDER BY date DESC LIMIT 1",
            (today,),
        )
        prev = cursor.fetchone()
        if prev:
            invested = Decimal(str(prev[0]))
            cash = Decimal(str(prev[1]))
        else:
            invested = Decimal("0")
            cash = Decimal("0")

    new_invested = invested + amt
    new_cash = cash - amt
    new_net = new_invested + new_cash

    if row:
        cursor.execute(
            "UPDATE snapshots "
            "SET total_invested_value = %s, cash_balance = %s, net_worth = %s "
            "WHERE date = %s",
            (new_invested, new_cash, new_net, today),
        )
    else:
        cursor.execute(
            "INSERT INTO snapshots "
            "(date, total_invested_value, cash_balance, net_worth) "
            "VALUES (%s, %s, %s, %s)",
            (today, new_invested, new_cash, new_net),
        )

    mysql.connection.commit()
    cursor.close()


def process_sell_flow(amount: float):
    today = date.today()
    amt = Decimal(str(amount))
    cursor = mysql.connection.cursor()

    cursor.execute(
        "SELECT total_invested_value, cash_balance "
        "FROM snapshots WHERE date = %s",
        (today,),
    )
    row = cursor.fetchone()

    if row:
        invested = Decimal(str(row[0]))
        cash = Decimal(str(row[1]))
    else:
        cursor.execute(
            "SELECT total_invested_value, cash_balance "
            "FROM snapshots WHERE date < %s "
            "ORDER BY date DESC LIMIT 1",
            (today,),
        )
        prev = cursor.fetchone()
        if prev:
            invested = Decimal(str(prev[0]))
            cash = Decimal(str(prev[1]))
        else:
            invested = Decimal("0")
            cash = Decimal("0")

    new_invested = invested - amt
    new_cash = cash + amt
    new_net = new_cash + new_invested

    if row:
        cursor.execute(
            "UPDATE snapshots "
            "SET total_invested_value = %s, cash_balance = %s, net_worth = %s "
            "WHERE date = %s",
            (new_invested, new_cash, new_net, today),
        )
    else:
        cursor.execute(
            "INSERT INTO snapshots "
            "(date, total_invested_value, cash_balance, net_worth) "
            "VALUES (%s, %s, %s, %s)",
            (today, new_invested, new_cash, new_net),
        )

    mysql.connection.commit()
    cursor.close()
