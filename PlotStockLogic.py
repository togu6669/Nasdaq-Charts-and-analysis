import yfinance as yf
import plotly.graph_objects as go
from dash import Input, Output, html

def wilder_average(series, n):
    return series.ewm(alpha=1/n, adjust=False).mean()

def metric_card(label, value):
    """Helper to make styled metric cards."""
    return html.Div([
        html.Div(label, style={"font-size": "14px", "color": "gray"}),
        html.Div(value, style={"font-size": "18px", "font-weight": "bold"})
    ], style={
        "border": "1px solid #ddd",
        "border-radius": "10px",
        "padding": "10px 15px",
        "box-shadow": "0 1px 3px rgba(0,0,0,0.1)",
        "min-width": "140px",
        "text-align": "center",
        "background-color": "white"
    })

def calc_growth(series, label):
    """Calculate YoY growth % from yfinance financials series."""
    try:
        if len(series) >= 2:
            latest = series.iloc[0]
            prev = series.iloc[1]
            growth = (latest - prev) / prev * 100
            return f"{growth:.2f}%"
        return "N/A"
    except Exception:
        return "N/A"

def register_callbacks(app):

    @app.callback(
        Output("stock-chart", "figure"),
        Output("fundamental-info", "children"),
        Input("ticker-input", "value"),
        Input("period-dropdown", "value"),
        Input("chart-type", "value"),
        Input("wilder-days", "value"),
    )
    def update_chart(ticker, period, mode, wilder_days):
        if not ticker:
            return go.Figure(), []

        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return go.Figure().update_layout(
                title=f"No data found for {ticker}",
                template="plotly_white"
            ), []

        fig = go.Figure()

        # Main chart
        if mode == "candlestick":
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name="OHLC"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name="Close Price"
            ))

        # Wilder’s average
        rma = None
        if wilder_days and wilder_days > 1:
            rma = wilder_average(hist["Close"], wilder_days)
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=rma,
                mode='lines',
                name=f"Wilder {wilder_days}-day Avg",
                line=dict(color="orange", width=2, dash="dot")
            ))

        # Volume
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name="Volume",
            yaxis="y2",
            opacity=0.3,
            marker_color="blue"
        ))

        fig.update_layout(
            title=f"{ticker.upper()} Stock Price ({period})",
            xaxis=dict(
                rangeslider=dict(visible=True),
                type="date",
                showspikes=True,
                spikemode="across",
                spikesnap="cursor",
            ),
            yaxis=dict(title="Price (USD)", showspikes=True),
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            hovermode="x unified",
            template="plotly_white",
            legend=dict(orientation="h", y=-0.2)
        )

        # Fundamentals
        info = stock.info
        pe_ratio = info.get("trailingPE", "N/A")
        pb_ratio = info.get("priceToBook", "N/A")
        current_ratio = info.get("currentRatio", "N/A")
        quick_ratio = info.get("quickRatio", "N/A")

        disparity = None
        if rma is not None and not rma.dropna().empty:
            disparity = round(hist["Close"].iloc[-1] / rma.iloc[-1] * 100, 2)

        # Growth metrics
        financials = stock.financials
        cashflow = stock.cashflow

        revenue_growth = calc_growth(financials.loc["Total Revenue"], "Revenue") if "Total Revenue" in financials.index else "N/A"
        eps_growth = calc_growth(financials.loc["Diluted EPS"], "EPS") if "Diluted EPS" in financials.index else "N/A"
        fcf_growth = calc_growth(cashflow.loc["Total Cash From Operating Activities"], "Free Cash Flow") if "Total Cash From Operating Activities" in cashflow.index else "N/A"

        # --- Two groups of cards ---
        fundamentals = html.Div([
            html.Div([
                metric_card("P/E Ratio", pe_ratio),
                metric_card("P/B Ratio", pb_ratio),
                metric_card(f"Disparity ({wilder_days}d)", f"{disparity}%" if disparity else "N/A"),
                metric_card("Current Ratio", current_ratio),
                metric_card("Quick Ratio", quick_ratio),
            ], style={
                "display": "flex", "gap": "20px", "flex-wrap": "wrap", "margin-bottom": "20px"
            }),

            html.Div([
                html.H4("Profit Stocks", style={"margin-bottom": "10px"}),
                metric_card("Revenue Growth (YoY)", revenue_growth),
                metric_card("EPS Growth (YoY)", eps_growth),
                metric_card("Free Cash Flow Growth (YoY)", fcf_growth),
            ], style={
                "display": "flex", "gap": "20px", "flex-wrap": "wrap"
            })
        ])

        return fig, fundamentals
