"""Optional HTTP API: suitable for Home Assistant REST sensors."""

from fastapi import FastAPI, HTTPException, Query

from .service import RouteService, UnknownRouteError
from .tfl import TflApiError

service = RouteService()
app = FastAPI(title="TfL route data", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/v1/routes")
def routes() -> dict:
    return {"routes": service.route_ids()}


@app.get("/v1/routes/{route_id}/departures")
def departures(route_id: str, limit: int = Query(default=3, ge=1, le=10)) -> dict:
    try:
        return service.departures(route_id, limit)
    except UnknownRouteError:
        raise HTTPException(status_code=404, detail="Unknown route") from None
    except TflApiError:
        raise HTTPException(status_code=502, detail="TfL data is temporarily unavailable") from None
