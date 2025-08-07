import traceback
from flask import Blueprint, jsonify, request
from app.services import portfolioService
from app.services import yfinanceService
from collections import defaultdict
from decimal import Decimal

from app.services.chatbotService import ask_chatbot

portfolio_bp = Blueprint('portfolio', __name__)


def fetch_assets():
    try:
        assets = portfolioService.get_assets()
        if not assets:
            return []

        data = []
        for asset in assets:
            data.append({
                "ticker": asset[0],
                "asset_type": asset[1],
                "price": asset[2],
                "quantity": asset[3]
            })
        return data
    except Exception as e:
        print(f"Error fetching assets: {e}")
        return []


@portfolio_bp.route("/recent_orders", methods=["GET"])
def get_recent_orders():
    try:
        orders = portfolioService.get_recent_orders()
        if not orders:
            return jsonify({"message": "No recent orders found"}), 404

        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/assets", methods=["GET"])
def get_assets():
    try:
        assets = fetch_assets()
        if not assets:
            return jsonify({"message": "No current assets found"}), 404

        return jsonify(assets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/pnl_by_asset", methods=["GET"])
def get_pnl_by_asset():
    try:
        assets = fetch_assets()
        if not assets:
            return jsonify({"message": "No current assets found"}), 404

        pnl_data = []

        for asset in assets:
            ticker = asset['ticker']
            asset_type = asset['asset_type']
            positions = portfolioService.get_remaining_asset_batches(ticker)

            for position in positions:
                quantity = position['remaining_quantity']
                buy_price = position['buy_price']
                current_price = yfinanceService.getMarketPrice(ticker)

                if current_price is None:
                    return jsonify({"error": f"Market price not available for {ticker}"}), 500

                total_invested = float(quantity) * float(buy_price)
                current_value = float(quantity) * float(current_price)
                pnl = current_value - total_invested
                pnl_percentage = (pnl / total_invested *
                                  100) if total_invested != 0 else 0

                pnl_data.append({
                    "ticker": ticker,
                    "asset_type": asset_type,
                    "quantity": quantity,
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "total_invested": round(total_invested, 2),
                    "current_value": round(current_value, 2),
                    "pnl": round(pnl, 2),
                    "pnl_percentage": round(pnl_percentage, 2)
                })

        # Aggregate by ticker
        agg = defaultdict(lambda: {
            "quantity": 0,
            "total_invested": Decimal("0"),
            "current_value": Decimal("0"),
            "pnl": Decimal("0"),
            "asset_type": None
        })

        for row in pnl_data:
            ticker = row["ticker"]
            agg[ticker]["quantity"] += row["quantity"]
            agg[ticker]["total_invested"] += Decimal(
                str(row["total_invested"]))
            agg[ticker]["current_value"] += Decimal(str(row["current_value"]))
            agg[ticker]["pnl"] += Decimal(str(row["pnl"]))
            agg[ticker]["asset_type"] = row["asset_type"]

        result = []
        for ticker, values in agg.items():
            total_invested = values["total_invested"]
            pnl = values["pnl"]
            pnl_percentage = (pnl / total_invested * Decimal("100")
                              ) if total_invested != 0 else Decimal("0")

            result.append({
                "ticker": ticker,
                "asset_type": values["asset_type"],
                "quantity": values["quantity"],
                "total_invested": float(round(total_invested, 2)),
                "current_value": float(round(values["current_value"], 2)),
                "pnl": float(round(pnl, 2)),
                "pnl_percentage": float(round(pnl_percentage, 2))
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/assets/buy", methods=["POST"])
def buy_asset():
    payload = request.get_json() or {}
    ticker = payload.get("ticker")
    quantity = payload.get("quantity")

    if not ticker or not quantity:
        return jsonify({"error": "Fields 'ticker' and 'quantity' are required"}), 400

    asset_type = yfinanceService.getAssetType(ticker)
    if not asset_type:
        return jsonify({"error": f"Could not fetch asset type for {ticker}"}), 500

    price = yfinanceService.getMarketPrice(ticker)
    if price is None:
        return jsonify({"error": f"Could not fetch price for {ticker}"}), 500

    total_cost = price * quantity
    current_cash = portfolioService.get_cash_balance()

    if current_cash < total_cost:
        return jsonify({
            "error": "Insufficient funds",
            "available_balance": current_cash,
            "required": total_cost
        }), 400

    try:
        order = portfolioService.buy_asset(ticker, asset_type, quantity)
        portfolioService.process_buy_flow(total_cost)
        snapshot = portfolioService.get_latest_snapshot()
        return jsonify({
            "message": "Buy order placed successfully",
            "order": order,
            "snapshot": snapshot
        }), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/asset_allocation", methods=["GET"])
def get_asset_allocation():
    try:
        allocation = portfolioService.get_asset_value_allocation()
        return jsonify(allocation), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/portfolio_value", methods=["GET"])
def get_portfolio_value():
    try:
        total_value = calculate_portfolio_value()
        return jsonify({
            "portfolio_value": round(total_value, 2)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def calculate_portfolio_value():
    assets = portfolioService.get_assets()
    total_value = 0

    for asset in assets:
        ticker = asset[0]
        quantity = float(asset[3])
        price = yfinanceService.getMarketPrice(ticker)
        if price is not None:
            total_value += quantity * price

    return round(total_value, 2)


@portfolio_bp.route("/gainers-losers", methods=["GET"])
def gainers_losers():
    try:
        assets = fetch_assets()
        changes = []

        for asset in assets:
            ticker = asset['ticker']
            change = yfinanceService.getPercentageChange(ticker)
            name = yfinanceService.getName(ticker)
            if change is not None:
                changes.append({
                    "ticker": ticker,
                    "name": name,
                    "change": change
                })

        # Sort by change percentage
        sorted_changes = sorted(
            changes, key=lambda x: x["change"], reverse=True)

        top_gainers = sorted_changes[:5]
        # last 5, reversed to show biggest drop first
        top_losers = sorted_changes[-5:][::-1]

        return jsonify({
            "gainers": top_gainers,
            "losers": top_losers
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/assets/sell", methods=["POST"])
def sell_asset():
    data = request.get_json() or {}
    ticker = data.get('ticker')
    qty_to_sell = data.get('quantity')

    if not ticker or not qty_to_sell:
        return jsonify({"error": "Missing ticker or quantity"}), 400

    assets = fetch_assets()
    asset = next((a for a in assets if a['ticker'] == ticker), None)
    if not asset:
        return jsonify({"message": f"Asset {ticker} not found"}), 400

    current_qty = int(asset['quantity'])
    if current_qty < qty_to_sell:
        return jsonify({
            "message": f"Not enough {ticker} to sell. Current quantity: {current_qty}"
        }), 400

    batches = portfolioService.get_remaining_asset_batches(ticker)
    remaining = qty_to_sell
    proceeds = 0
    price = yfinanceService.getMarketPrice(ticker)
    if price is None:
        return jsonify({"error": "Market price not available"}), 500

    for batch in batches:
        if remaining <= 0:
            break
        avail = batch['remaining_quantity']
        sold = min(remaining, avail)
        portfolioService.update_order_quantity(batch['id'], avail - sold)
        proceeds += sold * price
        remaining -= sold

    portfolioService.sell_asset(
        ticker, qty_to_sell, price, asset['asset_type'])

    portfolioService.process_sell_flow(proceeds)

    snapshot = portfolioService.get_latest_snapshot()
    return jsonify({
        "message": f"Sold {qty_to_sell} of {ticker}",
        "proceeds": proceeds,
        "snapshot": snapshot
    }), 200


@portfolio_bp.route("/asset_value_allocation", methods=["GET"])
def asset_value_allocation():
    try:
        assets = fetch_assets()
        if not assets:
            return jsonify({"message": "No current assets found"}), 404

        portfolio_value = calculate_portfolio_value()

        if portfolio_value is None:
            return jsonify({"error": "Could not calculate portfolio value"}), 500

        holdings = []

        for asset in assets:

            market_price = float(
                yfinanceService.getMarketPrice(asset['ticker']))
            if market_price is None:
                return jsonify({"error": f"Market price not available for {asset['ticker']}"}), 500

            quantity = float(asset['quantity'])
            total_value = quantity * market_price

            allocation_percentage = round(
                total_value / portfolio_value * 100, 2)
            holdings.append({
                "ticker": asset['ticker'],
                "allocation_percentage": allocation_percentage,
            })

        return jsonify(holdings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/deposit", methods=["PUT"])
def deposit():
    payload = request.get_json() or {}
    try:
        amount = float(payload.get("amount", 0))
    except ValueError:
        return jsonify({"error": "Invalid deposit amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    try:
        portfolioService.add_cash_balance(amount)
        new_balance = portfolioService.get_cash_balance()
        return jsonify({
            "message": "Deposit successful",
            "available_balance": new_balance
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/balance", methods=["GET"])
def get_balance():
    balance = portfolioService.get_cash_balance()
    return jsonify({"available_balance": balance}), 200


@portfolio_bp.route("/stock/<string:ticker>", methods=["GET"])
def get_stock_details(ticker):
    details = yfinanceService.getStockDetails(ticker)
    if details is None:
        return jsonify({"error": f"No data for ticker {ticker}"}), 404

    return jsonify(details), 200


@portfolio_bp.route("/snapshot/latest", methods=["GET"])
def get_latest_portfolio_snapshot():
    try:
        snapshot = portfolioService.get_latest_snapshot()
        if not snapshot:
            return jsonify({"message": "No snapshots found"}), 404

        return jsonify(snapshot), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/snapshot/history", methods=["GET"])
def get_snapshot_history():
    try:
        snapshots = portfolioService.get_snapshot_history()
        if not snapshots:
            return jsonify({"message": "No snapshot history found"}), 404
        return jsonify(snapshots), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/chatbot", methods=["POST"])
def chat_with_portfolio_assistant():
    data = request.get_json()
    user_question = data.get("question")

    if not user_question:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    try:
        answer = ask_chatbot(user_question)
        return jsonify({"answer": answer}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
