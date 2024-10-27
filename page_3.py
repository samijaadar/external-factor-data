from datetime import datetime

import requests
import yfinance as yf
import pandas as pd
import streamlit as st


st.title("Company Financial Health Dashboard")

st.sidebar.header("Query For Financial Data")
ticker = st.sidebar.text_input("Enter Stock Ticker Symbol (e.g., AAPL for Apple)", "AAPL")

start_time = st.sidebar.date_input('Start Date', datetime(2023, 10, 1))
end_time = st.sidebar.date_input('End Date', datetime(2024, 10, 20))

stock_data = yf.download(ticker, start=start_time, end=end_time)
st.dataframe(stock_data)
info = yf.Ticker(ticker).info

profitability = {
    "Gross Profit Margin": info.get("grossMargins"),
    "Operating Profit Margin": info.get("operatingMargins"),
    "Net Profit Margin": info.get("netMargins"),
    "Return on Assets (ROA)": info.get("returnOnAssets"),
    "Return on Equity (ROE)": info.get("returnOnEquity"),
}

liquidity = {
    "Current Ratio": info.get("currentRatio"),
    "Quick Ratio": (info.get("totalCurrentAssets", 0) - info.get("inventory", 0)) / info.get("totalCurrentLiabilities", 1) if info.get("totalCurrentLiabilities") else None,
    "Cash Ratio": info.get("cash", 0) / info.get("totalCurrentLiabilities", 1) if info.get("totalCurrentLiabilities") else None,
}

leverage = {
    "Debt-to-Equity Ratio": info.get("debtToEquity"),
    "Interest Coverage Ratio": info.get("ebit", 0) / info.get("interestExpense", 1) if info.get("interestExpense") else None,
    "Debt Ratio": info.get("totalDebt", 0) / info.get("totalAssets", 1) if info.get("totalAssets") else None,
}

efficiency = {
    "Asset Turnover Ratio": info.get("totalRevenue", 0) / info.get("totalAssets", 1) if info.get("totalAssets") else None,
    "Inventory Turnover": info.get("costOfRevenue", 0) / info.get("inventory", 1) if info.get("inventory") else None,
    "Receivables Turnover": info.get("totalRevenue", 0) / info.get("receivables", 1) if info.get("receivables") else None,
}

market_valuation = {
    "Earnings per Share (EPS)": info.get("trailingEps"),
    "Price-to-Earnings Ratio (P/E)": info.get("trailingPE"),
    "Price-to-Book Ratio (P/B)": info.get("priceToBook"),
}

profitability_df = pd.DataFrame.from_dict(profitability, orient='index', columns=['Value'])
liquidity_df = pd.DataFrame.from_dict(liquidity, orient='index', columns=['Value'])
leverage_df = pd.DataFrame.from_dict(leverage, orient='index', columns=['Value'])
efficiency_df = pd.DataFrame.from_dict(efficiency, orient='index', columns=['Value'])
market_valuation_df = pd.DataFrame.from_dict(market_valuation, orient='index', columns=['Value'])

st.header("Key Financial Metrics")

st.subheader("Profitability Metrics")
st.write(profitability_df)

st.subheader("Liquidity Metrics")
st.write(liquidity_df)

st.subheader("Leverage Metrics")
st.write(leverage_df)

#st.subheader("Efficiency Metrics")
#st.write(efficiency_df)

st.subheader("Market Valuation Metrics")
st.write(market_valuation_df)

st.header("Stock Price")

st.subheader("Adjusted Close Price")
st.line_chart(stock_data['Adj Close'])


