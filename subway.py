"""
Subway arrival sign layout
"""

from load_config import config
import layout
import requests

import time
import datetime
import csv
import json
import math
import sys
import logging
from PIL import Image, ImageDraw, ImageFont, ImageColor


# from itertools import batched # Python 3.12+
import itertools


def batched(iterable, n, *, strict=False):
    # batched('ABCDEFG', 2) -> AB CD EF G
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


logger = logging.getLogger(__name__)

LINE_HEIGHT = 16
DISPLAY_HEIGHT = int(config["sign"]["display_height"])
DISPLAY_WIDTH = int(config["sign"]["display_width"])

line_heights = [LINE_HEIGHT / 2, DISPLAY_HEIGHT - LINE_HEIGHT / 2 + 1]

BULLET_SIZE = 14
ORDER_WIDTH = 8


def goodservice_trips(station_id):
    headers = {
        "x-application": "signpi",
        "x-api-key": config["subway"].get("api_key", ""),
    }

    trips = []
    try:
        with requests.get(
            f"https://api.subwaynow.app/stops/{station_id}", headers=headers
        ) as req:
            body = req.json()

            #    now = body['timestamp']

            for dir in filter(
                lambda d: d in config["subway"].get("direction"), body["upcoming_trips"]
            ):
                for trip in body["upcoming_trips"][dir]:
                    if config["subway"].get("route") and trip["route_id"] not in config[
                        "subway"
                    ].get("route"):
                        continue
                    route = get_route(trip["route_id"])
                    trips.append(
                        {
                            "route": {
                                "id": trip["route_id"],
                                "short_name": route["route_short_name"],
                                "text_color": route["route_text_color"],
                                "color": route["route_color"],
                                "destination": stop_name(trip["destination_stop"]),
                            },
                            "eta": trip["estimated_current_stop_arrival_time"],
                            "alert": (
                                "delay"
                                if trip["is_delayed"]
                                else "unassigned" if not trip["is_assigned"] else None
                            ),
                        }
                    )
    except ConnectionError:
        pass

    return trips


def transitland_trips(stop_id):
    headers = {
        "x-application": "signpi",
        "apikey": config["subway"].get("api_key", ""),
    }

    trips = []
    try:
        with requests.get(
            f"https://transit.land/api/v2/rest/stops/{stop_id}/departures?limit=8",
            headers=headers,
        ) as req:
            body = req.json()

            for s in body.get("stops", []):
                for t in s["departures"]:
                    route = t["trip"]["route"]
                    destination = t["trip"]["trip_headsign"]

                    if str(t["trip"]["direction_id"]) not in config["subway"].get(
                        "direction"
                    ) or (
                        config["subway"].get("route")
                        and route["route_id"] not in config["subway"].get("route")
                    ):
                        continue

                    # CapMetro includes route and direction
                    destination = (
                        destination.removeprefix(route["route_short_name"] + " ")
                        .removesuffix(" NB")
                        .removesuffix(" SB")
                    )

                    # MTA Bus likes to shout
                    if destination.isupper():
                        destination = destination.title()

                    trips.append(
                        {
                            "route": {
                                "id": route["route_id"],
                                "short_name": route["route_short_name"],
                                "text_color": route["route_text_color"],
                                "color": route["route_color"],
                                "destination": destination,
                            },
                            "eta": datetime.datetime.fromisoformat(
                                t["departure"]["estimated_local"]
                                or t["departure"]["scheduled_local"]
                            ).timestamp(),
                            "alert": (
                                "unassigned"
                                if not t["departure"]["estimated_local"]
                                else None
                            ),
                        }
                    )
    except ConnectionError as e:
        pass

    return trips


def get_data(last_timestamp):
    # Wait until 60 seconds have passed since the last update
    if time.time() - last_timestamp < 60:
        return 1

    trips = []

    for station in config["subway"].get("station").split(","):
        if station.startswith("s-"):
            trips += transitland_trips(station)
        else:
            trips += goodservice_trips(station)

    trips.sort(key=lambda t: t["eta"])

    pages = config["subway"].get("pages")

    # default - show up to 8 trains but less if all routes are covered in less
    if not pages:
        routes = set(t["route"]["id"] for t in trips[:8])
        destinations = set(t["route"]["destination"] for t in trips[:8])
        for pages in range(4):
            if (
                set(t["route"]["id"] for t in trips[: pages * 2]) >= routes
                and set(t["route"]["destination"] for t in trips[: pages * 2])
                >= destinations
            ):
                break
    else:
        pages = int(pages)

    json.dump(
        trips[: min(pages * 2, len(trips))],
        sys.stdout,
    )


_stops = {}


def stop_name(id):
    global _stops
    if not _stops:
        with open("data/stops.txt", "r") as f:
            _stops = {s["stop_id"]: s for s in csv.DictReader(f)}
    return _stops.get(id, {"stop_name": id})["stop_name"]


_routes = {}


def get_route(route_id):
    global _routes
    if not _routes:
        with open("data/routes.txt", "r") as f:
            _routes = {r["route_id"]: r for r in csv.DictReader(f)}

    return _routes.get(route_id, {})


def get_layout():
    trips = json.load(sys.stdin)

    now = time.time()

    if not trips:
        img = layout.new_frame()
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), "No data", anchor="lt")
        # TODO: better no data screen
        return [img], 1

    frames = []
    frame_times = []
    n = 1
    for batch in batched(trips, 2):
        img = layout.new_frame()
        for pos, trip in zip(line_heights, batch):
            draw_trip(
                img,
                pos,
                order=f"{n}.",
                route=trip["route"],
                eta=trip["eta"],
                alert=trip["alert"],
            )
            n += 1
        frames.append(img)
        frame_times.append(10)
    return frames, frame_times


def draw_trip(img, y, order, route, eta, alert):
    order_font = layout.fifteen
    main_font = layout.pokemon
    BULLET_SIZE = 14
    ORDER_WIDTH = 8

    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"  # no antialiasing

    eta_min = round((eta - time.time()) / 60)
    if alert == "delay":  # todo: support yellow/red alert
        eta_text = "Delay"
    elif eta_min > 60:
        logger.info(f'ETA: {eta_min}: {datetime.datetime.fromtimestamp(eta).strftime("%H:%M")}')
        # note that the timezone used is set when creating the image
        eta_text = datetime.datetime.fromtimestamp(eta).strftime("%H:%M")
    else:
        eta_text = f"{eta_min} min"

    # display scheduled trips dimmer
    if alert == "unassigned":
        eta_fill = (128, 128, 128)
    else:
        eta_fill = (255, 255, 255)

    x = 0

    draw.text((x, y), order, font=order_font, anchor="lm", fill=(255, 255, 255))

    x += ORDER_WIDTH

    x += draw_bullet(img, route, (x, y - 1), BULLET_SIZE)

    x += 4  # breathing room

    available_space = (
        DISPLAY_WIDTH
        - x
        - max(
            main_font.getlength("Delay"),
            main_font.getlength("99 min"),
            main_font.getlength("23:59"),
        )
    )

    # this font sucks
    dest = route["destination"].translate({ord("&"): "+", ord("^"): "-"})
    if main_font.getlength(dest) > available_space:
        # TODO: auto-abbreviation
        l = main_font.getlength(dest)
        dest = dest[: (len(dest) * available_space) // l - 1]

    draw.text(
        (x, y),
        text=dest,
        font=main_font,
        anchor="lm",
        fill=(255, 255, 255),
    )

    draw.text(
        (DISPLAY_WIDTH, y), text=eta_text, anchor="rm", font=main_font, fill=eta_fill
    )


def draw_bullet(img, route, pos, diameter):
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    bullet_font = layout.pm
    x, y = pos  # left, middle

    if len(route["color"]) == 6:
        route_color = ImageColor.getrgb(f"#{route['color']}")
    else:
        if route["id"] in ("GS", "FS", "H"):
            route_color = ImageColor.getrgb("#6D6E71")
        else:
            route_color = ImageColor.getrgb("black")

    if len(route["text_color"]) == 6:
        route_text_color = ImageColor.getrgb(f"#{route['text_color']}")
    else:
        if route["id"] in ("N", "Q", "R", "W"):
            route_text_color = ImageColor.getrgb("black")
        else:
            route_text_color = ImageColor.getrgb("white")

    bounds = [
        [x, x + diameter],
        [y - math.floor(diameter / 2), y + math.ceil(diameter / 2)],
    ]

    width = diameter
    if route["id"] in ("FX", "5X", "6X", "7X"):
        # draw diamond
        route_text = route["id"][:1]
        draw.polygon(
            [
                (bounds[0][0] - 1, y),
                (x + diameter // 2, bounds[1][0] - 1),
                (bounds[0][1] + 1, y),
                (x + diameter // 2, bounds[1][1] + 1),
            ],
            fill=route_color,
        )
    elif len(route["short_name"]) > 1:
        # Rectangles (variable width) for buses
        route_text = route["short_name"]
        m = bullet_font.getmetrics()
        height = m[0] - m[1]
        width = math.ceil(bullet_font.getlength(route_text) + 2)

        draw.rectangle(
            [
                (x, y - height // 2 - 1),
                (x + width, y + height // 2 + 1),
            ],
            outline=route_color,
            width=1,
        )
    else:
        # bullet
        route_text = route["short_name"]
        draw.ellipse(
            [(bounds[0][0], bounds[1][0]), (bounds[0][1], bounds[1][1])],
            fill=route_color,
        )

    # middle anchor is broken
    text_width = bullet_font.getlength(route_text)

    draw.text(
        (x + width / 2 - text_width / 2 + 1, y),
        route_text,
        font=bullet_font,
        anchor="lm",
        fill=route_text_color,
    )

    return width
