from dash import Input, Output, State, html
import math

def register_callbacks(app):
    @app.callback(
        Output("hover-info", "children"),
        Input("stock-chart", "hoverData"),
        State("indicator-history", "data"),
    )

    def display_hover_data(hoverData, indicator_history):
        if not hoverData:
            return "Hover over the chart to see details."

        points = hoverData.get("points", [])
        point = next(
            (item for item in points if item.get("data", {}).get("name") == "Price"),
            points[0] if points else None,
        )
        if point is None:
            return "Hover over the chart to see details."

        x = point.get("x")
        date_key = str(x)[:10] if x is not None else ""
        daily = (indicator_history or {}).get(date_key)
        if daily is None:
            return "No indicator data for this date."

        open_ = daily.get("open")
        high = daily.get("high")
        low = daily.get("low")
        close = daily.get("close")
        volume = daily.get("volume")
        prev_close = daily.get("previous_close")
        hv20 = daily.get("hv20")
        atrp14 = daily.get("atrp14")
        rsi14 = daily.get("rsi14")

        # Open: gap
        open_color = (
            "#28a745" if prev_close is not None and open_ > prev_close
            else "#dc3545" if prev_close is not None and open_ < prev_close
            else "#007bff"
        )
        # Close: bullish/bearish
        close_color = "#28a745" if close > open_ else "#dc3545" if close < open_ else "#6c757d"
        high_color = "#28a745"
        low_color = "#dc3545"

        def display_value(value, suffix=""):
            return f"{value:.2f}{suffix}" if value is not None and math.isfinite(value) else "N/A"

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
            badge("O", display_value(open_), open_color),
            badge("H", display_value(high), high_color),
            badge("L", display_value(low), low_color),
            badge("C", display_value(close), close_color),
            badge("HV20", display_value(hv20, "%"), "#6f42c1"),
            badge("ATRP14", display_value(atrp14, "%"), "#6f42c1"),
            badge("RSI14", display_value(rsi14), "#6f42c1"),
            badge("Vol", f"{volume:,.0f}" if volume is not None else "—", "#17a2b8")
        ]

        return html.Div(badges, style={"display":"flex","flexWrap":"wrap","gap":"6px"})
