from flask import Blueprint, jsonify
from ..db import mysql

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route("/", methods=["GET"])
def get_portfolios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM portfolios")
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "name": row[1]
            })
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
