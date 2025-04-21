"""
Dashboard design for GoHighLevel Magic Wheels locations
"""

import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
import json
from datetime import datetime, timedelta
import os

# Dashboard layout and structure
class DashboardDesign:
    def __init__(self):
        self.app = dash.Dash(__name__, 
                            external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])
        self.locations = [
            "Magic Wheels Augusta", 
            "Magic Wheels Columbus", 
            "Magic Wheels Greenville", 
            "Magic Wheels Jacksonville", 
            "Magic Wheels Macon", 
            "Magic Wheels Montgomery", 
            "Magic Wheels Mobile", 
            "Magic Wheels Pensacola", 
            "Magic Wheels Savannah"
        ]
        self.metrics = ["Sold Retail", "Sold Rental", "Lead Response Rate", "Avg Response Time"]
        self.date_ranges = ["Daily", "Weekly", "Monthly", "Custom"]
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Set up the dashboard layout with all components"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Magic Wheels Performance Dashboard", className="display-4 text-center"),
                html.P("Data refreshes hourly", className="text-center text-muted"),
                html.Hr()
            ], className="container mt-4"),
            
            # Filters section
            html.Div([
                html.Div([
                    html.H4("Filters", className="mb-3"),
                    html.Div([
                        html.Label("Date Range:"),
                        dcc.Dropdown(
                            id="date-range-dropdown",
                            options=[{"label": dr, "value": dr.lower()} for dr in self.date_ranges],
                            value="daily",
                            className="mb-3"
                        ),
                        html.Div([
                            dcc.DatePickerRange(
                                id="date-picker-range",
                                min_date_allowed=datetime.now() - timedelta(days=365),
                                max_date_allowed=datetime.now(),
                                start_date=datetime.now() - timedelta(days=30),
                                end_date=datetime.now(),
                                display_format="YYYY-MM-DD"
                            )
                        ], id="custom-date-container", style={"display": "none"}),
                        html.Label("Locations:"),
                        dcc.Dropdown(
                            id="location-dropdown",
                            options=[{"label": loc, "value": loc} for loc in self.locations] + 
                                    [{"label": "All Locations", "value": "all"}],
                            value="all",
                            multi=True,
                            className="mb-3"
                        ),
                        html.Label("Metrics:"),
                        dcc.Dropdown(
                            id="metric-dropdown",
                            options=[{"label": m, "value": m.lower().replace(" ", "_")} for m in self.metrics],
                            value=["sold_retail", "sold_rental"],
                            multi=True,
                            className="mb-3"
                        ),
                        html.Button("Apply Filters", id="apply-filters", className="btn btn-primary mt-2")
                    ])
                ], className="col-md-3"),
                
                # Summary cards
                html.Div([
                    html.H4("Performance Summary", className="mb-3"),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H5("Total Sold Retail", className="card-title"),
                                html.H2(id="total-retail", className="card-text text-primary")
                            ], className="card-body")
                        ], className="card mb-3"),
                        html.Div([
                            html.Div([
                                html.H5("Total Sold Rental", className="card-title"),
                                html.H2(id="total-rental", className="card-text text-success")
                            ], className="card-body")
                        ], className="card mb-3"),
                        html.Div([
                            html.Div([
                                html.H5("Avg Lead Response Rate", className="card-title"),
                                html.H2(id="avg-response-rate", className="card-text text-info")
                            ], className="card-body")
                        ], className="card mb-3"),
                        html.Div([
                            html.Div([
                                html.H5("Avg Response Time", className="card-title"),
                                html.H2(id="avg-response-time", className="card-text text-warning")
                            ], className="card-body")
                        ], className="card")
                    ])
                ], className="col-md-9")
            ], className="row container-fluid mt-4"),
            
            # Charts section
            html.Div([
                # Daily totals chart
                html.Div([
                    html.H4("Daily Performance", className="mb-3"),
                    dcc.Graph(id="daily-performance-chart")
                ], className="col-md-12 mt-4"),
                
                # Location comparison chart
                html.Div([
                    html.H4("Location Comparison", className="mb-3"),
                    dcc.Graph(id="location-comparison-chart")
                ], className="col-md-6 mt-4"),
                
                # Trend analysis chart
                html.Div([
                    html.H4("Trend Analysis", className="mb-3"),
                    dcc.Graph(id="trend-analysis-chart")
                ], className="col-md-6 mt-4")
            ], className="row container-fluid"),
            
            # Daily summary section
            html.Div([
                html.H4("Daily Summary Analysis", className="mb-3"),
                html.Div(id="daily-summary-text", className="p-3 border rounded")
            ], className="container mt-4 mb-5"),
            
            # Footer
            html.Footer([
                html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                       className="text-center text-muted")
            ], className="container mt-5 pt-3 border-top")
        ])
    
    def setup_callbacks(self):
        """Set up interactive callbacks for the dashboard"""
        
        # Show/hide custom date picker based on date range selection
        @self.app.callback(
            Output("custom-date-container", "style"),
            Input("date-range-dropdown", "value")
        )
        def toggle_custom_date_picker(date_range):
            if date_range == "custom":
                return {"display": "block"}
            return {"display": "none"}
        
        # Update charts based on filter selections
        @self.app.callback(
            [Output("daily-performance-chart", "figure"),
             Output("location-comparison-chart", "figure"),
             Output("trend-analysis-chart", "figure"),
             Output("total-retail", "children"),
             Output("total-rental", "children"),
             Output("avg-response-rate", "children"),
             Output("avg-response-time", "children"),
             Output("daily-summary-text", "children")],
            [Input("apply-filters", "n_clicks")],
            [dash.dependencies.State("date-range-dropdown", "value"),
             dash.dependencies.State("date-picker-range", "start_date"),
             dash.dependencies.State("date-picker-range", "end_date"),
             dash.dependencies.State("location-dropdown", "value"),
             dash.dependencies.State("metric-dropdown", "value")]
        )
        def update_charts(n_clicks, date_range, start_date, end_date, locations, metrics):
            # This function will be implemented once we have actual data
            # For now, we'll return placeholder figures and values
            
            # Create sample data for demonstration
            sample_data = self.generate_sample_data(date_range, start_date, end_date, locations, metrics)
            
            # Create daily performance chart
            daily_fig = self.create_daily_performance_chart(sample_data)
            
            # Create location comparison chart
            comparison_fig = self.create_location_comparison_chart(sample_data)
            
            # Create trend analysis chart
            trend_fig = self.create_trend_analysis_chart(sample_data)
            
            # Calculate summary values
            total_retail = f"${sample_data['total_retail']:,.2f}"
            total_rental = f"${sample_data['total_rental']:,.2f}"
            avg_response_rate = f"{sample_data['avg_response_rate']:.1f}%"
            avg_response_time = f"{sample_data['avg_response_time']:.1f} min"
            
            # Generate daily summary text
            summary_text = self.generate_summary_text(sample_data)
            
            return daily_fig, comparison_fig, trend_fig, total_retail, total_rental, avg_response_rate, avg_response_time, summary_text
    
    def generate_sample_data(self, date_range, start_date, end_date, locations, metrics):
        """Generate sample data for demonstration purposes"""
        # This will be replaced with actual data retrieval once we have API access
        
        # Convert locations to list if it's a string
        if isinstance(locations, str):
            if locations == "all":
                locations = self.locations
            else:
                locations = [locations]
        
        # Generate date range
        if date_range == "daily":
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        elif date_range == "weekly":
            dates = pd.date_range(end=datetime.now(), periods=12, freq='W')
        elif date_range == "monthly":
            dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        else:  # custom
            dates = pd.date_range(start=start_date, end=end_date)
        
        # Create sample data structure
        data = {
            'dates': dates,
            'daily_data': {},
            'location_data': {},
            'trend_data': {},
            'total_retail': 0,
            'total_rental': 0,
            'avg_response_rate': 0,
            'avg_response_time': 0
        }
        
        # Generate random data for each location
        import random
        
        for location in locations:
            # Daily data
            retail_values = [random.uniform(5000, 15000) for _ in range(len(dates))]
            rental_values = [random.uniform(3000, 10000) for _ in range(len(dates))]
            response_rates = [random.uniform(60, 95) for _ in range(len(dates))]
            response_times = [random.uniform(5, 60) for _ in range(len(dates))]
            
            data['daily_data'][location] = {
                'sold_retail': retail_values,
                'sold_rental': rental_values,
                'lead_response_rate': response_rates,
                'avg_response_time': response_times
            }
            
            # Location summary data
            data['location_data'][location] = {
                'sold_retail': sum(retail_values),
                'sold_rental': sum(rental_values),
                'lead_response_rate': sum(response_rates) / len(response_rates),
                'avg_response_time': sum(response_times) / len(response_times)
            }
            
            # Add to totals
            data['total_retail'] += sum(retail_values)
            data['total_rental'] += sum(rental_values)
        
        # Calculate averages
        num_locations = len(locations)
        data['avg_response_rate'] = sum([data['location_data'][loc]['lead_response_rate'] for loc in locations]) / num_locations
        data['avg_response_time'] = sum([data['location_data'][loc]['avg_response_time'] for loc in locations]) / num_locations
        
        # Generate trend data (simple moving average)
        for location in locations:
            data['trend_data'][location] = {}
            for metric in ['sold_retail', 'sold_rental', 'lead_response_rate', 'avg_response_time']:
                values = data['daily_data'][location][metric]
                # Calculate 7-day moving average
                ma_values = []
                for i in range(len(values)):
                    if i < 7:
                        ma_values.append(sum(values[:i+1]) / (i+1))
                    else:
                        ma_values.append(sum(values[i-6:i+1]) / 7)
                data['trend_data'][location][metric] = ma_values
        
        return data
    
    def create_daily_performance_chart(self, data):
        """Create daily performance chart based on filtered data"""
        # Create figure
        fig = go.Figure()
        
        # Add traces for each location
        for location in data['daily_data'].keys():
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['daily_data'][location]['sold_retail'],
                mode='lines+markers',
                name=f"{location} - Retail"
            ))
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['daily_data'][location]['sold_rental'],
                mode='lines+markers',
                name=f"{location} - Rental"
            ))
        
        # Update layout
        fig.update_layout(
            title="Daily Sales Performance",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            legend_title="Location & Metric",
            height=500
        )
        
        return fig
    
    def create_location_comparison_chart(self, data):
        """Create location comparison chart based on filtered data"""
        # Prepare data for bar chart
        locations = list(data['location_data'].keys())
        retail_values = [data['location_data'][loc]['sold_retail'] for loc in locations]
        rental_values = [data['location_data'][loc]['sold_rental'] for loc in locations]
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(name='Sold Retail', x=locations, y=retail_values),
            go.Bar(name='Sold Rental', x=locations, y=rental_values)
        ])
        
        # Update layout
        fig.update_layout(
            title="Location Sales Comparison",
            xaxis_title="Location",
            yaxis_title="Total Amount ($)",
            barmode='group',
            height=500
        )
        
        return fig
    
    def create_trend_analysis_chart(self, data):
        """Create trend analysis chart based on filtered data"""
        # Create figure
        fig = go.Figure()
        
        # Add traces for each location's trend
        for location in data['trend_data'].keys():
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['trend_data'][location]['sold_retail'],
                mode='lines',
                name=f"{location} - Retail Trend"
            ))
        
        # Update layout
        fig.update_layout(
            title="Sales Trend Analysis (7-day Moving Average)",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            legend_title="Location Trend",
            height=500
        )
        
        return fig
    
    def generate_summary_text(self, data):
        """Generate daily summary analysis text"""
        # Find top performing location
        locations = list(data['location_data'].keys())
        retail_values = [data['location_data'][loc]['sold_retail'] for loc in locations]
        rental_values = [data['location_data'][loc]['sold_rental'] for loc in locations]
        
        top_retail_loc = locations[retail_values.index(max(retail_values))]
        top_rental_loc = locations[rental_values.index(max(rental_values))]
        
        # Find location with best response metrics
        response_rates = [data['location_data'][loc]['lead_response_rate'] for loc in locations]
        response_times = [data['location_data'][loc]['avg_response_time'] for loc in locations]
        
        best_response_rate_loc = locations[response_rates.index(max(response_rates))]
        best_response_time_loc = locations[response_times.index(min(response_times))]
        
        # Generate summary text
        summary = f"""
        <h5>Performance Highlights:</h5>
        <p>During the selected period, <strong>{top_retail_loc}</strong> had the highest retail sales at ${max(retail_values):,.2f}, 
        while <strong>{top_rental_loc}</strong> led in rental sales with ${max(rental_values):,.2f}.</p>
        
        <p>The best lead response rate was achieved by <strong>{best_response_rate_loc}</strong> at {max(response_rates):.1f}%, 
        and <strong>{best_response_time_loc}</strong> had the fastest average response time at {min(response_times):.1f} minutes.</p>
        
        <p>Overall, the combined sales across all locations totaled ${data['total_retail'] + data['total_rental']:,.2f}, 
        with an average lead response rate of {data['avg_response_rate']:.1f}% and average response time of {data['avg_response_time']:.1f} minutes.</p>
        
        <h5>Recommendations:</h5>
        <p>Locations with response times above the average should review their lead management processes to improve efficiency. 
        Consider sharing best practices from {best_response_time_loc} with other locations to improve overall performance.</p>
        """
        
        return html.Div([html.P(i) for i in summary.split('\n') if i.strip()])
    
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port, host='0.0.0.0')


# This will be used once we have the actual implementation
if __name__ == "__main__":
    dashboard = DashboardDesign()
    dashboard.run_server()
