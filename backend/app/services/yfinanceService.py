# # services/yfinanceService.py

import requests_cache
requests_cache.install_cache('yfinance_cache', expire_after=86400)  # Cache for 1 day

import yfinance as yf

# Fetch current market price
def getMarketPrice(ticker):
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.info.get("regularMarketPrice")
        return current_price
    except Exception as e:
        print(f"Error fetching market price for {ticker}: {e}")
        return None

# Fetch asset type (e.g. stock, etf, mutualfund)
def getAssetType(ticker):
    try:
        stock = yf.Ticker(ticker)
        asset_type = stock.info.get("quoteType")
        return asset_type
    except Exception as e:
        print(f"Error fetching asset type for {ticker}: {e}")
        return None
    

# Fetch sector (e.g., Technology, Healthcare, Real Estate)
def getSector(ticker):
    try:
        stock = yf.Ticker(ticker)
        sector = stock.info.get("sector")  # Example: "Technology"
        return sector
    except Exception as e:
        print(f"Error fetching sector for {ticker}: {e}")
        return None

#Shows how price changed today    
def getPreviousClose(ticker):
    try:
        stock = yf.Ticker(ticker)
        previous_close = stock.info.get("previousClose")
        return previous_close
    except Exception as e:
        print(f"Error fetching previous close for {ticker}: {e}")
        return None

#Returns % gain/loss for today.    
def getPercentageChange(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.info.get("regularMarketPrice")
        prev = stock.info.get("previousClose")
        if price is not None and prev is not None and prev != 0:
            return round((price - prev) / prev * 100, 2)
        return None
    except Exception as e:
        print(f"Error calculating change: {e}")
        return None

 # Gets all stock details at once   
def getStockDetails(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "ticker": ticker,
            "shortName": info.get("shortName"),
            "assetType": info.get("quoteType"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency"),
            "exchange": info.get("exchange"),
            "marketPrice": info.get("regularMarketPrice"),
            "previousClose": info.get("previousClose"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "dividendYield": info.get("dividendYield"),
            "trailingPE": info.get("trailingPE")
        }
    except Exception as e:
        print(f"Error fetching full details: {e}")
        return None    




    

#Testing Code
# if __name__ == "__main__":
#     print("Testing yfinanceService...\n")

#     ticker = "AAPL"
#     # ticker2 = "AMD"

#     price = getMarketPrice(ticker)
#     sector = getSector(ticker)
#     print(f"Market Price of {ticker}: {price}")
#     print(f"Sector of {ticker}: {sector}")


#     price2 = getMarketPrice(ticker2)
#     print(f"Market Price of {ticker2}: {price2}")

#     asset_type = getAssetType(ticker)
#     print(f"Asset Type of {ticker}: {asset_type}")

