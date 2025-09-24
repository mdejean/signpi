## signpi
![signpi](https://user-images.githubusercontent.com/4019846/227429322-2647b48b-3728-4d00-b287-a09355d859c0.jpg)

A subway arrivals sign using an off-the-shelf sign and a Raspberry Pi. Powered by the [goodservice.io](https://goodservice.io) API.

### The ugly part

Each time the display updates, the sign will display `Load`, `ok ok`,
`HC-1`, and the display resolution. This process takes about 3 seconds.

[signpi.webm](https://user-images.githubusercontent.com/4019846/227528822-9f047f06-6170-4335-9cce-da6bcdb2f98a.webm)

### How-to

You will need

* A Raspberry Pi Zero W. These are unfortunately hard to get right now,
but should be more widely available soon.
* A 192 x 32 LED sign with a HC-1 controller.
These can be found on ebay, aliexpress, amazon.

Now, download the release zip: https://github.com/mdejean/signpi/releases/download/v0.4/signpi-0.4.zip

1. Insert your microSD card into the reader and open up rpi-imager.
Choose Raspberry Pi OS Lite

2. Adjust the advanced settings, especially the wireless network settings.
Uncheck the eject after complete option.

3. Write the microSD card.

4. Open up the 'bootfs' drive

    i. edit `cmdline.txt`: After `rootwait` add ` modules-load=dwc2`  
    ii. edit `config.txt`: At the bottom of the file, under `[all]` add a line with `dtoverlay=dwc2`  
    iii. Rename `firstrun.sh` to `firstrun2.sh`  
    iv. Copy `signpi.deb` and `firstrun.sh` to it.  

5. Eject, put the microSD card in your Pi and plug it in to the sign.

6. Wait about 6 minutes for the first-run process on the Pi to complete. When
it's done you should have a functioning sign, displaying northbound arrivals
at Nevins Street.


7. To change the station, unplug the Pi from the sign and plug
it into your computer. It will appear after 15-20 seconds as a flash drive.
Open the `config.ini` file on the flash drive and edit the station. To find
your station's code, go to https://goodservice.io/stations and click on your
station. The station's code is at the end of the page's address. For example
Nevins Street is `https://goodservice.io/stations/234` so the code is `234`


### How it works

These displays allow the user to program the sign using some software
which puts a file (`COLOR_01.PRG`) on a flash drive which is then plugged
in to the sign. signpi makes the Raspberry Pi Zero W pretend to be a
flash drive containing that file, and 'unplugs' itself to get
the sign to display the image it has created.

### ADSB mode ^(new!)

[adsb.mov](https://github.com/user-attachments/assets/3b30e8f3-b036-454e-9836-f69fb1c8616b)

Displays the nearest aircraft to a location.

For aircraft location this repeatedly calls the [adsb.lol API](https://api.adsb.lol/docs) which is free.
For route information this uses the flightaware API which is not free - it
costs $0.005 per request, with up to $5/mo free. signpi tries to make only one
request per plane, but in busy areas this still adds up quickly. You must
create an account and put the api key in config.ini to use the flightaware api.


### License

Except as otherwise noted, this software is distributed under the terms of the GNU General Public License, version 2 or later. See LICENSE for the full text.
