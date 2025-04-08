from datetime import datetime
import pytz
import requests
from colorama import Fore, Style
import pandas as pd

class Station:
    def __init__(self, name, station_id, line, routes, display=None):
        self.name = name
        self.id = station_id
        self.line = line
        self.routes = routes
        self.display = display or {"show_northbound": True, "show_southbound": True}
        self.london_timezone = pytz.timezone('Europe/London')

    def format_arrival_time(self, iso_time_str):
        """Convert ISO time string to formatted local time."""
        try:
            dt = datetime.fromisoformat(iso_time_str.replace('Z', '+00:00'))
            london_time = dt.astimezone(self.london_timezone)
            return london_time.strftime('%H:%M')
        except (ValueError, AttributeError):
            return "Unknown"

    def process_train_data(self, train):
        """Extract and format relevant information from a train object."""
        time_to_station = train.get("timeToStation", 0) / 60
        
        # Store raw time for sorting
        raw_time = time_to_station
        
        # Format display time
        if time_to_station < 1:
            display_time = "Due"
        else:
            display_time = str(int(time_to_station))  # Round down to integer
        
        # Color code based on arrival time
        time_color = (Fore.GREEN if time_to_station > 10 else 
                     Fore.YELLOW if time_to_station > 5 else 
                     Fore.RED)
        
        return {
            "Expected Arrival": self.format_arrival_time(train.get("expectedArrival", "")),
            "Time to Arrival (mins)": f"{time_color}{display_time}{Style.RESET_ALL}",
            "Platform": train.get("platformName", "Unknown"),
            "Line": train.get("lineName", "Unknown"),
            "Destination": train.get("destinationName", "Unknown"),
            "Status": train.get("currentLocation", "En Route"),
            "_raw_time": raw_time  # Hidden field for sorting
        }

    def get_arrivals(self, max_trains=3, clapham_only=True):
        """Fetch and process arrivals for this station."""
        api_url = f"https://api.tfl.gov.uk/StopPoint/{self.id}/Arrivals"
        
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None, None, None

            # Process data
            northbound_trains = []
            southbound_trains = []

            # Keep track of vehicle IDs to avoid duplicates
            seen_vehicle_ids = set()

            for train in data:
                vehicle_id = train.get("vehicleId")
                
                # Skip if we've already seen this train
                if vehicle_id in seen_vehicle_ids:
                    continue
                
                destination = train.get("destinationName", "").lower()
                train_info = self.process_train_data(train)

                # Check northbound routes
                if any(route in destination for route in self.routes['northbound']):
                    northbound_trains.append(train_info)
                    seen_vehicle_ids.add(vehicle_id)
                # Check southbound routes - filter for Clapham Junction if clapham_only is True
                elif any(route in destination for route in self.routes['southbound']):
                    if not clapham_only or "clapham junction" in destination:
                        southbound_trains.append(train_info)
                        seen_vehicle_ids.add(vehicle_id)

            # Sort and limit results using the raw time
            northbound_trains = sorted(northbound_trains, key=lambda x: x["_raw_time"])[:max_trains]
            southbound_trains = sorted(southbound_trains, key=lambda x: x["_raw_time"])[:max_trains]

            # Remove the _raw_time field before display
            for trains in [northbound_trains, southbound_trains]:
                for train in trains:
                    train.pop("_raw_time", None)

            return northbound_trains, southbound_trains, True

        except requests.exceptions.RequestException as e:
            return None, None, str(e)
        except Exception as e:
            return None, None, str(e) 