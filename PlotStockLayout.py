from dash import html, dcc

# Periods for dropdown
period_options = {
    "1wk": "1 Week",
    "1mo": "1 Month",
    "6mo": "6 Months",
    "1y": "1 Year",
    "5y": "5 Years",
    "max": "From Beginning"
}

def create_layout():
    return html.Div([
        html.H2("📈 Interactive NASDAQ Stock Viewer with Indicators"),

        # --- Controls in one row ---
        html.Div([
            html.Div([
                html.Label("Ticker"),
                dcc.Input(
                    id="ticker-input",
                    type="text",
                    value="AAPL",
                    debounce=True,
                    placeholder="e.g. AAPL, MSFT, GOOG",
                    style={"width": "120px"}
                )
            ]),

            html.Div([
                html.Label("Period"),
                dcc.Dropdown(
                    id="period-dropdown",
                    options=[{"label": v, "value": k} for k, v in period_options.items()],
                    value="6mo",
                    clearable=False,
                    style={"width": "140px"}
                )
            ]),

            html.Div([
                html.Label("Chart Type"),
                dcc.RadioItems(
                    id="chart-type",
                    options=[
                        {"label": "Candles", "value": "candlestick"},
                        {"label": "Line", "value": "line"}
                    ],
                    value="candlestick",
                    inline=True
                )
            ], style={"padding": "0 15px"}),

            html.Div([
                html.Label("Wilder Days"),
                dcc.Input(
                    id="wilder-days",
                    type="number",
                    value=14,
                    min=2,
                    max=200,
                    step=1,
                    style={"width": "80px"}
                )
            ]),
        ], style={
            "display": "flex",
            "gap": "20px",
            "align-items": "center",
            "margin-bottom": "20px",
            "flex-wrap": "wrap"
        }),

        # --- Metrics row ---
        html.Div(id="fundamental-info", style={
            "display": "flex",
            "gap": "20px",
            "margin-bottom": "20px",
            "flex-wrap": "wrap"
        }),

        # Chart
        dcc.Graph(id="stock-chart")
    ])
