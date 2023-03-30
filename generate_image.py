#!/usr/bin/env python3
"""
Generate COLOR_01.PRG
"""

from config import *
import layout
import hc1


from PIL import Image
import json
import sys

transpose_base = Image.Transpose if hasattr(
        Image, 'Transpose') else Image #PIL 8.1 change

def image_to_6bpp(img):
    img = img.transpose(transpose_base.TRANSPOSE)
    return bytes([
        (pixel[0] >> 6) | ((pixel[1] >> 6) << 2) | ((pixel[2] >> 6) << 4)
        for pixel in img.getdata()
    ])

def main():
    img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    if mode == 'subway':
        with open('trips.json') as f:
            trips = json.load(f)
        layout.draw(img, trips)
    elif mode == 'splash':
        layout.splash_screen(img)

    frames = [img]
    frame_times = [1]

    # for debugging
    img.show()

    with open(target, 'wb') as f:
        f.write(hc1.generate_prg(
            sign.getint('brightness', 0),
            [
                image_to_6bpp(
                    i.transpose(transpose_base.ROTATE_180)
                    if sign.getboolean('flip', False)
                    else i
                ) for i in frames
            ],
            frame_times
        ))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    main()
