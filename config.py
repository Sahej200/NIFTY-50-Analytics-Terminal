"""
Configuration file for NIFTY 50 Analytics Dashboard
Contains ticker symbols, sector mappings, and app-wide constants.
"""

# NIFTY 50 constituent stocks with Yahoo Finance ticker suffix (.NS = NSE)
NIFTY50_STOCKS = {
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Financial Services"},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Financial Services"},
    "INFY.NS": {"name": "Infosys", "sector": "IT"},
    "BHARTIARTL.NS": {"name": "Bharti Airtel", "sector": "Telecom"},
    "ITC.NS": {"name": "ITC", "sector": "FMCG"},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Financial Services"},
    "LT.NS": {"name": "Larsen & Toubro", "sector": "Infrastructure"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Financial Services"},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever", "sector": "FMCG"},
    "AXISBANK.NS": {"name": "Axis Bank", "sector": "Financial Services"},
    "BAJFINANCE.NS": {"name": "Bajaj Finance", "sector": "Financial Services"},
    "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Automobile"},
    "SUNPHARMA.NS": {"name": "Sun Pharma", "sector": "Pharma"},
    "TITAN.NS": {"name": "Titan Company", "sector": "Consumer Durables"},
    "ULTRACEMCO.NS": {"name": "UltraTech Cement", "sector": "Cement"},
    "ASIANPAINT.NS": {"name": "Asian Paints", "sector": "Consumer Durables"},
    "NESTLEIND.NS": {"name": "Nestle India", "sector": "FMCG"},
    "WIPRO.NS": {"name": "Wipro", "sector": "IT"},
    "M&M.NS": {"name": "Mahindra & Mahindra", "sector": "Automobile"},
    "NTPC.NS": {"name": "NTPC", "sector": "Energy"},
    "POWERGRID.NS": {"name": "Power Grid Corp", "sector": "Energy"},
    "TATASTEEL.NS": {"name": "Tata Steel", "sector": "Metals"},
    "TATAMOTORS.NS": {"name": "Tata Motors", "sector": "Automobile"},
    "ADANIENT.NS": {"name": "Adani Enterprises", "sector": "Diversified"},
    "JSWSTEEL.NS": {"name": "JSW Steel", "sector": "Metals"},
    "HCLTECH.NS": {"name": "HCL Technologies", "sector": "IT"},
    "ONGC.NS": {"name": "Oil & Natural Gas Corp", "sector": "Energy"},
    "COALINDIA.NS": {"name": "Coal India", "sector": "Energy"},
    "BAJAJFINSV.NS": {"name": "Bajaj Finserv", "sector": "Financial Services"},
    "DRREDDY.NS": {"name": "Dr Reddy's Labs", "sector": "Pharma"},
    "GRASIM.NS": {"name": "Grasim Industries", "sector": "Cement"},
    "INDUSINDBK.NS": {"name": "IndusInd Bank", "sector": "Financial Services"},
    "TECHM.NS": {"name": "Tech Mahindra", "sector": "IT"},
    "HINDALCO.NS": {"name": "Hindalco Industries", "sector": "Metals"},
    "CIPLA.NS": {"name": "Cipla", "sector": "Pharma"},
    "BRITANNIA.NS": {"name": "Britannia Industries", "sector": "FMCG"},
    "EICHERMOT.NS": {"name": "Eicher Motors", "sector": "Automobile"},
    "APOLLOHOSP.NS": {"name": "Apollo Hospitals", "sector": "Healthcare"},
    "DIVISLAB.NS": {"name": "Divi's Laboratories", "sector": "Pharma"},
    "BPCL.NS": {"name": "Bharat Petroleum", "sector": "Energy"},
    "HEROMOTOCO.NS": {"name": "Hero MotoCorp", "sector": "Automobile"},
    "SBILIFE.NS": {"name": "SBI Life Insurance", "sector": "Financial Services"},
    "HDFCLIFE.NS": {"name": "HDFC Life Insurance", "sector": "Financial Services"},
    "SHREECEM.NS": {"name": "Shree Cement", "sector": "Cement"},
    "UPL.NS": {"name": "UPL Limited", "sector": "Chemicals"},
    "TATACONSUM.NS": {"name": "Tata Consumer Products", "sector": "FMCG"},
    "ADANIPORTS.NS": {"name": "Adani Ports", "sector": "Infrastructure"},
    "BAJAJ-AUTO.NS": {"name": "Bajaj Auto", "sector": "Automobile"},
}

NIFTY_INDEX_TICKER = "^NSEI"  # Nifty 50 Index

# Multi-asset market snapshot tickers (Yahoo Finance symbols)
MARKET_ASSETS = {
    "^NSEI": {"label": "NIFTY 50", "format": "index"},
    "^BSESN": {"label": "SENSEX", "format": "index"},
    "^NSEBANK": {"label": "BANK NIFTY", "format": "index"},
    "^INDIAVIX": {"label": "INDIA VIX", "format": "index"},
    "INR=X": {"label": "USD/INR", "format": "currency"},
    "GC=F": {"label": "GOLD (USD/oz)", "format": "commodity"},
    "CL=F": {"label": "CRUDE OIL (USD/bbl)", "format": "commodity"},
}

# App-wide constants
DEFAULT_PERIOD = "6mo"          # default historical lookback
CACHE_TTL_SECONDS = 900         # 15 minutes cache for API calls
EMA_SHORT_WINDOW = 9
EMA_LONG_WINDOW = 21
RSI_WINDOW = 14
VOLATILITY_WINDOW = 21          # rolling window (~1 trading month)

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BOLLINGER_WINDOW = 20
BOLLINGER_STD = 2

# ATR (Average True Range)
ATR_WINDOW = 14

# Color theme (dark mode — modern finance aesthetic)
THEME = {
    "primary": "#F59E0B",
    "positive": "#22C55E",
    "negative": "#EF4444",
    "neutral": "#94A3B8",
    "accent": "#38BDF8",
    "accent2": "#A78BFA",

    "background": "#050A12",
    "card_bg": "#0F172A",
    "grid": "#1E293B",
    "text": "#F8FAFC",
    "border": "#1E293B",
}