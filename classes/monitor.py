from datetime import datetime
import pytz
import time
import sys
import requests
from colorama import Fore, Style
from .station import Station
from .display import Display

class Monitor:
    def __init__(self, stations_config, refresh_interval=30, max_trains=3, clapham_only=True):
        self.stations = {
            name: Station(
                name=name,
                station_id=info['id'],
                line=info['line'],
                routes=info['routes'],
                display=info.get('display')
            )
            for name, info in stations_config.items()
        }
        self.refresh_interval = refresh_interval
        self.max_trains = max_trains
        self.clapham_only = clapham_only
        self.display = Display()
        self.london_timezone = pytz.timezone('Europe/London')

    def get_line_status(self, line_id):
        """Get the current status of a TfL line."""
        try:
            response = requests.get(f"https://api.tfl.gov.uk/Line/{line_id}/Status", timeout=10)
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                line_status = data[0].get('lineStatuses', [{}])[0]
                status = line_status.get('statusSeverityDescription', 'Unknown')
                reason = line_status.get('reason', '')
                
                # If there's a reason for disruption, include it in the status
                if reason:
                    return f"{status} - {reason}"
                return status
            return "Status unavailable"
        except requests.exceptions.RequestException as e:
            return "Status unavailable"
        except Exception as e:
            return "Status unavailable"

    def update_display(self):
        """Update the display with current train information."""
        current_time = datetime.now(self.london_timezone).strftime('%H:%M:%S')
        
        self.display.clear_screen()
        self.display.show_header(current_time)
        
        # Show overall line status - use mildmay instead of london-overground
        line_status = self.get_line_status("mildmay")
        status_color = self.display.get_status_color(line_status)
        self.display.show_line_status(line_status, status_color)
        
        self.display.show_color_coding()
        
        # Show each station's information
        for station_name, station in self.stations.items():
            northbound, southbound, result = station.get_arrivals(
                max_trains=self.max_trains,
                clapham_only=self.clapham_only
            )
            
            if isinstance(result, str):  # Error occurred
                self.display.show_error(station_name, result)
                continue
                
            station_status = self.get_line_status(station.line)
            status_color = self.display.get_status_color(station_status)
            
            self.display.show_station_header(station_name, station_status, status_color)
            
            # Only show directions that are enabled for this station
            if station.display["show_northbound"]:
                self.display.show_direction_header("Northbound")
                self.display.show_trains(northbound)
            
            if station.display["show_southbound"]:
                self.display.show_direction_header("Southbound")
                self.display.show_trains(southbound)

    def run(self, stop_event=None):
        """Run the monitor continuously."""
        try:
            while True:
                self.update_display()
                
                if stop_event and stop_event.wait(self.refresh_interval):
                    break
                elif not stop_event:
                    time.sleep(self.refresh_interval)
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped by user.{Style.RESET_ALL}")
            sys.exit(0) 