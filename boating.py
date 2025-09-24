#!/usr/bin/env python3

from load_config import config
import layout

import requests
import json
import csv
import sys
from datetime import date, timedelta, datetime
from io import StringIO
from PIL import Image, ImageDraw, ImageFont, ImageColor

headers = {"x-application": "signpi", "x-api-key": config["boating"].get("api_key", "")}

weather_station = config["boating"].get("weather_station")
zone = config["boating"].get("zone")
buoy = config["boating"].get("buoy")
tide_station = config["boating"].get("tide_station")
current_station = config["boating"].get("current_station")
current_bin = config["boating"].get("current_bin")
today = date.today()
tomorrow = today + timedelta(days=1)


def get_data(last_timestamp):
    # Wait until 60 seconds have passed since the last update
    if time.time() - last_timestamp < 60:
        return 1
    try:
        with requests.get(
            f"https://api.weather.gov/stations/{weather_station}/observations/latest"
        ) as req:
            weather = req.json()["properties"]["textDescription"]
        with requests.get(
            f"https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/an/{zone.lower()}.txt"
        ) as req:
            forecast = {"advisories": [], "periods": {}}

            # skip lines until one starts with .
            # lines starting with ... are advisories
            # format is .<TIME PERIOD>...<FORECAST>
            s = req.text

            while len(s) > 0:
                t, _, s = s.partition("\n")
                if t.startswith("..."):
                    advisory, _, s = (t[3:] + "\n" + s).partition("...")
                    forecast["advisories"].append(advisory.replace("\n", " ").strip())
                elif t.startswith("."):
                    period, _, rest = t[1:].partition("...")
                    s = rest + "\n" + s
                    period_forecast, _, s = s.partition("\n.")
                    forecast["periods"][period] = period_forecast.replace(
                        "\n", " "
                    ).strip()
                    if len(s) > 0:
                        s = "." + s  # don't lose the period for the next iteration

        with requests.get(
            f"https://www.ndbc.noaa.gov/data/realtime2/{buoy}.txt"
        ) as req:
            (
                yy,
                mm,
                dd,
                hh,
                mi,
                wind_dir,
                wind,
                gust,
                wave_ht,
                wave_dpd,
                wave_apd,
                mwd,
                pressure,
                temp,
                water_temp,
                dew_pt,
                vis,
                ptdy,
                tide,
            ) = req.text.splitlines()[2].split()
        with requests.get(
            f'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&begin_date={today.strftime("%Y%m%d")}&end_date={tomorrow.strftime("%Y%m%d")}&datum=MLLW&station={tide_station}&time_zone=lst_ldt&units=english&interval=hilo&format=json&application=signpi'
        ) as req:
            tides = req.json()

            high_tide = None
            low_tide = None
            for tide in tides["predictions"]:
                time = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
                if time < datetime.now():
                    continue
                if tide["type"] == "H":
                    if high_tide is None:
                        high_tide = time
                if tide["type"] == "L":
                    if low_tide is None:
                        low_tide = time
        with requests.get(
            f'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?station={current_station}&time_zone=LST_LDT&interval=MAX_SLACK&units=english&bin={current_bin}&begin_date={today.strftime("%Y%m%d")}&range=48&product=currents_predictions&format=json'
        ) as req:
            currents = req.json()["current_predictions"]["cp"]
            next_slack = None
            for row in currents:
                time = datetime.strptime(row["Time"], "%Y-%m-%d %H:%M")
                if time < datetime.now() or direction == "slack":
                    direction = row["Type"]
                if (
                    time > datetime.now()
                    and next_slack is None
                    and row["Type"] == "slack"
                ):
                    next_slack = time
        json.dump(
            {
                "weather": weather,
                "temp": temp,
                "high_tide": high_tide,
                "low_tide": low_tide,
                "direction": direction,
                "next_slack": next_slack,
                "wind_dir": wind_dir,
                "wind": wind,
                "gust": gust,
                "forecast": forecast,
            },
            sys.stdout,
        )
    except ConnectionError:
        return 1


def compass(degrees):
    dirs = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    ix = round(float(degrees) / (360.0 / len(dirs)))
    return dirs[ix % len(dirs)]


def mps_to_kt(mps):
    return round(float(mps) / 0.514444)


def c_to_f(c):
    return round(float(c) * 9 / 5 + 32)


def main():
    get_data(0)


def get_layout():
    data = json.load(sys.stdin)
    (
        weather,
        temp,
        high_tide,
        low_tide,
        direction,
        next_slack,
        wind_dir,
        wind,
        gust,
        forecast,
    ) = (
        data["weather"],
        data["temp"],
        data["high_tide"],
        data["low_tide"],
        data["direction"],
        data["next_slack"],
        data["wind_dir"],
        data["wind"],
        data["gust"],
        data["forecast"],
    )

    base = layout.new_frame()

    draw = ImageDraw.Draw(base)
    draw.fontmode = "1"

    now = datetime.now()

    draw.text(
        (0, 0),
        now.strftime("%l:%M%p %a %b %d, %Y").strip(),
        anchor="lt",
        font=layout.font0403,
    )
    draw.text(
        (192, 0), f"{weather} {c_to_f(temp)}  'F", anchor="rt", font=layout.font0403
    )
    draw.text(
        (-1, 6),
        f"High: {high_tide.strftime('%l:%M%p')}",
        anchor="lt",
        font=layout.small,
    )
    draw.text((80 - 1, 6), direction.capitalize(), anchor="lt", font=layout.small)
    draw.text(
        (192, 6),
        f"{compass(wind_dir)} {mps_to_kt(wind)}kt (G{mps_to_kt(gust)}kt)",
        anchor="rt",
        font=layout.small,
    )
    draw.text(
        (0, 14),
        f"Low tide: {low_tide.strftime('%l:%M%p')}",
        anchor="lt",
        font=layout.font0403,
    )
    draw.text(
        (80, 14),
        f"Slack: {next_slack.strftime('%l:%M%p')}",
        anchor="lt",
        font=layout.font0403,
    )

    frames = []
    periods = list(forecast["periods"].keys())[:2]
    for period in periods:
        line = period + ": " + forecast["periods"][period].translate({"\n": " "})
        rest = ""
        while True:
            img = base.copy()
            draw = ImageDraw.Draw(img)
            while layout.font0403.getlength(line) > layout.DISPLAY_WIDTH:
                line, sep, add_rest = line.rpartition(" ")
                rest = sep + add_rest + rest
            draw.text((0, 19), line, font=layout.font0403)
            # line 2
            line = rest
            rest = ""
            while layout.font0403.getlength(line) > layout.DISPLAY_WIDTH:
                line, sep, add_rest = line.rpartition(".")
                rest = sep + add_rest + rest

            if line == "":
                while layout.font0403.getlength(line) > layout.DISPLAY_WIDTH:
                    line, sep, add_rest = line.rpartition(" ")
                    rest = sep + add_rest + rest
            else:
                line += "."
                rest = rest[1:]
            draw.text((0, 25), line.strip(), font=layout.font0403)
            frames.append(img)
            if rest == "":
                break
            line = period + ": " + rest
            rest = ""

    return frames, [5 for _ in frames]


if __name__ == "__main__":
    main()
