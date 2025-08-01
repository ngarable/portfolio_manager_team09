from flask import Blueprint, jsonify, request
from app.services import portfolioService
from app.services import yfinanceService

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
                "quantity": asset[2]
            })
        return data
    except Exception as e:
        print(f"Error fetching assets: {e}")
        return []


@portfolio_bp.route("/assets", methods=["GET"])
def get_assets():
    try:
        assets = fetch_assets()
        if not assets:
            return jsonify({"message": "No current assets found"}), 404

        return jsonify(assets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/assets/buy", methods=["POST"])
def buy_asset():
    payload = request.get_json() or {}
    ticker = payload.get("ticker")
    asset_type = payload.get("asset_type")
    quantity = payload.get("quantity")

    if not all([ticker, asset_type, quantity]):
        return jsonify(
            {"error": "Fields 'ticker', 'asset_type' and 'quantity' are required"}
        ), 400

    try:
        order = portfolioService.buy_asset(ticker, asset_type, quantity)
        return jsonify({
            "message": "Buy order placed successfully",
            "order": order
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route("/asset_allocation", methods=["GET"])
def get_asset_allocation():
    try:
        allocation = portfolioService.get_asset_value_allocation()
        return jsonify(allocation), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Blessing..Example use: http://localhost:5000/api/portfolio/portfolio_value


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
        quantity = float(asset[2])
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
    data = request.get_json()  # Parse JSON request body
    ticker_to_sell = data.get('ticker')
    quantity_to_sell = data.get('quantity')

    if not ticker_to_sell or not quantity_to_sell:
        return jsonify({"error": "Missing ticker or quantity in request body"}), 400

    assets = fetch_assets()
    if not assets:
        return jsonify({"error": "No assets found"}), 404

    # check if ticker exists in the portfolio
    asset = next((a for a in assets if a['ticker'] == ticker_to_sell), None)

    if asset:
        current_quantity = int(asset['quantity'])  # convert from string to int
        if current_quantity >= quantity_to_sell:

            asset_batches = portfolioService.get_remaining_asset_batches(
                ticker_to_sell)

            remaining = quantity_to_sell
            total_profit = 0
            market_price = yfinanceService.getMarketPrice(ticker_to_sell)

            if market_price is None:
                return jsonify({"error": "Market price not available"}), 500

            for batch in asset_batches:
                if remaining <= 0:
                    break

                qty_available = batch['remaining_quantity']
                qty_sold = min(remaining, qty_available)

                new_remaining_quantity = qty_available - qty_sold

                portfolioService.update_order_quantity(
                    batch['id'], new_remaining_quantity)

                total_profit += qty_sold * market_price
                remaining -= qty_sold
        else:
            return jsonify({"message": f"Not enough {ticker_to_sell} to sell. Current quantity: {current_quantity}"}), 400
    else:
        return jsonify({"message": f"Asset {ticker_to_sell} not found"}), 400

    available_balance['value'] += total_profit
    portfolioService.sell_asset(
        ticker_to_sell, quantity_to_sell, market_price, asset['asset_type'])

    return jsonify({"message": f"Sold {quantity_to_sell} of {ticker_to_sell}", "profit": total_profit}), 200


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


available_balance = {"value": 10000}


@portfolio_bp.route("/deposit", methods=["PUT"])
def deposit():
    payload = request.get_json()
    amount = payload.get("amount")
    if not amount or float(amount) <= 0:
        return jsonify({"error": "Invalid deposit amount"}), 400

    available_balance["value"] += float(amount)
    return jsonify({
        "message": "Deposit successful",
        "available_balance": available_balance["value"]
    }), 200


@portfolio_bp.route("/stock/<string:ticker>", methods=["GET"])
def get_stock_details(ticker):
    details = yfinanceService.getStockDetails(ticker)
    if details is None:
        return jsonify({"error": f"No data for ticker {ticker}"}), 404

    return jsonify(details), 200
