#!/usr/bin/env python3
"""
Generate COLOR_01.PRG
"""

from config import *
import layout

from PIL import Image
import json


def main():
    with open('trips.json') as f:
        trips = json.load(f)

    img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    layout.draw(img, trips)

    # for debugging
    img.show()

    output = None
    with open('template.bin', 'rb') as f:
        output = f.read()
    # output is column-first
    img = img.transpose(Image.Transpose.TRANSPOSE if hasattr(
        Image, 'Transpose') else Image.TRANSPOSE)  #PIL 8.1 change
    output += bytes([
        (pixel[0] >> 6) | ((pixel[1] >> 6) << 2) | ((pixel[2] >> 6) << 4)
        for pixel in img.getdata()
    ])

    with open('COLOR_01.PRG', 'wb') as f:
        f.write(output)


if __name__ == '__main__':
    main()