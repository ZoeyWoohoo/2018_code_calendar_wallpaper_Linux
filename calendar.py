import datetime
import os
import json

from urllib.parse import urlparse
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

BASE = os.getcwd()  # now path
PDF_SOURCE = BASE + '/2018_code_calendar.pdf[{}]'  # PDF path
OUTPUT = BASE + '/calendar_wallpaper.jpg'  # new wallpaper
PAGE_OFFSET = 6  # PDF start page

time = datetime.datetime.now()
current_week = time.isocalendar()[1]
current_day = time.isoweekday()
page = PAGE_OFFSET + current_week

calendar_resolution = 170

red = '#ff4d00'
green = '#00ff83'

CCPX = 118  # Circle center point x axis coordinate
CCPY = 924  # Circle center point y axis coordinate
CPPX = 88  # Circle perimeter point x axis coordinate
CPPY = 894  # Circle perimeter point y axis coordinate
LSPX = 89  # Line start point x axis coordinate
LSPY = 895  # Line start point y axis coordinate
LEPX = 147  # Line end point x axis coordinate
LEPY = 953  # Line end point y axis coordinate

with open('config.json', 'r') as f:
    config = json.load(f)

if config['background_image'] != '':
    BACKGROUND_SOURCE = BASE + "/wallpaper/" + config['background_image']
else:
    BACKGROUND_SOURCE = BASE + "/wallpaper.png"

if config['position'] != "":
    if config['position'] == 'right':
        MARGIN_LEFT = 1100
        MARGIN_TOP = 60
    else:
        MARGIN_LEFT = 40
        MARGIN_TOP = 60
else:
    MARGIN_LEFT = 1100 if (config['left'] == "") else int(config['left'])
    MARGIN_TOP = 60 if (config['top'] == "") else int(config['top'])


def draw_type_one(draw, width):
    if config['mark_color'] == "":
        draw.stroke_color = Color(green)
    spacing = 100 if (width != 2560) else 118
    draw.circle((CCPX + spacing * (current_day - 1), CCPY),
                (CPPX + spacing * (current_day - 1), CPPY))


def draw_type_two(draw, width):
    if config['mark_color'] == "":
        draw.stroke_color = Color(red)
    spacing = 100 if (width != 2560) else 118
    if current_day != 1:
        for x in range(1, current_day):
            draw.circle((CCPX + spacing * (x - 1), CCPY),
                        (CPPX + spacing * (x - 1), CPPY))
            draw.line((LSPX + spacing * (x - 1), LSPY),
                      (LEPX + spacing * (x - 1), LEPY))


def draw_type_three(draw, width):
    if config['mark_color'] == "":
        draw.stroke_color = Color(red)
    spacing = 100 if (width != 2560) else 118
    if current_day != 1:
        for x in range(1, current_day):
            draw.line((LSPX + spacing * (x - 1) + 6, LSPY + 6),
                      (LEPX + spacing * (x - 1) - 5, LEPY - 5))
            draw.line((LSPX + spacing * (x - 1), LSPY + 65),
                      (LEPX + spacing * (x - 1), LEPY - 65))


def draw_mark(width):
    with Drawing() as draw:
        if config['mark_color'] != "":
            draw.stroke_color = Color(config['mark_color'])
        draw.stroke_width = 4
        draw.stroke_opacity = 0.8
        draw.fill_opacity = 0
        if config['mark_type'] == "":
            draw_type_one(draw, width)
        else:
            if config['mark_type'] == '1':
                draw_type_one(draw, width)
            if config['mark_type'] == '2':
                draw_type_two(draw, width)
            if config['mark_type'] == '3':
                draw_type_three(draw, width)
        draw(calendar)


with Image(filename=BACKGROUND_SOURCE) as background:
    if background.width == 2560:
        calendar_resolution = 200
        CCPX = 138
        CCPY = 1099
        CPPX = 108
        CPPY = 1069
        LSPX = 109
        LSPY = 1070
        LEPX = 167
        LEPY = 1128

    with Image(filename=PDF_SOURCE.format(page),
               resolution=calendar_resolution) as calendar:
        calendar.crop(0, 65, calendar.width, calendar.height)
        draw_mark(background.width)

        background.composite_channel(
            'default_channels', calendar, 'blend', MARGIN_LEFT, MARGIN_TOP)
        background.format = 'jpeg'
        background.save(filename=OUTPUT)

        uri = urlparse(OUTPUT, scheme='file')
        change_background = ('gsettings set org.gnome.desktop.background '
                             + 'picture-uri '
                             + uri.geturl())

        os.system(change_background)
