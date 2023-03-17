#!/usr/bin/python3
"""
When run, update the wifi configuration from config.ini, otherwise provide the
  values from config.ini in 'config'
"""
import configparser
import os

config = configparser.ConfigParser()
config.read(['/media/mass_storage_gadget/config.ini', 'config.ini'])


def main():
    wlan = config['wlan']

    wpa_supplicant_conf = \
        f"""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country="{wlan['country']}"

network={{
        ssid="{wlan['ssid']}"
        psk="{wlan['psk']}"
}}"""
    print("updating /etc/wpa_supplicant/wpa_supplicant.conf to\n" +
          wpa_supplicant_conf)

    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
        f.write(wpa_supplicant_conf)
    # trigger wpa_suplicant to reload the conf

    os.system("wpa_cli reconfigure")


if __file__ == '__main__':
    main()
