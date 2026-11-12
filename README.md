# TfL Train Monitor

Live departure data for a terminal display, dashboard, Home Assistant, or mobile widget.

## Reusable route-data service

The original terminal monitor remains available. The `train_times` package creates a small, stable data layer:

1. **Configuration** — stations and the services that matter to you;
2. **TfL retrieval** — one focused client, with clear errors;
3. **Normalisation** — a compact departure-focused JSON response;
4. **Delivery** — an optional HTTP API that any widget or automation can query.

The first configured route is `kensington_olympia_highbury_islington`, with two boards:

- Kensington Olympia → Highbury & Islington (Mildmay services to Stratford)
- Highbury & Islington → Kensington Olympia (Mildmay services to Clapham Junction)

### Consumer-first response

`GET /v1/routes/kensington_olympia_highbury_islington/departures?limit=3` provides an immediate `next_departure` for each board as well as the `departures` list.

```json
{
  "station_name": "Kensington Olympia",
  "target_station": "Highbury & Islington",
  "next_departure": {
    "expected_departure": "2026-11-12T09:32:00Z",
    "minutes_until_departure": 6,
    "platform": "Platform 2",
    "destination": "Stratford (London) Rail Station",
    "cancelled": null,
    "cancellation_status": "not_reported"
  }
}
```

The TfL arrivals endpoint calls its prediction `expectedArrival`. At the station it functions as the live departure-board prediction, so the public API intentionally presents it as `expected_departure`.

**Cancellation accuracy:** TfL's live response contains active predictions but does not currently include a per-service cancellation flag or a scheduled departure time. For that reason, `cancelled` is `null` and `cancellation_status` is `not_reported` unless an upstream provider explicitly supplies a cancellation value. It never silently reports an unknown service as active. Add a National Rail/Darwin-compatible provider if confirmed cancellations become essential.

### Run the service

```bash
python -m pip install -e .
uvicorn train_times.api:app --host 0.0.0.0 --port 8080
```

- `GET /health`
- `GET /v1/routes`
- `GET /v1/routes/kensington_olympia_highbury_islington/departures?limit=3`

Responses are cached in-process for 15 seconds so multiple widgets do not each call TfL.

### Home Assistant example

Add a REST sensor (replace the host with the machine or container running this service):

```yaml
rest:
  - resource: http://TRAIN_TIMES_HOST:8080/v1/routes/kensington_olympia_highbury_islington/departures?limit=3
    scan_interval: 30
    sensor:
      - name: Kensington Olympia next departure
        unique_id: kensington_olympia_next_departure
        value_template: >
          {{ value_json.boards[0].next_departure.minutes_until_departure
             if value_json.boards[0].next_departure else 'none' }}
        json_attributes:
          - fetched_at
          - boards
```

For an Android widget, query the same URL and display `boards[0].next_departure.expected_departure`, `minutes_until_departure`, and `cancellation_status`. The response structure does not depend on Home Assistant.

To add a journey, create another `RouteDefinition` in `train_times/config.py`; the API and consumer contract stay the same.

## Original terminal monitor

The original display requires the packages in `requirements.txt` and can still be run with:

```bash
python main.py
```
