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

