#!/usr/bin/python3
"""
When run, update the wifi configuration from config.ini, otherwise provide the
  values from config.ini in 'config'
"""
import configparser
import os
import logging

config = configparser.ConfigParser()
config.read_string(
    """
[logging]
log_level=INFO

[wlan]
#country=US
#ssid=abc
#psk=xyz

[sign]
flip=false
mode=subway
brightness=0
display_height=32
display_width=192
debug=false

[subway]
api_key=
pages=
direction=south,north,0,1
route=
station=123,s-dr5rurx7ss-w72st~broadway

[adsb]
api_key=
lat=0
lon=0
radius=1
max_altitude=99999
route_api=flightaware

[boating]
api_key=
weather_station=KNYC
zone=ANZ338
buoy=ROBN4
tide_station=8518750
current_station=NYH1927
current_bin=13
"""
)

config_locations = [
    "config.ini",
    "/etc/signpi/config.ini",
    "/media/mass_storage_gadget/config.ini",
]
for f in config_locations:
    try:
        config.read(f)
    except:
        pass

logging.basicConfig(level=getattr(logging, config["logging"]["log_level"], None))

def main():
    wlan = config["wlan"]
    if "country" in wlan:
        os.system(f"raspi-config nonint do_wifi_country '{wlan['country']}'")
    if "ssid" in wlan and "psk" in wlan:
        os.system(
            f"raspi-config nonint do_wifi_ssid_passphrase '{wlan['ssid']}' '{wlan['psk']}'"
        )


if __name__ == "__main__":
    main()
