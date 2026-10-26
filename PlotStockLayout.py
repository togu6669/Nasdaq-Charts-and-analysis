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

        dcc.Store(id="ticker-history", storage_type="local", data=["INTC"]),
        dcc.Store(id="indicator-history", storage_type="memory", data={}),

        # --- Controls in one row ---
        html.Div([
            html.Div([
                html.Label("Ticker", style={"fontSize": "11px", "fontFamily": "Arial, Helvetica, sans-serif"}),
                dcc.Dropdown(
                    id="ticker-input",
                    options=[{"label": "INTC", "value": "INTC"}],
                    value="INTC",
                    searchable=True,
                    clearable=False,
                    placeholder="Type or select",
                    style={"width": "130px", "fontSize": "12px", "fontFamily": "Arial, Helvetica, sans-serif"}
                )
            ], style={"display": "flex", "flexDirection": "column", "gap": "3px"}),

            html.Div([
                html.Label("Period", style={"fontSize": "11px", "fontFamily": "Arial, Helvetica, sans-serif"}),
                dcc.Dropdown(
                    id="period-dropdown",
                    options=[{"label": v, "value": k} for k, v in period_options.items()],
                    value="6mo",
                    clearable=False,
                    style={"width": "130px", "fontSize": "12px", "fontFamily": "Arial, Helvetica, sans-serif"}
                )
            ], style={"display": "flex", "flexDirection": "column", "gap": "3px"}),

            html.Div([
                html.Label("Chart Type", style={"fontSize": "11px", "fontFamily": "Arial, Helvetica, sans-serif"}),
                dcc.RadioItems(
                    id="chart-type",
                    options=[
                        {"label": "Candles", "value": "candlestick"},
                        {"label": "Line", "value": "line"}
                    ],
                    value="candlestick",
                    inline=True,
                    style={"fontSize": "12px", "fontFamily": "Arial, Helvetica, sans-serif"}
                )
            ], style={"display": "flex", "flexDirection": "column", "gap": "3px", "padding": "0 4px"}),

            html.Div([
                html.Label("Wilder Days", style={"fontSize": "11px", "fontFamily": "Arial, Helvetica, sans-serif"}),
                dcc.Input(
                    id="wilder-days",
                    type="number",
                    value=14,
                    min=2,
                    max=200,
                    step=1,
                    style={"width": "62px", "height": "26px", "padding": "2px 5px", "fontSize": "12px", "fontFamily": "Arial, Helvetica, sans-serif"}
                )
            ], style={"display": "flex", "flexDirection": "column", "gap": "3px"}),
        ], style={
            "display": "flex",
            "gap": "12px",
            "alignItems": "center",
            "marginBottom": "12px",
            "flexWrap": "wrap",
            "fontFamily": "Arial, Helvetica, sans-serif"
        }),

        # --- Metrics row ---
        html.Div([
            # Row 1: OHLCV dynamic badges
            html.Div(id="hover-info", style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px",
                "marginBottom": "10px"
            }),

            # Row 2: Fundamental metrics (static)
            html.Div(id="fundamental-info", style={
                "display": "none",
                "flexWrap": "wrap",
                "gap": "8px",
                "marginBottom": "7px"
            }),

            # Row 3: Profit metrics (static)
            html.Div(id="profit-info", style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px",
                "marginBottom": "7px"
            }),

            # Row 4: Mean-reversion entry signal (always visible)
            html.Div(id="signal-info", style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px",
                "alignItems": "center",
                "marginBottom": "10px"
            })
        ], style={
            "padding": "7px",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "backgroundColor": "white",
            "fontFamily": "Arial, Helvetica, sans-serif"
        }),

        # --- Chart ---
        dcc.Graph(
            id="stock-chart",
            clear_on_unhover=True,  # removes stale info
            config={"displayModeBar": True}
        )
    ], style={"fontFamily": "Arial, Helvetica, sans-serif", "fontSize": "12px"})
