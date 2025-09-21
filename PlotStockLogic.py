from dash import Input, Output, html
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

def metric_card(label, value, color="#007bff"):
    return html.Div([
        html.Div(label, style={"fontSize": "12px", "color": "gray"}),
        html.Div(value, style={"fontSize": "16px", "fontWeight": "bold", "color": "white"})
    ], style={
        "backgroundColor": color,
        "padding": "6px 12px",
        "borderRadius": "8px",
        "minWidth": "120px",
        "textAlign": "center"
    })

def calc_growth(series):
    if series is not None and len(series) >= 2:
        latest = series.iloc[0]
        prev = series.iloc[1]
        return f"{(latest - prev) / prev * 100:.2f}%"
    return "N/A"

def register_callbacks(app):

    @app.callback(
        Output("stock-chart", "figure"),
        Output("fundamental-info", "children"),
        Output("profit-info", "children"),
        Input("ticker-input", "value"),
        Input("period-dropdown", "value"),
        Input("chart-type", "value"),
        Input("wilder-days", "value"),
    )
    def update_chart(ticker, period, chart_type, wilder_days):
        if not ticker:
            return go.Figure(), [], []

        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return go.Figure(), [], []

        # --- Chart ---
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.67, 0.33],
        )

        # Candlestick / line
        if chart_type == "candlestick":
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price",
                customdata=np.stack([df["High"].values, df["Low"].values, df["Close"].shift(1).values], axis=-1)
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="Price"
            ), row=1, col=1)

        # Wilder
        df["Wilder"] = df["Close"].ewm(span=wilder_days, adjust=False, min_periods=wilder_days).mean()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Wilder"],
            mode="lines",
            name=f"Wilder {wilder_days}d"
        ), row=1, col=1)

        # Volume
        fig.add_trace(go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color="rgba(0,100,200,0.4)"
        ), row=2, col=1)

        fig.update_layout(
            hovermode="x",
            xaxis=dict(showspikes=True, spikemode="across"),
            xaxis2=dict(showspikes=True, spikemode="across"),
            yaxis=dict(title="Price (USD)"),
            yaxis2=dict(title="Volume"),
            template="plotly_white"
        )

        # --- Static metrics ---
        info = stock.info
        pe_ratio = info.get("trailingPE","N/A")
        pb_ratio = info.get("priceToBook","N/A")
        current_ratio = info.get("currentRatio","N/A")
        quick_ratio = info.get("quickRatio","N/A")
        disparity = round(df["Close"].iloc[-1] / df["Wilder"].iloc[-1] * 100, 2) if "Wilder" in df else "N/A"

        fundamental_info = [
            metric_card("P/E Ratio", pe_ratio),
            metric_card("P/B Ratio", pb_ratio),
            metric_card("Disparity", f"{disparity}%"),
            metric_card("Current Ratio", current_ratio),
            metric_card("Quick Ratio", quick_ratio)
        ]

        financials = stock.financials if stock.financials is not None else None
        cashflow = stock.cashflow if stock.cashflow is not None else None
        revenue_growth = calc_growth(financials.loc["Total Revenue"]) if financials is not None and "Total Revenue" in financials.index else "N/A"
        eps_growth = calc_growth(financials.loc["Diluted EPS"]) if financials is not None and "Diluted EPS" in financials.index else "N/A"
        fcf_growth = calc_growth(cashflow.loc["Total Cash From Operating Activities"]) if cashflow is not None and "Total Cash From Operating Activities" in cashflow.index else "N/A"

        profit_info = [
            metric_card("Revenue Growth", revenue_growth),
            metric_card("EPS Growth", eps_growth),
            metric_card("Free Cash Flow Growth", fcf_growth)
        ]

        return fig, fundamental_info, profit_info
