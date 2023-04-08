"""
Subway arrival sign layout
"""
import config

import time
import csv
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageColor

LINE_HEIGHT = 16
DISPLAY_HEIGHT = config.DISPLAY_HEIGHT
DISPLAY_WIDTH = config.DISPLAY_WIDTH

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
hv = ImageFont.truetype('DejaVuSans-Bold.ttf', 126)
#gem = ImageFont.load('gem.pil')

def new_frame():
    return Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT))

def splash_screen():
    img = new_frame()
    draw = ImageDraw.Draw(img)
    
    draw.text((0, 0), text=f"signpi 0.3 mode={config.mode}", anchor='lt', font=pokemon)
    draw.text((DISPLAY_WIDTH, 0), text=time.strftime('%Y-%m-%d %H:%M'), anchor='rt', font=pokemon)
    if config.mode == 'subway':
        draw.text((0, DISPLAY_HEIGHT), text=stops[config.subway.get('station')]['stop_name'], anchor='lb', font=pokemon)
        draw.text((DISPLAY_WIDTH, DISPLAY_HEIGHT), text=config.subway.get('direction'), anchor='rb', font=pokemon)

    return [img], [1]

def subway():
    with open('trips.json') as f:
        trips = json.load(f)

    now = time.time()

    if len(trips) < 2 or max(t['timestamp'] for t in trips) < now - 60 * 5:
        img = new_frame()
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), "No data", anchor='lt')
        #TODO: better no data screen
        return [img], 1

    frames = []
    frame_times = []
    for page in range(min(config.subway.getint('pages', 2), len(trips) // 2)):
        img = new_frame()
        for i in range(page * 2, (page + 1) * 2):
            stop_id = trips[i]['destination_stop']

            eta_min = round(
                (trips[i]['estimated_current_stop_arrival_time'] - now) / 60)
            if eta_min > 99 or trips[i]['is_delayed']:
                eta = 'Delay'
            else:
                eta = f'{eta_min} min'

            draw_trip(img,
                    line_heights[i % len(line_heights)],
                    order=f'{i+1}.',
                    route=trips[i]['route_id'],
                    dest=stops[stop_id]['stop_name'],
                    dest_short='x',
                    eta=eta)
        frames.append(img)
        frame_times.append(10)
    return frames, frame_times

def draw_trip(img,
              y,
              order,
              route,
              dest,
              dest_short,
              eta,
              eta_fill=(255, 255, 255)):

    order_font = fifteen
    main_font = pokemon

    BULLET_SIZE = 14
    ORDER_WIDTH = 8

    draw = ImageDraw.Draw(img)
    draw.fontmode = '1' # no antialiasing

    draw.text((0, y),
              order,
              font=order_font,
              anchor='lm',
              fill=(255, 255, 255))

    draw_bullet(img, route, (ORDER_WIDTH + BULLET_SIZE - BULLET_SIZE // 2, y-1), BULLET_SIZE)
    dest_x = ORDER_WIDTH + BULLET_SIZE + 4
    available_space = DISPLAY_WIDTH - dest_x - max(
        main_font.getlength('Delay'), main_font.getlength('99 min'))

    draw.text((dest_x, y),
              text=dest
              if main_font.getlength(dest) < available_space else dest_short,
              font=main_font,
              anchor='lm',
              fill=(255, 255, 255))

    draw.text((DISPLAY_WIDTH, y),
              text=eta,
              anchor="rm",
              font=main_font,
              fill=eta_fill)

def draw_bullet(img, route_id, center, diameter):
    draw = ImageDraw.Draw(img)
    bullet_font = pm #gem
    x, y = center

    route = routes[route_id]
    if len(route['route_color']) == 6:
        route_color = ImageColor.getrgb(f"#{route['route_color']}")
    else:
        route_color = ImageColor.getrgb('black')

    if len(route['route_text_color']) == 6:
        route_text_color = ImageColor.getrgb(
            f"#{route['route_text_color']}")
    else:
        if sum(route_color) / 3 > 144:
            route_text_color = ImageColor.getrgb('black')
        else:
            route_text_color = ImageColor.getrgb('white')

    bounds = [[x - math.floor(diameter / 2), x + math.ceil(diameter / 2)],
              [y - math.floor(diameter / 2), y + math.ceil(diameter / 2)]]

    if route_id in ('FX', '5X', '6X', '7X'):
        # draw diamond
        route_text = route_id[:1]
        draw.polygon([
            (bounds[0][0]-1, y),
            (x, bounds[1][0]-1 ),
            (bounds[0][1]+1, y),
            (x, bounds[1][1]+1)],
        fill=route_color)
    else:
        route_text = route['route_short_name']
        draw.ellipse([(bounds[0][0], bounds[1][0]),
                    (bounds[0][1], bounds[1][1])],
                    fill=route_color)

    #draw.text((x-3, y-6), route_text, font=gem, anchor='mm', fill=route_text_color)
    draw.text((x+1, y), route_text, font=bullet_font, anchor='mm', fill=route_text_color)
