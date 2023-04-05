from load_config import config

#TODO: refactor config stuff

api_key = ''

sign = config['sign']

subway = config['subway']

wlan = config['wlan']

mode = sign['mode'] or 'clock'

direction = subway['direction'] or 'north'

goodservice_url = 'https://www.goodservice.io/api/stops/' + subway.get('station')

target = '/media/mass_storage_gadget/COLOR_01.PRG'

DISPLAY_WIDTH = 192
DISPLAY_HEIGHT = 32
