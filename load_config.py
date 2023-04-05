#!/usr/bin/python3
"""
When run, update the wifi configuration from config.ini, otherwise provide the
  values from config.ini in 'config'
"""
import configparser
import os

config = configparser.ConfigParser()
config_locations = [
    'config.ini',
    '/etc/signpi/config.ini',
    '/media/mass_storage_gadget/config.ini'
]
for f in config_locations:
    try:
        config.read(f)
    except:
        pass


def main():
    wlan = config['wlan']
    if 'country' in wlan:
        os.system(f"raspi-config nonint do_wifi_country '{wlan['country']}'")
    if 'ssid' in wlan and 'psk' in wlan:
        os.system(f"raspi-config nonint do_wifi_ssid_passphrase '{wlan['ssid']}' '{wlan['psk']}'")


if __name__ == '__main__':
    main()
