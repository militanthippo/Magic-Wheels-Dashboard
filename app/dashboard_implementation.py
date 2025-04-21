"""
Dashboard implementation with filters and graphs for GoHighLevel data
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from flask import Flask

# Import the dashboard design
from dashboard_design import DashboardDesign

# Create a class for the dashboard implementation
class DashboardImplementation:
    def __init__(self, data_dir='/home/ubuntu/gohighlevel_dashboard/data'):
        self.data_dir = data_dir
        self.dashboard = DashboardDesign()
        self.setup_data_handlers()
        self.enhance_callbacks()
    
    def setup_data_handlers(self):
        """Set up data loading and processing functions"""
        # These functions will handle loading data from files or API
        
        def load_data(date_range='daily', start_date=None, end_date=None, locations=None):
            """
            Load data from files or API based on filters
            This will be implemented once we have OAuth credentials
            """
            # For now, use the sample data generator
            return self.dashboard.generate_sample_data(date_range, start_date, end_date, locations, 
                                                     ['sold_retail', 'sold_rental', 'lead_response_rate', 'avg_response_time'])
        
        def process_data(raw_data, metrics=None):
            """Process raw data for visualization"""
            # This will be implemented with actual data processing
            # For now, return the sample data as is
            return raw_data
        
        # Add these functions to the dashboard object
        self.dashboard.load_data = load_data
        self.dashboard.process_data = process_data
    
    def enhance_callbacks(self):
        """Enhance dashboard callbacks with additional functionality"""
        
        # Override the update_charts callback to use our data handlers
        @self.dashboard.app.callback(
            [Output("daily-performance-chart", "figure"),
             Output("location-comparison-chart", "figure"),
             Output("trend-analysis-chart", "figure"),
             Output("total-retail", "children"),
             Output("total-rental", "children"),
             Output("avg-response-rate", "children"),
             Output("avg-response-time", "children"),
             Output("daily-summary-text", "children")],
            [Input("apply-filters", "n_clicks")],
            [State("date-range-dropdown", "value"),
             State("date-picker-range", "start_date"),
             State("date-picker-range", "end_date"),
             State("location-dropdown", "value"),
             State("metric-dropdown", "value")]
        )
        def update_charts(n_clicks, date_range, start_date, end_date, locations, metrics):
            # Convert locations to list if it's a string or "all"
            if locations == "all":
                locations = self.dashboard.locations
            elif isinstance(locations, str):
                locations = [locations]
            
            # Load data based on filters
            data = self.dashboard.load_data(date_range, start_date, end_date, locations)
            
            # Process data for visualization
            processed_data = self.dashboard.process_data(data, metrics)
            
            # Create charts
            daily_fig = self.dashboard.create_daily_performance_chart(processed_data)
            comparison_fig = self.dashboard.create_location_comparison_chart(processed_data)
            trend_fig = self.dashboard.create_trend_analysis_chart(processed_data)
            
            # Calculate summary values
            total_retail = f"${processed_data['total_retail']:,.2f}"
            total_rental = f"${processed_data['total_rental']:,.2f}"
            avg_response_rate = f"{processed_data['avg_response_rate']:.1f}%"
            avg_response_time = f"{processed_data['avg_response_time']:.1f} min"
            
            # Generate summary text
            summary_text = self.dashboard.generate_summary_text(processed_data)
            
            return daily_fig, comparison_fig, trend_fig, total_retail, total_rental, avg_response_rate, avg_response_time, summary_text
        
        # Add a callback for data refresh
        @self.dashboard.app.callback(
            Output("last-updated", "children"),
            Input("refresh-data", "n_clicks")
        )
        def refresh_data(n_clicks):
            if n_clicks is None:
                # Initial load
                return f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # This would trigger a data refresh from the API
            # For now, just update the timestamp
            return f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Add a callback for exporting data
        @self.dashboard.app.callback(
            Output("download-data", "data"),
            Input("export-button", "n_clicks"),
            [State("date-range-dropdown", "value"),
             State("date-picker-range", "start_date"),
             State("date-picker-range", "end_date"),
             State("location-dropdown", "value"),
             State("metric-dropdown", "value")]
        )
        def export_data(n_clicks, date_range, start_date, end_date, locations, metrics):
            if n_clicks is None:
                return None
            
            # Convert locations to list if it's a string or "all"
            if locations == "all":
                locations = self.dashboard.locations
            elif isinstance(locations, str):
                locations = [locations]
            
            # Load data based on filters
            data = self.dashboard.load_data(date_range, start_date, end_date, locations)
            
            # Convert to DataFrame for export
            export_data = {}
            for location in data['daily_data'].keys():
                for metric in ['sold_retail', 'sold_rental', 'lead_response_rate', 'avg_response_time']:
                    if metric in metrics:
                        col_name = f"{location}_{metric}"
                        export_data[col_name] = data['daily_data'][location][metric]
            
            df = pd.DataFrame(export_data)
            df['date'] = data['dates']
            
            # Return the data for download
            return dcc.send_data_frame(df.to_csv, "magic_wheels_data.csv")
    
    def enhance_layout(self):
        """Enhance the dashboard layout with additional components"""
        
        # Add a refresh button to the header
        header = self.dashboard.app.layout.children[0]
        refresh_button = html.Button(
            "Refresh Data", 
            id="refresh-data", 
            className="btn btn-outline-primary float-right"
        )
        header.children.insert(1, refresh_button)
        
        # Add an export button to the filters section
        filters_section = self.dashboard.app.layout.children[1].children[0]
        export_button = html.Button(
            "Export Data", 
            id="export-button", 
            className="btn btn-outline-secondary mt-3"
        )
        filters_section.children[1].children.append(export_button)
        
        # Add a download component
        download = dcc.Download(id="download-data")
        self.dashboard.app.layout.children.append(download)
        
        # Add a last updated indicator to the footer
        footer = self.dashboard.app.layout.children[-1]
        footer.children[0] = html.P(
            id="last-updated",
            className="text-center text-muted"
        )
        
        return self.dashboard.app.layout
    
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server"""
        # Enhance the layout before running
        self.dashboard.app.layout = self.enhance_layout()
        
        # Run the server
        self.dashboard.app.run_server(debug=debug, port=port, host='0.0.0.0')


# Create a Flask server for the dashboard
server = Flask(__name__)

@server.route('/')
def index():
    return "GoHighLevel Dashboard Server is running. Access the dashboard at /dashboard"

@server.route('/dashboard')
def dashboard():
    # This would normally render the dashboard, but for now just return a message
    return "Dashboard will be available once OAuth credentials are obtained."

@server.route('/health')
def health():
    return "OK"

# This will be used once we have the actual implementation
if __name__ == "__main__":
    # Check if we should run the dashboard or the server
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # Run the Flask server
        server.run(debug=True, port=8050, host='0.0.0.0')
    else:
        # Run the dashboard
        dashboard = DashboardImplementation()
        dashboard.run_server()
