#!/bin/bash 

set -e

dd if=/dev/zero of=/var/local/mass_storage_backing bs=1M seek=16 count=0
parted --script /var/local/mass_storage_backing mktable msdos 'mkpart primary fat32 0 -0'
losetup -o512 /dev/loop0 /var/local/mass_storage_backing
mkfs.vfat /dev/loop0

mkdir -p /media/mass_storage_gadget
sudo mount -o umask=000 -t vfat /dev/loop0 /media/mass_storage_gadget

install -t /usr/local/bin/ composite_gadget.sh
install -t /usr/lib/systemd/system/ usb_gadget.service

systemctl enable usb_gadget.service




