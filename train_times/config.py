"""Route configuration is data, so adding a journey needs no code change."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StationBoard:
    """One live departure board used to describe one leg of a route."""

    station_id: str
    station_name: str
    direction: str
    target_station: str
    line_id: str
    destination_hints: tuple[str, ...]


@dataclass(frozen=True)
class RouteDefinition:
    route_id: str
    name: str
    boards: tuple[StationBoard, ...]


DEFAULT_ROUTES = {
    "kensington_olympia_highbury_islington": RouteDefinition(
        route_id="kensington_olympia_highbury_islington",
        name="Kensington Olympia ↔ Highbury & Islington",
        boards=(
            StationBoard(
                station_id="910GKENOLYM",
                station_name="Kensington Olympia",
                direction="towards_highbury_islington",
                target_station="Highbury & Islington",
                line_id="mildmay",
                # Mildmay trains to Stratford call at Highbury & Islington.
                destination_hints=("stratford",),
            ),
            StationBoard(
                station_id="910GHGHI",
                station_name="Highbury & Islington",
                direction="towards_kensington_olympia",
                target_station="Kensington Olympia",
                line_id="mildmay",
                destination_hints=("clapham junction",),
            ),
        ),
    ),
}
