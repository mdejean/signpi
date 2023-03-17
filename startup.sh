#!/bin/bash

set -e

losetup -o512 /dev/loop0 /var/local/mass_storage_backing
mount -o umask=000 -t vfat /dev/loop0 /media/mass_storage_gadget

/usr/local/lib/signpi/load_config.py
