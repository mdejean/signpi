#!/usr/bin/env python3
"""
Generate COLOR_01.PRG
"""

from load_config import config
import layout
import subway
import boating
import adsb
import hc1


from PIL import Image
import sys

target = "/media/mass_storage_gadget/COLOR_01.PRG"

transpose_base = (
    Image.Transpose if hasattr(Image, "Transpose") else Image
)  # PIL 8.1 change


def image_to_6bpp(img):
    img = img.transpose(transpose_base.TRANSPOSE)
    return bytes(
        [
            (pixel[0] >> 6)
            | ((pixel[1] >> 6) << 2)
            | ((pixel[2] >> 6) << 4)
            for pixel in img.getdata()
        ]
    )


def generate_image(mode="splash", target="COLOR_01.PRG"):
    if mode == "subway":
        frames, frame_times = subway.get_layout()
    elif mode == "boating":
        frames, frame_times = boating.get_layout()
    elif mode == "adsb":
        frames, frame_times = adsb.get_layout()
    elif mode == "splash":
        frames, frame_times = layout.splash_screen()

    # for debugging
    for f in frames:
        f.show()

    with open(target, "wb") as f:
        f.write(
            hc1.generate_prg(
                frames=[
                    image_to_6bpp(
                        i.transpose(transpose_base.ROTATE_180)
                        if config["sign"].getboolean("flip", False)
                        else i
                    )
                    for i in frames
                ],
                frame_times=frame_times,
                brightness=config["sign"].getint("brightness", 0),
                display_height=int(config["sign"]["display_height"]),
                display_width=int(config["sign"]["display_width"]),
            )
        )


if __name__ == "__main__":
    generate_image(sys.argv[1] if len(sys.argv) > 1 else config["sign"]["mode"], target)
