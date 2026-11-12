"""Small, dependency-light TfL API client and normaliser."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests


class TflApiError(RuntimeError):
    """The TfL API could not provide usable departure data."""


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
            raise TflApiError(f"Could not retrieve TfL departures for {station_id}") from exc

        if not isinstance(data, list):
            raise TflApiError(f"Unexpected TfL departure response for {station_id}")
        return data

    @staticmethod
    def normalise_arrival(arrival: dict[str, Any]) -> dict[str, Any]:
        """Map TfL's arrival-shaped prediction to a departure-board contract.

        TfL currently provides active predictions but not a per-service cancellation
        flag.  A missing flag is represented as unknown, never as "not cancelled".
        """
        seconds = max(0, int(arrival.get("timeToStation") or 0))
        raw_cancelled = arrival.get("isCancelled", arrival.get("cancelled"))
        cancelled = bool(raw_cancelled) if raw_cancelled is not None else None
        cancellation_status = (
            "cancelled" if cancelled else "active" if cancelled is False else "not_reported"
        )
        return {
            "vehicle_id": arrival.get("vehicleId"),
            "destination": arrival.get("destinationName") or "Unknown",
            "platform": arrival.get("platformName") or None,
            # TfL names this expectedArrival; it is the live departure-board time
            # presented to consumers for this station.
            "expected_departure": arrival.get("expectedArrival"),
            "minutes_until_departure": seconds // 60,
            "seconds_until_departure": seconds,
            "cancelled": cancelled,
            "cancellation_status": cancellation_status,
            "line": arrival.get("lineId") or arrival.get("lineName"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
