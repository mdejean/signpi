#!/usr/bin/python

from load_config import config

api_key = ''

sign = config['sign']

mode = sign['mode'] or 'clock'

station = sign['station'] or '234'

direction = sign['direction'] or 'north'

goodservice_url = 'https://www.goodservice.io/api/stops/' + station

target = '/media/mass_storage_gadget/COLOR_01.PRG'

DISPLAY_WIDTH = 192
DISPLAY_HEIGHT = 32
