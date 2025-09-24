"""
Subway arrival sign layout
"""

from load_config import config
import layout
import requests

import time
import csv
import json
import math
import sys
from PIL import Image, ImageDraw, ImageFont, ImageColor

LINE_HEIGHT = 16
DISPLAY_HEIGHT = int(config["sign"]["display_height"])
DISPLAY_WIDTH = int(config["sign"]["display_width"])

line_heights = [LINE_HEIGHT / 2, DISPLAY_HEIGHT - LINE_HEIGHT / 2 + 1]

BULLET_SIZE = 14
ORDER_WIDTH = 8


def get_data(last_timestamp):
    headers = {
        "x-application": "signpi",
        "x-api-key": config["subway"].get("api_key", ""),
    }

    # Wait until 60 seconds have passed since the last update
    if time.time() - last_timestamp < 60:
        return 1

    try:
        with requests.get(
            "https://www.goodservice.io/api/stops/" + config["subway"].get("station")
        ) as req:
            body = req.json()

            #    now = body['timestamp']

            # TODO: both directions, filter routes
            trips = body["upcoming_trips"][config["subway"].get("direction", "north")]

            #    for n in range(min(4, len(trips))):
            #        t = trips[n]
            #        eta_min = round((t['estimated_current_stop_arrival_time'] - now) / 60)

            #        print(f"{n}. {t['route_id']} {t['destination_stop']} {eta_min} min")
            json.dump(
                trips[: min(config["subway"].getint("pages", 4), len(trips))],
                sys.stdout,
            )
    except ConnectionError:
        print("[]")
        return 1


_stops = {}


def stop_name(id):
    global _stops
    if not _stops:
        with open("data/stops.txt", "r") as f:
            _stops = {s["stop_id"]: s for s in csv.DictReader(f)}
    return _stops[id]["stop_name"]


_routes = {}


def get_route(route_id):
    global _routes
    if not _routes:
        with open("data/routes.txt", "r") as f:
            _routes = {r["route_id"]: r for r in csv.DictReader(f)}

    return _routes[route_id]


def get_layout():

    trips = json.load(sys.stdin)

    now = time.time()

    if len(trips) < 2 or max(t["timestamp"] for t in trips) < now - 60 * 5:
        img = new_frame()
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), "No data", anchor="lt")
        # TODO: better no data screen
        return [img], 1

    frames = []
    frame_times = []
    for page in range(min(config["subway"].getint("pages", 2), len(trips) // 2)):
        img = layout.new_frame()
        for i in range(page * 2, (page + 1) * 2):
            stop_id = trips[i]["destination_stop"]

            eta_min = round(
                (trips[i]["estimated_current_stop_arrival_time"] - now) / 60
            )
            if eta_min > 99 or trips[i]["is_delayed"]:
                eta = "Delay"
            else:
                eta = f"{eta_min} min"

            draw_trip(
                img,
                line_heights[i % len(line_heights)],
                order=f"{i+1}.",
                route=trips[i]["route_id"],
                dest=stop_name(stop_id),
                dest_short="x",
                eta=eta,
            )
        frames.append(img)
        frame_times.append(10)
    return frames, frame_times


def draw_trip(img, y, order, route, dest, dest_short, eta, eta_fill=(255, 255, 255)):

    order_font = layout.fifteen
    main_font = layout.pokemon

    BULLET_SIZE = 14
    ORDER_WIDTH = 8

    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"  # no antialiasing

    draw.text((0, y), order, font=order_font, anchor="lm", fill=(255, 255, 255))

    draw_bullet(
        img, route, (ORDER_WIDTH + BULLET_SIZE - BULLET_SIZE // 2, y - 1), BULLET_SIZE
    )
    dest_x = ORDER_WIDTH + BULLET_SIZE + 4
    available_space = (
        DISPLAY_WIDTH
        - dest_x
        - max(main_font.getlength("Delay"), main_font.getlength("99 min"))
    )

    draw.text(
        (dest_x, y),
        text=dest if main_font.getlength(dest) < available_space else dest_short,
        font=main_font,
        anchor="lm",
        fill=(255, 255, 255),
    )

    draw.text((DISPLAY_WIDTH, y), text=eta, anchor="rm", font=main_font, fill=eta_fill)


def draw_bullet(img, route_id, center, diameter):
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    bullet_font = layout.pm
    x, y = center

    route = get_route(route_id)
    if len(route["route_color"]) == 6:
        route_color = ImageColor.getrgb(f"#{route['route_color']}")
    else:
        if route_id in ("GS", "FS", "H"):
            route_color = ImageColor.getrgb("#6D6E71")
        else:
            route_color = ImageColor.getrgb("black")

    if len(route["route_text_color"]) == 6:
        route_text_color = ImageColor.getrgb(f"#{route['route_text_color']}")
    else:
        if route_id in ("N", "Q", "R", "W"):
            route_text_color = ImageColor.getrgb("black")
        else:
            route_text_color = ImageColor.getrgb("white")

    bounds = [
        [x - math.floor(diameter / 2), x + math.ceil(diameter / 2)],
        [y - math.floor(diameter / 2), y + math.ceil(diameter / 2)],
    ]

    if route_id in ("FX", "5X", "6X", "7X"):
        # draw diamond
        route_text = route_id[:1]
        draw.polygon(
            [
                (bounds[0][0] - 1, y),
                (x, bounds[1][0] - 1),
                (bounds[0][1] + 1, y),
                (x, bounds[1][1] + 1),
            ],
            fill=route_color,
        )
    else:
        route_text = route["route_short_name"]
        draw.ellipse(
            [(bounds[0][0], bounds[1][0]), (bounds[0][1], bounds[1][1])],
            fill=route_color,
        )

    draw.text(
        (x + 1, y), route_text, font=bullet_font, anchor="mm", fill=route_text_color
    )
