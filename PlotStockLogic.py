from dash import Input, Output, html
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

# Signal colours: red flags an entry, green means stand aside.
RED = "#d32f2f"
GREEN = "#2e7d32"
GRAY = "#757575"

# Historical buy signals plotted on the price chart.
SIGNAL_MARKER = "#ff8c00"

def metric_card(label, value, color="#000000"):
    """
    White card with a dark label and a coloured value.

    `color` tints the value text only, so a signal still reads as red or
    green while every card keeps the same white background.
    """
    return html.Div([
        html.Div(label, style={"fontSize": "12px", "color": "#333333"}),
        html.Div(value, style={"fontSize": "16px", "fontWeight": "bold", "color": color})
    ], style={
        "backgroundColor": "white",
        "border": "1px solid #cccccc",
        "padding": "6px 12px",
        "borderRadius": "8px",
        "minWidth": "120px",
        "textAlign": "center"
    })

def rsi(close, window=14):
    """RSI using Wilder-style smoothing. Returns 0-100."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    return 100 - (100 / (1 + avg_gain / avg_loss))


def buy_signal_series(close):
    """
    Flag every bar in `close` that met the buy thresholds.

    Same rule as entry_signal, vectorised over the whole history so the
    signals can be drawn on the chart. Always uses a 14-day Wilder span
    and a 14-day RSI, which is what the thresholds were calibrated on.

    Returns a boolean Series aligned with `close`.
    """
    wilder = close.ewm(span=14, adjust=False, min_periods=14).mean()
    disparity = close / wilder * 100

    return (disparity < 92) & (rsi(close) < 35)


def entry_signal(disparity, rsi_value):
    """
    Classify a mean-reversion long entry from disparity and RSI.

    Thresholds are empirical, measured over 30 large-cap tech names,
    2018-2026 (59,910 daily bars) against a +0.74% 5-day baseline:

        disparity < 88 and RSI < 30   n= 350   +4.49% / 5d   65% win
        disparity < 92 and RSI < 35   n=1444   +2.47% / 5d   61% win

    Both conditions must hold; either one alone is much weaker.
    Returns (label, colour).
    """
    if disparity is None or rsi_value is None:
        return "NO DATA", GRAY

    if np.isnan(disparity) or np.isnan(rsi_value):
        return "NO DATA", GRAY

    if disparity < 88 and rsi_value < 30:
        return "STRONG BUY SIGNAL", RED

    if disparity < 92 and rsi_value < 35:
        return "BUY SIGNAL", RED

    return "NO SIGNAL", GREEN


def calc_growth(series):
    if series is not None and len(series) >= 2:
        latest = series.iloc[0]
        prev = series.iloc[1]
        if prev != 0:
            return f"{(latest - prev) / abs(prev) * 100:.2f}%"
    return "N/A"

def register_callbacks(app):

    @app.callback(
        Output("stock-chart", "figure"),
        Output("fundamental-info", "children"),
        Output("profit-info", "children"),
        Output("signal-info", "children"),
        Input("ticker-input", "value"),
        Input("period-dropdown", "value"),
        Input("chart-type", "value"),
        Input("wilder-days", "value"),
    )
    def update_chart(ticker, period, chart_type, wilder_days):
        if not ticker:
            return go.Figure(), [], [], []

        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return go.Figure(), [], [], []

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

        # Historical buy signals, marked at each bar's low so they sit
        # below the candles instead of covering them.
        buy_signals = buy_signal_series(df["Close"])
        if buy_signals.any():
            signal_days = df[buy_signals]
            fig.add_trace(go.Scatter(
                x=signal_days.index,
                y=signal_days["Low"] * 0.985,
                mode="markers",
                name="Buy signal",
                marker=dict(
                    symbol="triangle-up",
                    size=11,
                    color=SIGNAL_MARKER,
                    line=dict(width=1, color="#b36200"),
                ),
                hovertemplate="Buy signal<br>%{x|%Y-%m-%d}<extra></extra>",
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
        fcf_growth = calc_growth(cashflow.loc["Operating Cash Flow"]) if cashflow is not None and "Operating Cash Flow" in cashflow.index else "N/A"

        profit_info = [
            metric_card("Revenue Growth", revenue_growth),
            metric_card("EPS Growth", eps_growth),
            metric_card("Free Cash Flow Growth", fcf_growth)
        ]

        # --- Entry signal ---
        # The thresholds were calibrated on a 14-day Wilder span, so the
        # signal is always evaluated on 14 regardless of the chart setting.
        wilder14 = df["Close"].ewm(span=14, adjust=False, min_periods=14).mean()
        signal_disparity = df["Close"].iloc[-1] / wilder14.iloc[-1] * 100
        signal_rsi = rsi(df["Close"]).iloc[-1]

        label, color = entry_signal(signal_disparity, signal_rsi)

        # A period shorter than the 14-day window leaves these as NaN.
        disparity_text = "N/A" if np.isnan(signal_disparity) else f"{signal_disparity:.2f}"
        rsi_text = "N/A" if np.isnan(signal_rsi) else f"{signal_rsi:.1f}"

        signal_info = [
            metric_card("Disparity (14d)", disparity_text),
            metric_card("RSI (14d)", rsi_text),
            metric_card("Entry Signal", label, color),
            metric_card(
                "Signals in Period",
                str(int(buy_signals.sum())),
                SIGNAL_MARKER if buy_signals.any() else "#000000",
            ),
            html.Div(
                "buy below 92 / 35, strong below 88 / 30",
                style={"fontSize": "11px", "color": "#333333"}
            )
        ]

        return fig, fundamental_info, profit_info, signal_info
