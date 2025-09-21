from dash import Input, Output, html

def register_callbacks(app):
    @app.callback(
        Output("hover-info", "children"),
        Input("stock-chart", "hoverData")
    )

    def display_hover_data(hoverData):
        if not hoverData:
            return "Hover over the chart to see details."

        point = hoverData["points"][0]
        x = point["x"]
        open_, high, low, close = point.get("open"), point.get("high"), point.get("low"), point.get("close")
        volume = point.get("y") if point["data"]["name"]=="Volume" else None
        custom = point.get("customdata")
        prev_close = custom[2] if custom is not None else close

        # Open: gap
        open_color = "#28a745" if open_ > prev_close else "#dc3545" if open_ < prev_close else "#007bff"
        # Close: bullish/bearish
        close_color = "#28a745" if close > open_ else "#dc3545" if close < open_ else "#6c757d"
        # High/Low: new highs/lows
        highs, lows = custom[0], custom[1] if custom is not None else (high, low)
        high_color = "#2ecc71" if high >= max(highs) else "#28a745"
        low_color = "#e74c3c" if low <= min(lows) else "#dc3545"

        # Badge helper
        def badge(label, value, color):
            return html.Span(
                f"{label}: {value}",
                style={
                    "backgroundColor": color,
                    "color": "white",
                    "padding": "4px 8px",
                    "borderRadius": "6px",
                    "marginRight": "6px",
                    "fontSize": "13px",
                    "fontFamily": "Arial, sans-serif",
                    "fontWeight": "bold"
                }
            )

        badges = [
            html.Span(f"📅 {x}", style={"marginRight":"8px", "fontWeight":"bold"}),
            badge("O", f"{open_:.2f}", open_color),
            badge("H", f"{high:.2f}", high_color),
            badge("L", f"{low:.2f}", low_color),
            badge("C", f"{close:.2f}", close_color),
            badge("Vol", f"{volume:,}" if volume else "—", "#17a2b8")
        ]

        return html.Div(badges, style={"display":"flex","flexWrap":"wrap","gap":"6px"})
