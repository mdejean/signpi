#!/bin/bash

prefix=/usr

mass_storage_gadget() {
    if [ -n "$1" -a $1 = 'down' ] ; then
        modprobe -r g_mass_storage
    else
        modprobe g_mass_storage file=/var/local/mass_storage_backing removable=y
    fi
}

mount_backing() {
    losetup -o512 /dev/loop0 /var/local/mass_storage_backing
    mkdir -p /media/mass_storage_gadget
    mount -o sync,flush,umask=000 -t vfat /dev/loop0 /media/mass_storage_gadget
}

unmount_backing() {
    losetup -d /dev/loop0
    umount /media/mass_storage_gadget
}

# Reformat the backing with a new fat file system, optionally preserving the config.ini
reformat_backing() {
    if [ -n "$1" ] ; then
        preserve_config=$1
    else
        preserve_config=0
    fi
    
    if [ -e /var/local/mass_storage_backing -a "$preserve_config" -gt 0 ] ; then
        mount_backing
        #copy config to /tmp/ if exists
        if [ -e /media/mass_storage_gadget/config.ini ] ; then
            cp /media/mass_storage_gadget/config.ini /tmp/
        fi
        unmount_backing
    fi

    # create backing file
    dd if=/dev/zero of=/var/local/mass_storage_backing bs=1M seek=16 count=0
    parted --script /var/local/mass_storage_backing mktable msdos 'mkpart primary fat32 0 -0'
    losetup -o512 /dev/loop0 /var/local/mass_storage_backing
    mkfs.vfat /dev/loop0

    mount_backing
    
    if [ "$preserve_config" -gt 0 -a -e /tmp/config.ini ] ; then
        cp /tmp/config.ini /media/mass_storage_gadget/
    else
        cp config.ini /media/mass_storage_gadget/
    fi
    
    unmount_backing
}

if [ -e /var/local/mass_storage_backing ] ; then
    # Load user-edited config.ini
    mount_backing

    # If mount failed or went read-only due to filesystem errors, reformat and try to salvage config.ini
    if ! mount -l -t vfat | grep -q /media/mass_storage_gadget \
        || mount -l -t vfat | grep loop0 | grep -q '[(,]ro[),]' ; then
        unmount_backing
        reformat_backing 1
        mount_backing
    fi

    $prefix/lib/signpi/load_config.py
else
    # Start from scratch
    reformat_backing
    
    shutdown -r now #ugly hack
fi

sleep 1 # wait a sec for wifi

$prefix/lib/signpi/generate_image.py splash

unmount_backing

terminated=0
trap terminated=1 TERM

while [ $terminated -eq 0 ] ; do
    mass_storage_gadget up
    
    sleep 3 # Give some time to connect and for the sign to load
    
    usb_speed=$(cat /sys/devices/platform/soc/*/udc/*/current_speed)
    
    if [ $usb_speed = "full-speed" ] ; then
        echo "Connected to sign"
        # Disconnect the mass storage function wait so the sign loads
        mass_storage_gadget down
        
        # Wait to generate a new sign image
        sleep 56
        
        mount_backing
        
        $prefix/lib/signpi/get_data.py
        $prefix/lib/signpi/generate_image.py
        
        unmount_backing
    elif [ $usb_speed = "high-speed" ] ; then
        echo "Connected to computer"
        while [ $terminated -eq 0 ] ; do
            sleep 1 # sync a lot in the hopes that we don't lose anything when the user unplugs
            sync -f
        done
    else
        echo "USB speed is '$usb_speed'"
    fi
done

echo "Got signal, exiting"
