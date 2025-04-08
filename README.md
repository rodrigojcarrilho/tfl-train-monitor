# TfL Train Monitor

A real-time train monitoring application for Transport for London (TfL) stations. Currently configured for monitoring trains between Stratford and Clapham Junction on the London Overground, but designed to be adaptable for other routes.

## Current Configuration

This implementation is specifically monitoring:
- Kensington Olympia (Northbound to Stratford)
- Highbury & Islington (Southbound to Clapham Junction)

## Features

- Real-time train arrival information
- Live service status updates
- Configurable station display preferences
- Color-coded arrival times
- Platform information
- Customizable refresh rate

## Requirements

- Python 3.6+
- Required packages listed in `requirements.txt`

## Configuration

### Station Configuration

Stations are configured in `main.py` using the `STATIONS` dictionary. Each station requires:
- `id`: TfL station ID
- `line`: TfL line ID
- `routes`: Dictionary of northbound/southbound destinations
- `display`: Display preferences for each direction

Example configuration:
```python
STATIONS = {
    "Station Name": {
        "id": "STATION_ID",
        "line": "LINE_ID",
        "routes": {
            "northbound": ["destination1", "destination2"],
            "southbound": ["destination3", "destination4"]
        },
        "display": {
            "show_northbound": True,
            "show_southbound": True
        }
    }
}
```

### Adapting for Other Routes

To adapt this monitor for different routes:

1. Find Station IDs:
   - Use the TfL API to find station IDs: `https://api.tfl.gov.uk/StopPoint/Search/{station_name}`
   - Or consult the TfL API documentation: [TfL API Docs](https://api.tfl.gov.uk/swagger/ui/index.html)

2. Update Configuration:
   - Modify the `STATIONS` dictionary in `main.py`
   - Add new stations with their IDs and routes
   - Configure display preferences per station

3. Customize Display:
   - Modify `classes/display.py` for different display formats
   - Update direction headers in `show_direction_header()`
   - Adjust color coding thresholds if needed

## Color Coding

- 🟢 Green: Train arrives in more than 10 minutes
- 🟡 Yellow: Train arrives in 5-10 minutes
- 🔴 Red: Train arrives in less than 5 minutes
- "Due": Train arrives in less than 1 minute
