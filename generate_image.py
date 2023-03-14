#!/usr/bin/env python3
"""
Update the sign
"""

from PIL import Image, ImageDraw, ImageFont

DISPLAY_WIDTH = 192
DISPLAY_HEIGHT = 32


def main():
    img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    mania = ImageFont.truetype('mania.ttf', 14)
    pokemon = ImageFont.truetype('Pokemon X and Y.ttf', 11)
    fifteen = ImageFont.truetype('15x5.ttf', 16)
    pm = ImageFont.truetype('pixelmix_bold.ttf', 8)
    draw = ImageDraw.Draw(img)

    LINE_HEIGHT = 16

    line1_mid = LINE_HEIGHT / 2
    line2_mid = DISPLAY_HEIGHT - LINE_HEIGHT / 2

    BULLET_SIZE = 14
    ORDER_WIDTH = 8

    draw.text((0, 0),
              "1.",
              font=fifteen,
              anchor='lt',
              fill=(255, 255, 255))
    draw.text((0, DISPLAY_HEIGHT),
              "3.",
              font=fifteen,
              anchor='lb',
              fill=(255, 255, 255))

    draw.ellipse([(ORDER_WIDTH + 0, 0), (ORDER_WIDTH + BULLET_SIZE, BULLET_SIZE)],
             fill=(0, 255, 0),
             width=2)
    draw.text((ORDER_WIDTH + BULLET_SIZE / 2 + 1, BULLET_SIZE / 2),
              "4",
              font=pm,
              anchor='mm',
              fill=(0, 0, 0))
    draw.text((ORDER_WIDTH + BULLET_SIZE + 4, line1_mid),
              "Brooklyn Bridge - City Hall",
              font=pokemon,
              anchor='lm',
              fill=(255, 255, 255))
    draw.ellipse([(ORDER_WIDTH + 0, DISPLAY_HEIGHT - 1 - BULLET_SIZE),
              (ORDER_WIDTH + BULLET_SIZE, DISPLAY_HEIGHT - 1)],
             fill=(127, 0, 0),
             width=2)
    draw.text((ORDER_WIDTH + BULLET_SIZE / 2 + 1,
               DISPLAY_HEIGHT - 1 - BULLET_SIZE / 2),
              "2",
              font=pm,
              anchor='mm',
              fill=(255, 255, 255))
    draw.text((ORDER_WIDTH + BULLET_SIZE + 4, line2_mid),
              "Van Cortlandt Park - 242nd Street",
              font=pokemon,
              anchor='lm',
              fill=(255, 255, 255))
    # draw.text((192, 0),
    #           "10:47 PM",
    #           font=mania,
    #           anchor='rt',
    #           fill=(255, 255, 255))

    draw.text((DISPLAY_WIDTH, line1_mid),
              text="3 min",
              anchor="rm",
              font=pokemon)
    draw.text((DISPLAY_WIDTH, line2_mid),
              text="6 min",
              anchor="rm",
              font=pokemon)
    
    output = None
    with open('template.bin', 'rb') as f:
        output = f.read()
    
    # output is column-first
    img = img.transpose(Image.Transpose.TRANSPOSE)
    output += bytes([
        (pixel[0] >> 6) | ((pixel[1] >> 6) << 2) | ((pixel[2] >> 6) << 4) 
        for pixel in img.getdata()
    ])
    
    with open('COLOR_01.PRG', 'wb') as f:
        f.write(output)

if __name__ == '__main__':
    main()