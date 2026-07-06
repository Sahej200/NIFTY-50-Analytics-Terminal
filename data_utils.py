"""
Data fetching and financial computation utilities for the NIFTY 50 Dashboard.
Handles yfinance API calls (with caching) and derived metric calculations
such as EMA, VWAP, RSI, volatility, and returns.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st

from config import (
    NIFTY50_STOCKS,
    NIFTY_INDEX_TICKER,
    MARKET_ASSETS,
    CACHE_TTL_SECONDS,
    EMA_SHORT_WINDOW,
    EMA_LONG_WINDOW,
    RSI_WINDOW,
    VOLATILITY_WINDOW,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    BOLLINGER_WINDOW,
    BOLLINGER_STD,
    ATR_WINDOW,
)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical OHLCV data for a single ticker."""
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        if df is None or df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_multiple(tickers: list, period: str = "6mo") -> dict:
    """Fetch historical data for multiple tickers, returned as a dict of DataFrames."""
    result = {}
    for t in tickers:
        df = fetch_history(t, period=period)
        if not df.empty:
            result[t] = df
    return result


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    """Fetch key statistics / info for a single ticker."""
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


def compute_ema(df: pd.DataFrame, short=EMA_SHORT_WINDOW, long=EMA_LONG_WINDOW) -> pd.DataFrame:
    """Add short and long EMA columns to a price DataFrame."""
    out = df.copy()
    out[f"EMA_{short}"] = out["Close"].ewm(span=short, adjust=False).mean()
    out[f"EMA_{long}"] = out["Close"].ewm(span=long, adjust=False).mean()
    return out


def compute_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Add a cumulative VWAP column to a price DataFrame."""
    out = df.copy()
    typical_price = (out["High"] + out["Low"] + out["Close"]) / 3
    cum_vol = out["Volume"].cumsum().replace(0, np.nan)
    out["VWAP"] = (typical_price * out["Volume"]).cumsum() / cum_vol
    return out


def compute_rsi(df: pd.DataFrame, window: int = RSI_WINDOW) -> pd.Series:
    """Compute Relative Strength Index (RSI) for a price series."""
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)  # neutral fill for warm-up period


def compute_rolling_volatility(df: pd.DataFrame, window: int = VOLATILITY_WINDOW) -> pd.Series:
    """Compute annualized rolling volatility from daily returns."""
    daily_returns = df["Close"].pct_change()
    rolling_std = daily_returns.rolling(window=window).std()
    annualized_vol = rolling_std * np.sqrt(252) * 100  # in percent
    return annualized_vol


def compute_period_return(df: pd.DataFrame) -> float:
    """Compute simple percentage return over the full available window."""
    if df.empty or len(df) < 2:
        return np.nan
    start, end = df["Close"].iloc[0], df["Close"].iloc[-1]
    return ((end - start) / start) * 100


def compute_daily_change(df: pd.DataFrame) -> tuple:
    """Return (latest_close, change_value, change_pct) vs previous close."""
    if df.empty or len(df) < 2:
        return (np.nan, np.nan, np.nan)
    latest = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    change = latest - prev
    change_pct = (change / prev) * 100
    return (latest, change, change_pct)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_market_assets(period: str = "1mo") -> dict:
    """Fetch data for the multi-asset market snapshot (indices, forex, commodities)."""
    result = {}
    for ticker in MARKET_ASSETS:
        df = fetch_history(ticker, period=period)
        if not df.empty:
            result[ticker] = df
    return result


def compute_macd(df: pd.DataFrame, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL) -> pd.DataFrame:
    """Add MACD line, signal line, and histogram columns to a price DataFrame."""
    out = df.copy()
    ema_fast = out["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = out["Close"].ewm(span=slow, adjust=False).mean()
    out["MACD"] = ema_fast - ema_slow
    out["MACD_Signal"] = out["MACD"].ewm(span=signal, adjust=False).mean()
    out["MACD_Hist"] = out["MACD"] - out["MACD_Signal"]
    return out


def compute_bollinger_bands(df: pd.DataFrame, window=BOLLINGER_WINDOW, num_std=BOLLINGER_STD) -> pd.DataFrame:
    """Add Bollinger Band columns (middle/upper/lower) to a price DataFrame."""
    out = df.copy()
    mid = out["Close"].rolling(window=window).mean()
    std = out["Close"].rolling(window=window).std()
    out["BB_Middle"] = mid
    out["BB_Upper"] = mid + num_std * std
    out["BB_Lower"] = mid - num_std * std
    return out


def compute_atr(df: pd.DataFrame, window=ATR_WINDOW) -> pd.Series:
    """Compute Average True Range (ATR) — a volatility measure based on price range."""
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()


def compute_fibonacci_levels(df: pd.DataFrame) -> dict:
    """Compute Fibonacci retracement levels from the period's high and low."""
    high = df["Close"].max()
    low = df["Close"].min()
    diff = high - low
    return {
        "0.0% (High)": high,
        "23.6%": high - 0.236 * diff,
        "38.2%": high - 0.382 * diff,
        "50.0%": high - 0.5 * diff,
        "61.8%": high - 0.618 * diff,
        "78.6%": high - 0.786 * diff,
        "100.0% (Low)": low,
    }


def build_returns_matrix(data: dict) -> pd.DataFrame:
    """Build a DataFrame of daily returns for correlation analysis."""
    returns = {}
    for ticker, df in data.items():
        if not df.empty:
            returns[ticker] = df["Close"].pct_change()
    return pd.DataFrame(returns).dropna(how="all")


def build_market_summary(data: dict) -> pd.DataFrame:
    """Build a summary table (name, sector, price, change%, return%, volatility) across stocks."""
    rows = []
    for ticker, df in data.items():
        if df.empty:
            continue
        meta = NIFTY50_STOCKS.get(ticker, {"name": ticker, "sector": "N/A"})
        latest, change, change_pct = compute_daily_change(df)
        period_return = compute_period_return(df)
        vol_series = compute_rolling_volatility(df)
        latest_vol = vol_series.iloc[-1] if not vol_series.empty else np.nan

        rows.append({
            "Ticker": ticker.replace(".NS", ""),
            "Company": meta["name"],
            "Sector": meta["sector"],
            "Price": round(latest, 2) if pd.notna(latest) else None,
            "Change": round(change, 2) if pd.notna(change) else None,
            "Change %": round(change_pct, 2) if pd.notna(change_pct) else None,
            "Period Return %": round(period_return, 2) if pd.notna(period_return) else None,
            "Volatility %": round(latest_vol, 2) if pd.notna(latest_vol) else None,
        })
    return pd.DataFrame(rows)
