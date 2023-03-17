#!/usr/bin/python

from config import *

import time
import csv
from PIL import ImageDraw, ImageFont

LINE_HEIGHT = 16

line_heights = [LINE_HEIGHT / 2, DISPLAY_HEIGHT - LINE_HEIGHT / 2]

BULLET_SIZE = 14
ORDER_WIDTH = 8


def draw(img, trips):
    # TODO: alternating pages
    with open('routes.txt', 'r') as f:
        routes = {r['route_id']: r for r in csv.DictReader(f)}

    with open('stops.txt', 'r') as f:
        stops = {s['stop_id']: s for s in csv.DictReader(f)}

    now = time.time()

    if len(trips) < 2 or max(t['timestamp'] for t in trips) < now - 60 * 5:
        #TODO: no data screen
        return
    for i in (0, 1):
        route_id = trips[i]['route_id']
        stop_id = trips[i]['destination_stop']

        eta_min = round(
            (trips[i]['estimated_current_stop_arrival_time'] - now) / 60)
        if eta_min > 99 or trips[i]['is_delayed']:
            eta = 'Delay'
        else:
            eta = f'{eta_min} min'
        if len(routes[route_id]['route_color']) == 6:
            route_color = '#' + routes[route_id]['route_color']
        else:
            route_color = 'black'

        if len(routes[route_id]['route_text_color']) == 6:
            route_text_color = '#' + routes[route_id]['route_text_color']
        else:
            route_text_color = 'white'

        draw_trip(img,
                  line_heights[i],
                  order=f'{i+1}.',
                  route=routes[route_id]['route_short_name'],
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


def draw_trip(img,
              y,
              order,
              route,
              route_color,
              route_text_color,
              dest,
              dest_short,
              eta,
              eta_fill=(255, 255, 255)):
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

    draw.text((0, y), order, font=fifteen, anchor='lm', fill=(255, 255, 255))
    #draw.text((0, line2_mid + 1), # + 1 because this font sucks

    draw.ellipse([(ORDER_WIDTH + 0, y - BULLET_SIZE / 2),
                  (ORDER_WIDTH + BULLET_SIZE, y + BULLET_SIZE / 2)],
                 fill=route_color,
                 width=2)
    draw.text((ORDER_WIDTH + BULLET_SIZE / 2 + 1, y),
              text=route,
              font=pm,
              anchor='mm',
              fill=route_text_color)

    dest_x = ORDER_WIDTH + BULLET_SIZE + 4
    available_space = DISPLAY_WIDTH - dest_x - max(pokemon.getlength('Delay'),
                                                   pokemon.getlength('99 min'))

    draw.text(
        (dest_x, y),
        text=dest_short if pokemon.getlength(dest) > available_space else dest,
        font=pokemon,
        anchor='lm',
        fill=(255, 255, 255))

    draw.text((DISPLAY_WIDTH, y),
              text=eta,
              anchor="rm",
              font=pokemon,
              fill=eta_fill)
