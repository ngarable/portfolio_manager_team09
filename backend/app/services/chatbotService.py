import os
import openai
from dotenv import load_dotenv

from app.services import portfolioService
from app.services import yfinanceService

load_dotenv()


def get_portfolio_context() -> str:
    assets = portfolioService.get_assets()
    if not assets:
        return "The portfolio is currently empty."

    summary_lines = []
    total_value = 0.0

    for ticker, asset_type, avg_price, quantity in assets:
        market_price = yfinanceService.getMarketPrice(ticker) or 0.0
        total_value += float(quantity) * market_price
        summary_lines.append(
            f"{quantity} units of {ticker} ({asset_type}) purchased at an average price of ${avg_price}."
        )

    cash_balance = portfolioService.get_cash_balance()
    net_worth = cash_balance + total_value

    return (
        "Current Portfolio Summary:\n"
        + "\n".join(summary_lines)
        + f"\n\nCash balance: ${cash_balance:.2f}\n"
        + f"Total portfolio value: ${net_worth:.2f}"
    )


def ask_chatbot(user_question: str) -> str:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    context = get_portfolio_context()

    system_prompt = (
        "You are a financial advisor assistant. You give thoughtful and practical investment advice "
        "based on the user's current portfolio, best investment practices, market strategies, and recent financial trends. "
        "If relevant, mention potential risks or better allocation ideas based on the user's holdings."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\nUser Question: {user_question}"}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
