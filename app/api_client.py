"""
GoHighLevel API Client for retrieving data from sub-accounts
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
import pandas as pd
from config import API_KEY, SUB_ACCOUNTS, PIPELINE_STAGES

class GoHighLevelAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.locations = {}  # Will store location_id: location_name mapping
        
    def get_locations(self):
        """Retrieve all locations (sub-accounts) from the agency account"""
        endpoint = f"{self.base_url}/locations"
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            locations_data = response.json().get('locations', [])
            # Create a mapping of location names to their IDs
            self.locations = {loc['name']: loc['id'] for loc in locations_data}
            return self.locations
        else:
            print(f"Error retrieving locations: {response.status_code}")
            print(response.text)
            return {}
    
    def get_pipelines(self, location_id):
        """Retrieve all pipelines for a specific location"""
        endpoint = f"{self.base_url}/locations/{location_id}/pipelines"
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('pipelines', [])
        else:
            print(f"Error retrieving pipelines for location {location_id}: {response.status_code}")
            print(response.text)
            return []
    
    def get_pipeline_stages(self, location_id, pipeline_id):
        """Retrieve all stages for a specific pipeline"""
        endpoint = f"{self.base_url}/locations/{location_id}/pipelines/{pipeline_id}/stages"
        response = requests.get(endpoint, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('stages', [])
        else:
            print(f"Error retrieving stages for pipeline {pipeline_id}: {response.status_code}")
            print(response.text)
            return []
    
    def get_opportunities(self, location_id, pipeline_id, stage_id=None, start_date=None, end_date=None):
        """Retrieve opportunities from a specific pipeline stage"""
        endpoint = f"{self.base_url}/locations/{location_id}/pipelines/{pipeline_id}/opportunities"
        
        params = {}
        if stage_id:
            params['stageId'] = stage_id
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
            
        response = requests.get(endpoint, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json().get('opportunities', [])
        else:
            print(f"Error retrieving opportunities: {response.status_code}")
            print(response.text)
            return []
    
    def get_contacts(self, location_id, start_date=None, end_date=None):
        """Retrieve contacts for a specific location with optional date filtering"""
        endpoint = f"{self.base_url}/locations/{location_id}/contacts"
        
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
            
        response = requests.get(endpoint, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json().get('contacts', [])
        else:
            print(f"Error retrieving contacts: {response.status_code}")
            print(response.text)
            return []
    
    def get_lead_response_metrics(self, location_id, start_date=None, end_date=None):
        """Retrieve lead response metrics for a specific location"""
        # This is a placeholder - actual implementation will depend on how lead response
        # data is structured in GoHighLevel API
        contacts = self.get_contacts(location_id, start_date, end_date)
        
        # Calculate response metrics based on contact data
        # This is simplified and would need to be adjusted based on actual API data structure
        total_leads = len(contacts)
        responded_leads = sum(1 for contact in contacts if contact.get('lastContactedDate'))
        
        response_times = []
        for contact in contacts:
            created = contact.get('createdAt')
            contacted = contact.get('lastContactedDate')
            if created and contacted:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                contacted_dt = datetime.fromisoformat(contacted.replace('Z', '+00:00'))
                response_time = (contacted_dt - created_dt).total_seconds() / 60  # in minutes
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_leads': total_leads,
            'responded_leads': responded_leads,
            'response_rate': (responded_leads / total_leads) if total_leads > 0 else 0,
            'avg_response_time_minutes': avg_response_time
        }
    
    def collect_pipeline_data(self, target_locations=None, target_stages=None, days=30):
        """
        Collect pipeline data for specified locations and stages
        
        Args:
            target_locations: List of location names to collect data from (default: all locations)
            target_stages: List of stage names to collect data from (default: all stages)
            days: Number of days to look back for data (default: 30)
            
        Returns:
            Dictionary with collected data
        """
        if not self.locations:
            self.get_locations()
        
        # Filter locations if specified
        if target_locations:
            location_ids = {name: id for name, id in self.locations.items() if name in target_locations}
        else:
            location_ids = self.locations
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        all_data = {}
        
        for location_name, location_id in location_ids.items():
            print(f"Collecting data for {location_name}...")
            location_data = {
                'sold_retail': [],
                'sold_rental': [],
                'lead_metrics': {}
            }
            
            # Get pipelines for this location
            pipelines = self.get_pipelines(location_id)
            
            for pipeline in pipelines:
                pipeline_id = pipeline['id']
                pipeline_name = pipeline['name']
                
                # Get stages for this pipeline
                stages = self.get_pipeline_stages(location_id, pipeline_id)
                
                # Filter stages if specified
                if target_stages:
                    stages = [s for s in stages if s['name'] in target_stages]
                
                for stage in stages:
                    stage_id = stage['id']
                    stage_name = stage['name']
                    
                    # Get opportunities for this stage
                    opportunities = self.get_opportunities(
                        location_id, 
                        pipeline_id, 
                        stage_id, 
                        start_date_str, 
                        end_date_str
                    )
                    
                    # Store opportunities based on stage name
                    if stage_name == "Sold Retail":
                        location_data['sold_retail'] = opportunities
                    elif stage_name == "Sold Rental":
                        location_data['sold_rental'] = opportunities
            
            # Get lead response metrics
            location_data['lead_metrics'] = self.get_lead_response_metrics(
                location_id, 
                start_date_str, 
                end_date_str
            )
            
            all_data[location_name] = location_data
        
        return all_data
    
    def process_data_for_dashboard(self, raw_data):
        """
        Process raw API data into a format suitable for dashboard visualization
        
        Args:
            raw_data: Dictionary with raw data from collect_pipeline_data
            
        Returns:
            Dictionary with processed data ready for dashboard
        """
        processed_data = {
            'locations': [],
            'daily_totals': {},
            'weekly_totals': {},
            'monthly_totals': {},
            'lead_metrics': {},
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for location_name, location_data in raw_data.items():
            processed_data['locations'].append(location_name)
            
            # Process Sold Retail data
            retail_by_date = {}
            for opp in location_data['sold_retail']:
                # Extract date and monetary value
                date_str = opp.get('closedDate', opp.get('createdAt', '')).split('T')[0]
                value = float(opp.get('monetaryValue', 0))
                
                if date_str in retail_by_date:
                    retail_by_date[date_str] += value
                else:
                    retail_by_date[date_str] = value
            
            # Process Sold Rental data
            rental_by_date = {}
            for opp in location_data['sold_rental']:
                # Extract date and monetary value
                date_str = opp.get('closedDate', opp.get('createdAt', '')).split('T')[0]
                value = float(opp.get('monetaryValue', 0))
                
                if date_str in rental_by_date:
                    rental_by_date[date_str] += value
                else:
                    rental_by_date[date_str] = value
            
            # Store daily totals
            processed_data['daily_totals'][location_name] = {
                'retail': retail_by_date,
                'rental': rental_by_date
            }
            
            # Calculate weekly totals
            weekly_retail = {}
            weekly_rental = {}
            
            for date_str, value in retail_by_date.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                week_num = date_obj.strftime('%Y-W%U')
                
                if week_num in weekly_retail:
                    weekly_retail[week_num] += value
                else:
                    weekly_retail[week_num] = value
            
            for date_str, value in rental_by_date.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                week_num = date_obj.strftime('%Y-W%U')
                
                if week_num in weekly_rental:
                    weekly_rental[week_num] += value
                else:
                    weekly_rental[week_num] = value
            
            processed_data['weekly_totals'][location_name] = {
                'retail': weekly_retail,
                'rental': weekly_rental
            }
            
            # Calculate monthly totals
            monthly_retail = {}
            monthly_rental = {}
            
            for date_str, value in retail_by_date.items():
                month = date_str[:7]  # YYYY-MM format
                
                if month in monthly_retail:
                    monthly_retail[month] += value
                else:
                    monthly_retail[month] = value
            
            for date_str, value in rental_by_date.items():
                month = date_str[:7]  # YYYY-MM format
                
                if month in monthly_rental:
                    monthly_rental[month] += value
                else:
                    monthly_rental[month] = value
            
            processed_data['monthly_totals'][location_name] = {
                'retail': monthly_retail,
                'rental': monthly_rental
            }
            
            # Store lead metrics
            processed_data['lead_metrics'][location_name] = location_data['lead_metrics']
        
        return processed_data
    
    def save_data_to_file(self, data, filename):
        """Save processed data to a JSON file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filename}")
    
    def generate_daily_summary(self, processed_data):
        """Generate a daily summary of performance across all locations"""
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_retail_sales': 0,
            'total_rental_sales': 0,
            'location_performance': {},
            'lead_response': {}
        }
        
        # Get yesterday's date for daily totals
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        for location in processed_data['locations']:
            # Get yesterday's sales
            retail_sales = processed_data['daily_totals'][location]['retail'].get(yesterday, 0)
            rental_sales = processed_data['daily_totals'][location]['rental'].get(yesterday, 0)
            
            # Add to totals
            summary['total_retail_sales'] += retail_sales
            summary['total_rental_sales'] += rental_sales
            
            # Store location performance
            summary['location_performance'][location] = {
                'retail_sales': retail_sales,
                'rental_sales': rental_sales,
                'total_sales': retail_sales + rental_sales
            }
            
            # Store lead response metrics
            summary['lead_response'][location] = processed_data['lead_metrics'][location]
        
        return summary

# Example usage
if __name__ == "__main__":
    api = GoHighLevelAPI(API_KEY)
    raw_data = api.collect_pipeline_data(SUB_ACCOUNTS, PIPELINE_STAGES, days=30)
    processed_data = api.process_data_for_dashboard(raw_data)
    api.save_data_to_file(processed_data, '../data/dashboard_data.json')
    
    # Generate and save daily summary
    daily_summary = api.generate_daily_summary(processed_data)
    api.save_data_to_file(daily_summary, f'../data/daily_summary_{datetime.now().strftime("%Y-%m-%d")}.json')
