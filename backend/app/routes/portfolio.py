from flask import Blueprint, jsonify
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
    
# TODO: CORALIE
# POST buy (use fake market price for now)
# GET /asset_allocation (returns a percentage for each asset type)

# TODO: DENIS
# POST sell (use fake market price for now) after implementing the yfinanceService, we will get real data
# *have a fake balance for now, ex: available_balance = 10000

# GET /stock_allocation (returns a percentage for each stock in the portfolio)

# LATER
# GET /portfolio_value (returns the total value of the portfolio based on current market prices)

# PUT /deposit (updates the available balance) (later)

