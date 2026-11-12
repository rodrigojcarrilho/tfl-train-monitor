"""Transform TfL's raw arrivals into stable, consumer-friendly route data."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Mapping

from .config import DEFAULT_ROUTES, RouteDefinition, StationBoard
from .tfl import TflApiError, TflClient


class UnknownRouteError(KeyError):
    pass


class RouteService:
    """Provides compact route data and protects TfL from repeated consumers."""

    def __init__(
        self,
        client: TflClient | None = None,
        routes: Mapping[str, RouteDefinition] = DEFAULT_ROUTES,
        cache_seconds: int = 15,
    ):
        self.client = client or TflClient()
        self.routes = routes
        self.cache_seconds = cache_seconds
        self._cache: dict[str, tuple[datetime, dict]] = {}

    def route_ids(self) -> list[str]:
        return sorted(self.routes)

    def departures(self, route_id: str, limit: int = 3) -> dict:
        if route_id not in self.routes:
            raise UnknownRouteError(route_id)
        limit = max(1, min(limit, 10))

        cached = self._cache.get(route_id)
        now = datetime.now(UTC)
        if cached and now - cached[0] < timedelta(seconds=self.cache_seconds):
            return {**cached[1], "cached": True}

        route = self.routes[route_id]
        payload = {
            "route_id": route.route_id,
            "route_name": route.name,
            "fetched_at": now.isoformat(),
            "cached": False,
            "boards": [self._board(board, limit) for board in route.boards],
        }
        self._cache[route_id] = (now, payload)
        return payload

    def _board(self, board: StationBoard, limit: int) -> dict:
        raw_arrivals = self.client.arrivals(board.station_id)
        hints = tuple(hint.casefold() for hint in board.destination_hints)
        unique: dict[str, dict] = {}

        for raw in raw_arrivals:
            if raw.get("lineId") != board.line_id:
                continue
            destination = (raw.get("destinationName") or "").casefold()
            if not any(hint in destination for hint in hints):
                continue
            normalised = self.client.normalise_arrival(raw)
            key = normalised["vehicle_id"] or f'{destination}:{normalised["expected_arrival"]}'
            current = unique.get(key)
            if current is None or normalised["seconds_until"] < current["seconds_until"]:
                unique[key] = normalised

        arrivals = sorted(unique.values(), key=lambda item: item["seconds_until"])[:limit]
        return {
            "station_id": board.station_id,
            "station_name": board.station_name,
            "direction": board.direction,
            "target_station": board.target_station,
            "arrivals": arrivals,
        }
