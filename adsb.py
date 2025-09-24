#!/usr/bin/env python3

from load_config import config
import layout
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import json
import os
import sys
import csv
from PIL import Image, ImageDraw, ImageFont, ImageColor

import requests

LINE_HEIGHT = 16
DISPLAY_HEIGHT = int(config["sign"]["display_height"])
DISPLAY_WIDTH = int(config["sign"]["display_width"])

line_heights = [LINE_HEIGHT / 2, DISPLAY_HEIGHT - LINE_HEIGHT / 2 + 1]


def flightaware_cache(registration):
    assert "/" not in registration

    headers = {"x-application": "signpi", "x-apikey": config["adsb"]["api_key"] or ""}

    try:
        with open(f"/tmp/flightaware/{registration}.json") as f:
            all_flights = json.load(f)

            return next(
                r
                for r in all_flights
                if (
                    r.get("estimated_out", r.get("estimated_off"))
                    < datetime.utcnow().isoformat()
                    and r.get("estimated_in", r.get("estimated_on"))
                    > datetime.utcnow().isoformat()
                )
            )  # throws StopIteration if nothing matches
    except:
        start_date = datetime.utcnow() - timedelta(hours=10)
        end_date = datetime.utcnow() + timedelta(hours=10)
        with requests.get(
            f"https://aeroapi.flightaware.com/aeroapi/flights/{registration}",
            params={
                "ident_type": "registration",
                "start": start_date.isoformat(timespec="seconds"),
                "end": end_date.isoformat(timespec="seconds"),
            },
            headers=headers,
        ) as route_req:
            all_flights = route_req.json()["flights"]
            os.makedirs("/tmp/flightaware", exist_ok=True)
            with open(f"/tmp/flightaware/{registration}.json", "w") as f:
                json.dump(all_flights, f)

            for r in all_flights:
                if (
                    r.get("estimated_out", r.get("estimated_off"))
                    < datetime.utcnow().isoformat()
                    and r.get("estimated_in", r.get("estimated_on"))
                    > datetime.utcnow().isoformat()
                ):
                    return r
            if all_flights:
                return all_flights[len(all_flights) - 1]
            return {}  # todo: actually handle this case?


def get_data(last_timestamp, prev_data_length):
    with requests.get(
        f'https://api.adsb.lol/v2/closest/{config["adsb"]["lat"]}/{config["adsb"]["lon"]}/{config["adsb"]["radius"]}'
    ) as req:
        planes = req.json().get("ac")

        if (
            not planes
            or not planes[0].get("flight")
            or planes[0].get("alt_geom", 0) > config["adsb"].getint("max_altitude")
        ):
            if prev_data_length > 10:
                print("{}")
                return 0  # clear display
            else:
                return 1  # retry

        flight_no = planes[0].get("flight").strip()

        if config["adsb"]["route_api"] == "flightaware":
            # flightaware api, half a cent per request, $5/mo free (1000 requests).
            response = flightaware_cache(planes[0]["r"].strip())

            route_data = {
                "flight_no": flight_no,
                "codeshares": response["codeshares"],
                "operator": response["operator"],
                "aircraft_type": response["aircraft_type"],
                "origin": response["origin"]["code"],
                "origin_tz": response["origin"]["timezone"],
                "destination": response["destination"]["code"],
                "destination_tz": response["destination"]["timezone"],
                "departure_time": response.get("estimated_out")
                or response.get("estimated_off"),
                "departure_delay": response["departure_delay"],
                "arrival_time": response.get("estimated_in")
                or response.get("estimated_on"),
                "arrival_delay": response["arrival_delay"],
            }
        else:
            # free mode, no takeoff/landing times
            with requests.post(
                "https://api.adsb.lol/api/0/routeset",
                json.dumps(
                    {
                        "planes": [
                            {
                                "callsign": flight_no,
                                "lat": config["adsb"]["lat"],
                                "lon": config["adsb"]["lon"],
                            }
                        ]
                    }
                ),
            ) as route_req:
                response = route_req.json()
                if response:
                    route_data = {
                        "flight_no": flight_no,
                        "aircraft_type": planes[0]["t"],  # todo: decode
                        "route": response[0]["airport_codes"],
                        # this gives no info about which is origin/destination
                        # (e.g. airport_codes is  LGA-CLT-LGA), so need to infer from plane direction
                        "operator": response[0]["airline_code"],
                    }
                else:
                    # no flight info
                    route_data = {"flight_no": flight_no}

        output = json.dumps(route_data)

        # if last data was same length as this one (same plane, already on display)
        # then sleep for an estimated time until the plane is out of range and then retry to blank display
        if prev_data_length == len(output):
            # todo: actual calculation instead of hammering api
            return 1
        else:
            print(output)
            return 0


# list from Wikipedia
codeshare_map = {
    "UAL": {
        "brand": "United Express",
        "operators": ["UCA", "GJS", "ASH", "RPA", "SKW"],
    },
    "DAL": {"brand": "Delta Connection", "operators": ["EDV", "RPA", "SKW"]},
    "AAL": {
        "brand": "American Eagle",
        "operators": ["ENY", "PDT", "JIA", "RPA", "SKW"],
    },
    "ACA": {"brand": "Air Canada Express", "operators": ["JZA", "PVL"]},
}


def get_codeshare_operator(operator, codeshares):
    for codeshare in codeshares:
        for parent in codeshare_map:
            if operator in codeshare_map[parent]["operators"] and parent in codeshare:
                return parent


def get_layout():
    base = layout.new_frame()

    draw = ImageDraw.Draw(base)
    draw.fontmode = "1"

    try:
        data = json.load(sys.stdin)
    except:
        data = {}
    if not data:
        return [base], [1]

    with open("data/airlines.csv", "r") as f:
        operators = {l["Code"]: l["Name"] for l in csv.DictReader(f)}

    operator_with_codeshare = get_codeshare_operator(
        data["operator"], data.get("codeshares", [])
    )

    brand = (
        codeshare_map.get(operator_with_codeshare, {}).get("brand")
        or operators.get(data["operator"])
        or data["operator"]
    )

    if data.get("departure_time"):
        departure_time = datetime.fromisoformat(
            data.get("departure_time").replace("Z", "+00:00")
        ).astimezone(ZoneInfo(data.get("origin_tz")))
        arrival_time = datetime.fromisoformat(
            data.get("arrival_time").replace("Z", "+00:00")
        ).astimezone(ZoneInfo(data.get("destination_tz")))

        def format_otp(otp):
            sgn = "-" if otp < 0 else "+"
            min = (abs(otp) // 60) % 60
            hr = (abs(otp) // 60) // 60
            if hr == 0:
                return f"{sgn}{min}m"
            else:
                return f"{sgn}{hr}:{min:0>2}"

        def time_with_otp_and_tz(draw, t, delay, x, y, align="left"):
            font_large = layout.fifteen
            font_small = layout.font0403

            text = t.strftime("%l:%M%p").lower()
            text_width = font_large.getlength(text)

            tz_space = (
                max(
                    layout.font0403.getlength("CEST"),
                    layout.font0403.getlength("-1:00"),
                )
                + 1
            )

            otp_text = format_otp(delay)
            draw.text(
                (x if align == "left" else (x - tz_space), y),
                text,
                anchor="lt" if align == "left" else "rt",
                font=font_large,
            )
            draw.text(
                ((x + text_width + tz_space) if align == "left" else x, y),
                otp_text,
                anchor="rt",
                font=font_small,
                fill=(
                    (0, 192, 0)
                    if delay <= 0
                    else (128, 128, 0) if delay <= 300 else (192, 0, 0)
                ),
            )
            draw.text(
                ((x + text_width + tz_space) if align == "left" else x, y + 9),
                t.tzname(),
                anchor="rt",
                font=font_small,
            )

        time_with_otp_and_tz(
            draw,
            departure_time,
            data.get("departure_delay"),
            0,
            layout.DISPLAY_HEIGHT - 16,
        )

        time_with_otp_and_tz(
            draw,
            arrival_time,
            data.get("arrival_delay"),
            layout.DISPLAY_WIDTH,
            layout.DISPLAY_HEIGHT - 16,
            align="right",
        )

    draw.text(
        (layout.DISPLAY_WIDTH, 0),
        data.get("flight_no"),
        anchor="rt",
        font=layout.small,
    )

    if operator_with_codeshare:
        draw.text(
            (layout.DISPLAY_WIDTH, 8),
            "Op. by " + operators.get(data["operator"]),
            anchor="rt",
            font=layout.font0403,
            fill=(128, 128, 128),
        )

    draw.text(
        (layout.DISPLAY_WIDTH // 2, layout.DISPLAY_HEIGHT - 1),
        data.get("origin") + "  -  " + data.get("destination"),
        anchor="mb",
        font=layout.small,
    )
    try:
        with open(
            "icons/" + (operator_with_codeshare or data["operator"]) + ".png", "rb"
        ) as f:
            logo = Image.open(f)
            base.paste(logo, (0, 0))
            draw.text((17, 3), brand, anchor="lt", font=layout.pokemon)
    except OSError:
        draw.text((1, 3), brand, anchor="lt", font=layout.pokemon)

    return [base], [1]
