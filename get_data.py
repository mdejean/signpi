#!/usr/bin/python3

import requests
import json
import sys
import argparse

from load_config import config
import subway
import boating
import adsb


def get_data(mode="splash", last_timestamp=0, last_data_length=0):
    retry = False
    if mode == "subway":
        retry = subway.get_data(last_timestamp)
    elif mode == "boating":
        retry = boating.get_data(last_timestamp)
    elif mode == "adsb":
        retry = adsb.get_data(last_timestamp, last_data_length)
    elif mode == "splash":
        pass

    sys.exit(1 if retry else 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get sign data to stdout")
    parser.add_argument(
        "--date",
        "-d",
        default=0,
        type=int,
        help="Last timestamp that data was successfully retrieved",
    )
    parser.add_argument(
        "--length", "-l", default=0, type=int, help="Length of the previous data"
    )
    parser.add_argument(
        "mode", default=config["sign"]["mode"], nargs="?", help="Mode to run in"
    )

    args = parser.parse_args()

    get_data(mode=args.mode, last_timestamp=args.date, last_data_length=args.length)
