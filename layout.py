"""
Subway arrival sign layout
"""
from config import *

import time
import csv
from PIL import ImageDraw, ImageFont, ImageColor

LINE_HEIGHT = 16

line_heights = [LINE_HEIGHT / 2, DISPLAY_HEIGHT - LINE_HEIGHT / 2 + 1]

BULLET_SIZE = 14
ORDER_WIDTH = 8

with open('routes.txt', 'r') as f:
    routes = {r['route_id']: r for r in csv.DictReader(f)}

with open('stops.txt', 'r') as f:
    stops = {s['stop_id']: s for s in csv.DictReader(f)}

mania = ImageFont.truetype('mania.ttf', 14)
pokemon = ImageFont.truetype('Pokemon X and Y.ttf', 11)
fifteen = ImageFont.truetype('15x5.ttf', 16)
pm = ImageFont.truetype('pixelmix_bold.ttf', 8)

def splash_screen(img):
    draw = ImageDraw.Draw(img)
    
    draw.text((0, 0), text=f"signpi 0.2 mode={mode}", anchor='lt', font=pokemon)
    draw.text((DISPLAY_WIDTH, 0), text=time.strftime('%Y-%m-%d %H:%M'), anchor='rt', font=pokemon)
    if mode == 'subway':
        draw.text((0, DISPLAY_HEIGHT), text=stops[station]['stop_name'], anchor='lb', font=pokemon)
        draw.text((DISPLAY_WIDTH, DISPLAY_HEIGHT), text=direction, anchor='rb', font=pokemon)

def draw(img, trips):
    # TODO: alternating pages

    now = time.time()
    draw = ImageDraw.Draw(img)

    if len(trips) < 2 or max(t['timestamp'] for t in trips) < now - 60 * 5:
        draw.text((0, 0), "No data", anchor='lt')
        #TODO: better no data screen
        return
    for i in (0, 1):
        route = routes[trips[i]['route_id']]
        stop_id = trips[i]['destination_stop']

        eta_min = round(
            (trips[i]['estimated_current_stop_arrival_time'] - now) / 60)
        if eta_min > 99 or trips[i]['is_delayed']:
            eta = 'Delay'
        else:
            eta = f'{eta_min} min'
        if len(route['route_color']) == 6:
            route_color = ImageColor.getrgb(f"#{route['route_color']}")
        else:
            route_color = ImageColor.getrgb('black')

        if len(route['route_text_color']) == 6:
            route_text_color = ImageColor.getrgb(
                f"#{route['route_text_color']}")
        else:
            if sum(route_color) / 3 > 127:
                route_text_color = ImageColor.getrgb('black')
            else:
                route_text_color = ImageColor.getrgb('white')

        draw_trip(draw,
                  line_heights[i],
                  order=f'{i+1}.',
                  route=route['route_short_name'],
                  route_color=route_color,
                  route_text_color=route_text_color,
                  dest=stops[stop_id]['stop_name'],
                  dest_short='x',
                  eta=eta)

    # draw.text((192, 0),
    #           "10:47 PM",
    #           font=mania,
    #           anchor='rt',
    #           fill=(255, 255, 255))


def draw_trip(draw,
              y,
              order,
              route,
              route_color,
              route_text_color,
              dest,
              dest_short,
              eta,
              eta_fill=(255, 255, 255)):

    order_font = fifteen
    bullet_font = pm
    main_font = pokemon

    BULLET_SIZE = 14
    ORDER_WIDTH = 8

    draw.text((0, y),
              order,
              font=order_font,
              anchor='lm',
              fill=(255, 255, 255))

    draw.ellipse([(ORDER_WIDTH + 0, y - BULLET_SIZE / 2 - 1),
                  (ORDER_WIDTH + BULLET_SIZE, y + BULLET_SIZE / 2 - 1)],
                 fill=route_color,
                 width=2)
    draw.text((ORDER_WIDTH + BULLET_SIZE / 2 + 1, y - 1),
              text=route,
              font=bullet_font,
              anchor='mm',
              fill=route_text_color)

    dest_x = ORDER_WIDTH + BULLET_SIZE + 4
    available_space = DISPLAY_WIDTH - dest_x - max(
        main_font.getlength('Delay'), main_font.getlength('99 min'))

    draw.text((dest_x, y),
              text=dest_short
              if main_font.getlength(dest) > available_space else dest,
              font=main_font,
              anchor='lm',
              fill=(255, 255, 255))

    draw.text((DISPLAY_WIDTH, y),
              text=eta,
              anchor="rm",
              font=main_font,
              fill=eta_fill)
