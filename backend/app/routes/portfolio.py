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

