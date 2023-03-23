#!/bin/bash

set -e

if [ "$1" != "down" ] ; then
    losetup -o512 /dev/loop0 /var/local/mass_storage_backing
    mount -o sync,flush,umask=000 -t vfat /dev/loop0 /media/mass_storage_gadget
else
    losetup -d /dev/loop0
    umount /media/mass_storage_gadget
fi
