#!/bin/bash

if [ $(cat /sys/devices/platform/soc/*/udc/*/current_speed) = "full-speed" ] ; then
    echo "Connected to sign"
    systemctl stop usb_gadget
else
    echo "Connected to computer"
fi
