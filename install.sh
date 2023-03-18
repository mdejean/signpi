#!/bin/bash 

systemctl stop usb_gadget
systemctl stop sign_startup # FIXME: this should do the below

umount /media/mass_storage_gadget
losetup -d /dev/loop0

set -e

reformat=1

for arg in "$@"; do
  shift
  case $arg in
    --preserve-config) preserve_config=1 ;;
    --no-reformat) reformat=0 ;;
  esac
done

if [ $reformat -gt 0 ] ; then
    if [ -e /var/local/mass_storage_backing -a $preserve_config -eq 1 ] ; then
        # mount if exists
        losetup -o512 /dev/loop0 /var/local/mass_storage_backing
        mount -o umask=000 -t vfat /dev/loop0 /media/mass_storage_gadget
        #copy config to /tmp/ if exists
        if [ -e /media/mass_storage_gadget/config.ini ] ; then
            cp /media/mass_storage_gadget/config.ini /tmp/
        fi
        umount /media/mass_storage_gadget
        losetup -d /dev/loop0
    fi

    # create backing file
    dd if=/dev/zero of=/var/local/mass_storage_backing bs=1M seek=16 count=0
    parted --script /var/local/mass_storage_backing mktable msdos 'mkpart primary fat32 0 -0'
    losetup -o512 /dev/loop0 /var/local/mass_storage_backing
    mkfs.vfat /dev/loop0

    mkdir -p /media/mass_storage_gadget
    mount -o umask=000 -t vfat /dev/loop0 /media/mass_storage_gadget

    if [ $preserve_config -eq 1 ] ; then
        cp /tmp/config.ini /media/mass_storage_gadget/
    else
        cp config.ini /media/mass_storage_gadget/
    fi

    umount /media/mass_storage_gadget
    losetup -d /dev/loop0
fi

mkdir -p /usr/local/share/signpi
mkdir -p /usr/local/lib/signpi
install -t /usr/local/bin/ composite_gadget.sh check_usb_speed.sh startup.sh
install -t /usr/local/lib/signpi/ *.py
install -t /usr/local/share/signpi/ *.ttf config.ini template.bin routes.txt stops.txt
install -t /usr/lib/systemd/system/ *.service *.timer

systemctl enable sign_startup.service
systemctl enable usb_gadget.service
systemctl enable generate_image.timer
systemctl enable check_usb_sign.timer

echo Finished installing, restarting

systemctl restart sign_startup

echo Done

# mput *.sh *.service *.timer *.py *.ttf template.bin stops.txt routes.txt config.ini
