from flask import Blueprint, jsonify, request
from app.services import portfolioService

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


@portfolio_bp.route("/asset_allocation", methods=["GET"])
def get_asset_allocation():
    try:
        assets = portfolioService.get_asset_allocation()
        total = sum(row[1] for row in assets)
        allocation = [
            {
                "asset_type": row[0],
                "percent": round((row[1] / total) * 100, 2)
            }
            for row in assets
        ]
        return jsonify(allocation), 200

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

# TODO: DENIS
# POST sell (use fake market price for now) after implementing the yfinanceService, we will get real data
# *have a fake balance for now, ex: available_balance = 10000

@portfolio_bp.route("/assets/sell", methods=["POST"])
def sell_asset():
    data = request.get_json()  # Parse JSON request body
    ticker_to_sell = data.get('ticker')
    quantity_to_sell = data.get('quantity')

    if not ticker_to_sell or not quantity_to_sell:
        return jsonify({"error": "Missing ticker or quantity in request body"}), 400
    
    # check if ticker exists in the portfolio
    assets = fetch_assets()
    if not assets:
        return jsonify({"error": "No assets found"}), 404
    
    asset = next((a for a in assets if a['ticker'] == ticker_to_sell), None)

    if asset:
        current_quantity = int(asset['quantity'])  # convert from string to int
        if current_quantity >= quantity_to_sell:  # or any target quantity
            
            asset_batches = portfolioService.get_remaining_asset_batches(ticker_to_sell)

            remaining = quantity_to_sell
            total_profit = 0

            for batch in asset_batches:
                if remaining <= 0:
                    break

                qty_available = batch['remaining_quantity']
                qty_sold = min(remaining, qty_available)

                new_remaining_quantity = qty_available - qty_sold

                portfolioService.update_order_quantity(batch['id'], new_remaining_quantity)

                total_profit += qty_sold * 100 # replace by market_price
                remaining -= qty_sold
        else:
            return jsonify({"message": f"Not enough {ticker_to_sell} to sell. Current quantity: {current_quantity}"}), 400
    else:
        return jsonify({"message": f"Asset {ticker_to_sell} not found"}), 400
    
    # TODO: portfolioService.update_available_balance(total_profit) IMPLEMENT BALANCE ****
    portfolioService.sell_asset(ticker_to_sell, quantity_to_sell, 100, asset['asset_type'])  # replace 100 with market_price
    
    return jsonify({"message": f"Sold {quantity_to_sell} of {ticker_to_sell}", "profit" : total_profit}), 200
        

@portfolio_bp.route("/asset_value_allocation", methods=["GET"])
def asset_value_allocation():
    try:
        assets = fetch_assets()
        if not assets:
            return jsonify({"message": "No current assets found"}), 404

        portfolio_value = sum(asset['quantity'] * 100 for asset in assets) 
        # TODO: replace 100 with yfinanceService.getMarketPrice(asset['ticker']) when implemented *********

        if portfolio_value == 0:
            return jsonify({"message": "Total portfolio value is zero."}), 400

        holdings = []

        for asset in assets:
            allocation_percentage = round((asset['quantity'] * 100) / portfolio_value * 100, 2)
             # TODO: replace 100 with yfinanceService.getMarketPrice(asset['ticker']) when implemented **********
            holdings.append({
                "ticker": asset['ticker'],
                "allocation_percentage": allocation_percentage,
            })

        return jsonify(holdings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# LATER
# GET /portfolio_value (returns the total value of the portfolio based on current market prices)

# PUT /deposit (updates the available balance) (later)
