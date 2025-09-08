import yfinance as yf
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Create the Dash app
app = Dash(__name__)

# Available periods
period_options = {
    "1wk": "1 Week",
    "1mo": "1 Month",
    "6mo": "6 Months",
    "1y": "1 Year",
    "5y": "5 Years",
    "max": "From Beginning"
}


def wilder_average(series, n):
    """Calculate Wilder’s Moving Average (RMA)."""
    rma = series.ewm(alpha=1/n, adjust=False).mean()
    return rma


# App layout
app.layout = html.Div([
    html.H2("📈 Interactive NASDAQ Stock Viewer with Indicators"),

    # Ticker input
    html.Div([
        html.Label("Enter Ticker:"),
        dcc.Input(
            id="ticker-input",
            type="text",
            value="AAPL",  # default
            debounce=True,
            placeholder="e.g. AAPL, MSFT, GOOG"
        )
    ], style={"margin-bottom": "10px"}),

    # Period selection
    html.Div([
        html.Label("Select Period:"),
        dcc.Dropdown(
            id="period-dropdown",
            options=[{"label": v, "value": k} for k, v in period_options.items()],
            value="6mo",  # default
            clearable=False
        )
    ], style={"margin-bottom": "10px"}),

    # Chart type selection
    html.Div([
        html.Label("Chart Type:"),
        dcc.RadioItems(
            id="chart-type",
            options=[
                {"label": "Candlestick", "value": "candlestick"},
                {"label": "Line", "value": "line"}
            ],
            value="candlestick",
            inline=True
        )
    ], style={"margin-bottom": "20px"}),

    # Wilder average parameter
    html.Div([
        html.Label("Wilder’s Average Days:"),
        dcc.Input(
            id="wilder-days",
            type="number",
            value=14,  # default RSI-like period
            min=2,
            max=200,
            step=1
        )
    ], style={"margin-bottom": "20px"}),

    # Info cards
    html.Div([
        html.Div(id="fundamental-info", style={
            "display": "flex",
            "gap": "20px",
            "margin-bottom": "20px",
            "font-size": "16px"
        })
    ]),

    # Graph
    dcc.Graph(id="stock-chart")
])


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

    # Main price trace
    if mode == "candlestick":
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name="OHLC"
        ))
    else:  # line mode
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name="Close Price"
        ))

    # Wilder's Average (RMA)
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

    # Volume bars
    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist['Volume'],
        name="Volume",
        yaxis="y2",
        opacity=0.3,
        marker_color="blue"
    ))

    # Layout
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

    # --- Fundamental Data ---
    info = stock.info
    pe_ratio = info.get("trailingPE", "N/A")
    pb_ratio = info.get("priceToBook", "N/A")

    # Disparity Index (last close vs Wilder average)
    disparity = None
    if rma is not None and not rma.dropna().empty:
        disparity = round(hist["Close"].iloc[-1] / rma.iloc[-1] * 100, 2)

    fundamentals = [
        html.Div(f"P/E Ratio: {pe_ratio}"),
        html.Div(f"P/B Ratio: {pb_ratio}"),
        html.Div(f"Disparity ({wilder_days}-day): {disparity}%" if disparity else "Disparity: N/A")
    ]

    return fig, fundamentals


if __name__ == "__main__":
    app.run(debug=True)
