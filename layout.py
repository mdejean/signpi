"""
Subway arrival sign layout
"""

from load_config import config
import subway
import boating

import time
import csv
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageColor

LINE_HEIGHT = 16
DISPLAY_HEIGHT = int(config["sign"]["display_height"])
DISPLAY_WIDTH = int(config["sign"]["display_width"])

pokemon = ImageFont.truetype("fonts/Pokemon X and Y.ttf", 11)
fifteen = ImageFont.truetype("fonts/15x5.ttf", 16)
pm = ImageFont.truetype("fonts/pixelmix_bold.ttf", 8)
font0403 = ImageFont.truetype("fonts/04b03_thinspace.ttf", 8)
# tahoma = ImageFont.truetype('fonts_tahoma.ttf', 11)
# tahomabd = ImageFont.truetype('fonts_tahomabd.ttf', 11)
# msss = ImageFont.truetype('fonts_ms_sans_serif.ttf', 13)
# portfolio = ImageFont.truetype('Mx437_Portfolio_6x8.ttf', 8)
small = ImageFont.truetype("fonts/fonts_small_fonts.ttf", 11)


def new_frame():
    return Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT))


def splash_screen():
    img = new_frame()
    draw = ImageDraw.Draw(img)

    draw.text(
        (0, 0),
        text=f"signpi 0.4 mode={config['sign']['mode']}",
        anchor="lt",
        font=pokemon,
    )
    draw.text(
        (DISPLAY_WIDTH, 0),
        text=time.strftime("%Y-%m-%d %H:%M"),
        anchor="rt",
        font=pokemon,
    )
    if config["sign"]["mode"] == "subway":
        draw.text(
            (0, DISPLAY_HEIGHT),
            text=subway.stop_name(config["subway"].get("station")),
            anchor="lb",
            font=pokemon,
        )
        draw.text(
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
            text=config["subway"].get("direction"),
            anchor="rb",
            font=pokemon,
        )

    return [img], [1]
