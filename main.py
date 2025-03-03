from colorama import init
from classes import Monitor

# Initialize colorama for Windows support
init()

# Configuration
STATIONS = {
    "Kensington Olympia": {
        "id": "910GKENOLYM",
        "line": "mildmay",
        "routes": {
            "northbound": ["stratford"],
            "southbound": ["clapham junction"]
        },
        "display": {
            "show_northbound": True,
            "show_southbound": False  # Only show northbound for Kensington Olympia
        }
    },
    "Highbury & Islington": {
        "id": "910GHGHI",
        "line": "mildmay",
        "routes": {
            "northbound": ["stratford"],
            "southbound": ["clapham junction"]
        },
        "display": {
            "show_northbound": False,  # Only show southbound for Highbury and Islington
            "show_southbound": True
        }
    }
}

# Constants
REFRESH_INTERVAL = 30  # seconds
MAX_TRAINS = 3
CLAPHAM_ONLY = True

if __name__ == "__main__":
    monitor = Monitor(
        stations_config=STATIONS,
        refresh_interval=REFRESH_INTERVAL,
        max_trains=MAX_TRAINS,
        clapham_only=CLAPHAM_ONLY
    )
    monitor.run()
