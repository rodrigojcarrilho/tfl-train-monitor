import os
from colorama import Fore, Style
import pandas as pd

class Display:
    # Default direction configurations
    DIRECTION_CONFIG = {
        "northbound": {
            "arrow": "🔼",
            "default_destination": "Stratford"
        },
        "southbound": {
            "arrow": "🔽",
            "default_destination": "Clapham Junction"
        }
    }

    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def show_header(current_time):
        """Display the monitor header."""
        print(f"{Fore.GREEN}=== TfL Train Monitor - Last Updated: {current_time} ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to exit{Style.RESET_ALL}")

    @staticmethod
    def show_line_status(status, color):
        """Display the line status."""
        print(f"\n{Fore.CYAN}Overall Line Status:{Style.RESET_ALL} {color}{status}{Style.RESET_ALL}")

    @staticmethod
    def show_color_coding():
        """Display the color coding legend."""
        print(f"\nColor coding: {Fore.GREEN}> 10 mins{Style.RESET_ALL}, "
              f"{Fore.YELLOW}5-10 mins{Style.RESET_ALL}, "
              f"{Fore.RED}< 5 mins{Style.RESET_ALL}")

    @staticmethod
    def show_station_header(station_name, line_status, status_color):
        """Display the station header."""
        print(f"\n{Fore.CYAN}=== {station_name} ==={Style.RESET_ALL}")
        print(f"Line Status: {status_color}{line_status}{Style.RESET_ALL}")

    @classmethod
    def show_direction_header(cls, direction, destination=None):
        """Display the direction header with custom destination."""
        direction = direction.lower()
        config = cls.DIRECTION_CONFIG.get(direction, {
            "arrow": "➡️",
            "default_destination": "Unknown"
        })
        
        dest = destination or config["default_destination"]
        print(f"\n{Fore.YELLOW}{config['arrow']} {direction.title()} to {dest}:{Style.RESET_ALL}")

    @staticmethod
    def show_trains(trains):
        """Display the trains for a direction."""
        if trains:
            df = pd.DataFrame(trains)
            print(df.to_string(index=False))
        else:
            print(f"{Fore.RED}No trains scheduled{Style.RESET_ALL}")

    @staticmethod
    def show_error(station_name, error_msg):
        """Display an error message."""
        print(f"{Fore.RED}Error at {station_name}: {error_msg}{Style.RESET_ALL}")

    @staticmethod
    def get_status_color(status):
        """Get the appropriate color for a status."""
        return (Fore.RED if "Part Suspended" in status or "Suspended" in status or "Severe" in status
                else Fore.YELLOW if "Minor" in status or "Special" in status
                else Fore.GREEN if "Good Service" in status
                else Fore.BLUE) 