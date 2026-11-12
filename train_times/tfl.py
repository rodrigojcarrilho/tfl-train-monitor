"""Small, dependency-light TfL API client and normaliser."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests


class TflApiError(RuntimeError):
    """The TfL API could not provide usable arrival data."""


class TflClient:
    base_url = "https://api.tfl.gov.uk"

    def __init__(self, session: requests.Session | None = None, timeout_seconds: float = 10.0):
        self.session = session or requests.Session()
        self.timeout_seconds = timeout_seconds

    def arrivals(self, station_id: str) -> list[dict[str, Any]]:
        try:
            response = self.session.get(
                f"{self.base_url}/StopPoint/{station_id}/Arrivals",
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise TflApiError(f"Could not retrieve TfL arrivals for {station_id}") from exc

        if not isinstance(data, list):
            raise TflApiError(f"Unexpected TfL arrival response for {station_id}")
        return data

    @staticmethod
    def normalise_arrival(arrival: dict[str, Any]) -> dict[str, Any]:
        seconds = max(0, int(arrival.get("timeToStation") or 0))
        expected = arrival.get("expectedArrival")
        return {
            "vehicle_id": arrival.get("vehicleId"),
            "destination": arrival.get("destinationName") or "Unknown",
            "platform": arrival.get("platformName") or None,
            "expected_arrival": expected,
            "scheduled_arrival": arrival.get("scheduledTime"),
            "minutes_until": seconds // 60,
            "seconds_until": seconds,
            "status": arrival.get("currentLocation") or "Unknown",
            "line": arrival.get("lineId") or arrival.get("lineName"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
