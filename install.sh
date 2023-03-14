#!/bin/bash 

set -e

install -t /usr/local/bin/ composite_gadget.sh
install -t /usr/lib/systemd/system/ usb_gadget.service

systemctl enable usb_gadget.service
