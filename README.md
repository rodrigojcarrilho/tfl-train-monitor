# TfL Train Monitor

Real-time TfL arrivals, prepared for a terminal display, dashboard, or Home Assistant.

## New: reusable route-data service

The original terminal monitor remains available. The `train_times` package adds a stable data layer that separates:

1. **configuration** — stations and their service/destination filters;
2. **TfL retrieval** — one small client, with explicit errors;
3. **normalisation** — compact JSON without terminal colour codes;
4. **delivery** — an optional HTTP API for Home Assistant or other consumers.

The first configured route is `kensington_olympia_highbury_islington`, providing two boards:

- Kensington Olympia → Highbury & Islington (Mildmay services whose destination is Stratford)
- Highbury & Islington → Kensington Olympia (Mildmay services whose destination is Clapham Junction)

TfL exposes the route's final destination, not a full calling pattern. The configured destination hints correspond to the services that call at the target stations; add a more specific calling-pattern data source later if you need a hard guarantee for an intermediate stop.

### Run the service

```bash
python -m pip install -e .
uvicorn train_times.api:app --host 0.0.0.0 --port 8080
```

- `GET /health`
- `GET /v1/routes`
- `GET /v1/routes/kensington_olympia_highbury_islington/departures?limit=3`

Each departure returns predictable fields such as `minutes_until`, `expected_arrival`, `platform`, `destination`, and `status`. Results are cached in-process for 15 seconds so several dashboards do not each call TfL.

### Home Assistant example

Add a REST sensor (replace the host with the machine/container that runs this service):

```yaml
rest:
  - resource: http://TRAIN_TIMES_HOST:8080/v1/routes/kensington_olympia_highbury_islington/departures?limit=3
    scan_interval: 30
    sensor:
      - name: Kensington Olympia departures
        unique_id: kensington_olympia_departures
        value_template: >
          {{ value_json.boards[0].arrivals[0].minutes_until
             if value_json.boards[0].arrivals else 'none' }}
        json_attributes:
          - fetched_at
          - boards
```

Use the `boards` attribute in a Markdown card, or add template sensors for the opposite direction and individual departure details. To add a new journey, create another `RouteDefinition` in `train_times/config.py`; no API or filtering code should need to change.

## Original terminal monitor

The original display requires the packages in `requirements.txt` and can still be run with:

```bash
python main.py
```
