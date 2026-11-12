from train_times.config import StationBoard
from train_times.service import RouteService


class FakeClient:
    def arrivals(self, station_id):
        return [
            {
                "vehicleId": "one",
                "lineId": "mildmay",
                "destinationName": "Stratford",
                "timeToStation": 120,
                "expectedArrival": "2026-01-01T12:02:00Z",
                "platformName": "1",
            },
            {
                "vehicleId": "two",
                "lineId": "mildmay",
                "destinationName": "Richmond",
                "timeToStation": 60,
            },
        ]

    @staticmethod
    def normalise_arrival(arrival):
        return {
            "vehicle_id": arrival["vehicleId"],
            "destination": arrival["destinationName"],
            "platform": arrival.get("platformName"),
            "expected_departure": arrival.get("expectedArrival"),
            "minutes_until_departure": arrival["timeToStation"] // 60,
            "seconds_until_departure": arrival["timeToStation"],
            "cancelled": None,
            "cancellation_status": "not_reported",
            "line": arrival["lineId"],
            "fetched_at": "2026-01-01T12:00:00+00:00",
        }


def test_only_matching_destinations_are_returned():
    board = StationBoard("station", "Station", "outbound", "Target", "mildmay", ("stratford",))
    route = type("Route", (), {"route_id": "test", "name": "Test", "boards": (board,)})()
    result = RouteService(client=FakeClient(), routes={"test": route}).departures("test")

    board_result = result["boards"][0]
    assert board_result["next_departure"]["vehicle_id"] == "one"
    assert board_result["next_departure"]["cancellation_status"] == "not_reported"
    assert len(board_result["departures"]) == 1
