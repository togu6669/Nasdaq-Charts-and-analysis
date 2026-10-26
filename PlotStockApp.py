from dash import Dash, html, dcc
import PlotStockLayout  # UI components
import PlotStockLogic  # registers logic
import PlotStockDisplayHoverData  # registers hover details

# Create Dash app
app = Dash(__name__)
app.title = "📈 NASDAQ Stock Viewer"

# Set layout from layout.py
app.layout = PlotStockLayout.create_layout()

# Register callbacks
PlotStockLogic.register_callbacks(app)
PlotStockDisplayHoverData.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
