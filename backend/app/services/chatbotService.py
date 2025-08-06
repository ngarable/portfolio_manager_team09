import os
import re
import openai
from dotenv import load_dotenv
from app.services import portfolioService, yfinanceService

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_history = [
    {
        "role": "system",
        "content": (
            "You are a professional AI financial advisor. "
            "You provide concise, structured, and actionable investment advice based on the user's portfolio, "
            "market trends, and best financial practices.\n\n"
            "Respond ONLY to financial questions. If the question is not finance-related, reply: "
            "'I'm a Financial Advisor powered by AI, and I only answer financial-related questions.'\n\n"
            "If the user says 'Hi' or 'Hello', greet them and introduce yourself.\n\n"
            "**Always format your response clearly using Markdown with:**\n"
            "- Use at most **100 words** total\n"
            "- **Bold** only the key terms\n"
            "- Inline code for figures like `$5125.40`\n"
            "- Paragraphs no more than 2 sentences each\n"
        )
    }
]


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
    context = get_portfolio_context()

    chat_history.append({
        "role": "user",
        "content": f"{context}\n\nUser Question: {user_question}"
    })

    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history,
        temperature=0.3,
    )

    assistant_reply = response.choices[0].message.content.strip()
    assistant_reply = re.sub(r'\n{3,}', '\n\n', assistant_reply)
    words = assistant_reply.split()
    if len(words) > 150:
        assistant_reply = ' '.join(words[:150]) + '…'

    chat_history.append({
        "role": "assistant",
        "content": assistant_reply
    })
    return assistant_reply
