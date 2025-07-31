from flask import Blueprint, jsonify, request
from app.services import portfolioService

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route("/assets", methods=["GET"])
def get_assets():
    try:
        assets = portfolioService.get_assets()
        if not assets:
            return jsonify({"message": "No current assets found"}), 404

        data = []

        for asset in assets:
            data.append({
                "ticker": asset[0],
                "asset_type": asset[1],
                "quantity": asset[2]
            })

        return jsonify(data), 200
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

 # GET /asset_allocation (returns a percentage for each asset type)

# TODO: DENIS
# POST sell (use fake market price for now) after implementing the yfinanceService, we will get real data
# *have a fake balance for now, ex: available_balance = 10000

# GET /stock_allocation (returns a percentage for each stock in the portfolio)

# LATER
# GET /portfolio_value (returns the total value of the portfolio based on current market prices)

# PUT /deposit (updates the available balance) (later)
