"""
Data refresh mechanism for GoHighLevel dashboard
"""

import os
import sys
import time
import json
import logging
import schedule
from datetime import datetime, timedelta
import pandas as pd
import threading

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'refresh.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_refresh')

class DataRefreshManager:
    """Manager for scheduled data refresh operations"""
    
    def __init__(self, data_dir='/home/ubuntu/gohighlevel_dashboard/data', refresh_interval='hourly'):
        """
        Initialize the data refresh manager
        
        Args:
            data_dir: Directory to store data files
            refresh_interval: 'hourly' or 'daily'
        """
        self.data_dir = data_dir
        self.refresh_interval = refresh_interval
        self.running = False
        self.last_refresh = None
        self.scheduler_thread = None
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a status file to track refresh operations
        self.status_file = os.path.join(self.data_dir, 'refresh_status.json')
        self._load_status()
    
    def _load_status(self):
        """Load refresh status from file"""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                self.refresh_interval = status.get('refresh_interval', self.refresh_interval)
                self.last_refresh = status.get('last_refresh')
                logger.info(f"Loaded refresh status: interval={self.refresh_interval}, last_refresh={self.last_refresh}")
            except Exception as e:
                logger.error(f"Error loading refresh status: {e}")
        else:
            self._save_status()
    
    def _save_status(self):
        """Save refresh status to file"""
        status = {
            'refresh_interval': self.refresh_interval,
            'last_refresh': self.last_refresh,
            'updated_at': datetime.now().isoformat()
        }
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
            logger.info(f"Saved refresh status: {status}")
        except Exception as e:
            logger.error(f"Error saving refresh status: {e}")
    
    def set_refresh_interval(self, interval):
        """
        Set the refresh interval
        
        Args:
            interval: 'hourly' or 'daily'
        """
        if interval not in ['hourly', 'daily']:
            raise ValueError("Refresh interval must be 'hourly' or 'daily'")
        
        self.refresh_interval = interval
        self._save_status()
        
        # Reset the schedule
        if self.running:
            self.stop()
            self.start()
        
        logger.info(f"Set refresh interval to {interval}")
    
    def refresh_data(self):
        """
        Refresh data from GoHighLevel API
        This will be implemented once we have OAuth credentials
        """
        try:
            logger.info("Starting data refresh")
            self.last_refresh = datetime.now().isoformat()
            
            # This is where we would call the API client to fetch new data
            # For now, just create a placeholder file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            placeholder_file = os.path.join(self.data_dir, f'refresh_placeholder_{timestamp}.json')
            
            with open(placeholder_file, 'w') as f:
                json.dump({
                    'refresh_time': self.last_refresh,
                    'status': 'placeholder',
                    'message': 'This is a placeholder for actual data refresh. Will be replaced with real implementation once OAuth credentials are obtained.'
                }, f, indent=2)
            
            # Save the status
            self._save_status()
            
            logger.info(f"Data refresh completed at {self.last_refresh}")
            return True
        except Exception as e:
            logger.error(f"Error during data refresh: {e}")
            return False
    
    def start(self):
        """Start the scheduled data refresh"""
        if self.running:
            logger.warning("Data refresh is already running")
            return
        
        # Clear existing schedule
        schedule.clear()
        
        # Set up the schedule based on refresh interval
        if self.refresh_interval == 'hourly':
            schedule.every().hour.do(self.refresh_data)
            logger.info("Scheduled hourly data refresh")
        else:  # daily
            schedule.every().day.at("00:00").do(self.refresh_data)
            logger.info("Scheduled daily data refresh at midnight")
        
        # Run the scheduler in a separate thread
        def run_scheduler():
            self.running = True
            logger.info("Scheduler thread started")
            
            # Run an initial refresh
            self.refresh_data()
            
            while self.running:
                schedule.run_pending()
                time.sleep(1)
            
            logger.info("Scheduler thread stopped")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop the scheduled data refresh"""
        if not self.running:
            logger.warning("Data refresh is not running")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Clear the schedule
        schedule.clear()
        
        logger.info("Stopped data refresh")
    
    def get_status(self):
        """Get the current status of data refresh"""
        return {
            'running': self.running,
            'refresh_interval': self.refresh_interval,
            'last_refresh': self.last_refresh,
            'next_refresh': self._get_next_refresh_time()
        }
    
    def _get_next_refresh_time(self):
        """Get the next scheduled refresh time"""
        if not self.running:
            return None
        
        for job in schedule.jobs:
            return job.next_run.isoformat()
        
        return None
    
    def manual_refresh(self):
        """Manually trigger a data refresh"""
        logger.info("Manual data refresh triggered")
        return self.refresh_data()


# Command-line interface for the data refresh manager
def main():
    """Main function for command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GoHighLevel Dashboard Data Refresh Manager')
    parser.add_argument('--action', choices=['start', 'stop', 'status', 'refresh', 'interval'], required=True,
                        help='Action to perform')
    parser.add_argument('--interval', choices=['hourly', 'daily'],
                        help='Refresh interval (required for interval action)')
    
    args = parser.parse_args()
    
    # Create the data refresh manager
    manager = DataRefreshManager()
    
    if args.action == 'start':
        manager.start()
        print("Data refresh started")
    elif args.action == 'stop':
        manager.stop()
        print("Data refresh stopped")
    elif args.action == 'status':
        status = manager.get_status()
        print(json.dumps(status, indent=2))
    elif args.action == 'refresh':
        success = manager.manual_refresh()
        print(f"Manual refresh {'succeeded' if success else 'failed'}")
    elif args.action == 'interval':
        if not args.interval:
            print("Error: --interval is required for interval action")
            return 1
        
        manager.set_refresh_interval(args.interval)
        print(f"Refresh interval set to {args.interval}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
