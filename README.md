# TfL Train Monitor

A real-time train monitoring application for London Overground stations, specifically designed to track trains between Stratford and Clapham Junction.

## Features

- Real-time train arrival information
- Live service status updates
- Configurable station display preferences
- Color-coded arrival times
- Platform information
- Customizable refresh rate

## Stations Monitored

- Kensington Olympia (Northbound to Stratford)
- Highbury & Islington (Southbound to Clapham Junction)

## Requirements

- Python 3.6+
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rodrigojcarrilho/tfl-train-monitor.git
cd tfl-train-monitor
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the monitor:
```bash
python main.py
```

## Display Configuration

Each station can be configured to show specific directions:
- In the `STATIONS` configuration in `main.py`, set `show_northbound` and `show_southbound` to control which directions are displayed for each station.

## Color Coding

- 🟢 Green: Train arrives in more than 10 minutes
- 🟡 Yellow: Train arrives in 5-10 minutes
- 🔴 Red: Train arrives in less than 5 minutes
- "Due": Train arrives in less than 1 minute

## License

MIT License 