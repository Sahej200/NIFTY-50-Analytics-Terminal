# 📈 NIFTY 50 Stock Market Analytics Dashboard

A full-featured analytics dashboard for NIFTY 50 stocks, built with Python and Streamlit. Pulls live/historical NSE data and computes technical + statistical indicators used in real trading and investment analysis — EMA/VWAP crossovers, RSI, rolling volatility, sector performance, and cross-stock correlation.

**Live Demo:** [Add your Streamlit Cloud link here after deploying]

---

## Features

- **Market Overview** — NIFTY 50 index trend, daily advances/declines, top gainers & losers, full market summary table
- **Stock Deep Dive** — candlestick price chart with EMA (9/21) and VWAP overlays, volume chart, RSI with overbought/oversold zones, and plain-language signal interpretation
- **Correlation Analysis** — interactive heatmap of daily-return correlation across up to 50 stocks, with top correlated/inversely correlated pairs highlighted
- **Sector Performance** — average return by sector (IT, Financial Services, FMCG, Energy, etc.) with expandable per-sector breakdowns
- **Volatility Analysis** — 21-day annualized rolling volatility, compare up to 6 stocks side by side

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11+ |
| Data | [yfinance](https://pypi.org/project/yfinance/) (Yahoo Finance API wrapper) |
| Dashboard/UI | Streamlit |
| Visualization | Plotly |
| Data processing | Pandas, NumPy |

## Why This Project

This dashboard was built to demonstrate applied financial data analysis — the same EMA/VWAP-based technical indicators used in intraday trading strategies, extended here into a broader analytics tool covering an entire index. It combines:

- **Quantitative finance concepts** — EMA crossovers, VWAP, RSI, annualized volatility, return correlation
- **Data engineering** — API integration, caching, error handling for unreliable market data
- **Data visualization** — interactive, recruiter/reviewer-friendly dashboards (not just static notebooks)

## Getting Started

### Prerequisites
- Python 3.9 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/nifty50-analytics-dashboard.git
cd nifty50-analytics-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

## Deploying for Free (for your CV/portfolio link)

1. Push this project to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, select your repo, branch, and `app.py` as the entry point.
4. Deploy — you'll get a public URL like `https://your-app-name.streamlit.app` to put directly on your resume/LinkedIn.

## Project Structure

```
nifty50-analytics-dashboard/
├── app.py            # Main Streamlit application (UI + page logic)
├── data_utils.py      # Data fetching (yfinance) + financial calculations
├── config.py          # NIFTY 50 ticker list, sector mapping, constants
├── requirements.txt   # Python dependencies
└── README.md
```

## Possible Extensions

- Add portfolio simulation (track a hypothetical basket of stocks over time)
- Add news sentiment overlay using a financial news API
- Add email/Telegram alerts for RSI overbought/oversold crossovers
- Deploy a backend cache (Redis) to reduce repeated API calls at scale

## Disclaimer

This dashboard is built for educational and informational purposes only. It does not constitute investment advice. Market data may be delayed. Always do your own research before making investment decisions.

---

Built by Sahej — B.Tech CSE (Full Stack), Bennett University
