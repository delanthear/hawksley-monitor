from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from datetime import datetime

import os
import pprint
import ripple
import fox

# set to output data structures
debug = 0

# initialise the display
inky_display = auto()

# Get the current path
PATH = os.path.dirname(__file__)

# Ripple API Calls
rippleAPIKey = "ADD YOUR RIPPLE API KEY"
rippleDataset = ripple.getRippleData(rippleAPIKey)

# Fox API Calls
fox_api_key = "ADD YOUR FOX API KEY";
fox_serial = "ADD YOUR FOX SERIAL";
foxDataset = fox.getfoxData(fox_api_key, fox_serial)

# Extracting all values and their units into a dictionary
foxdataDict = {item['variable']: {'value': item['value'], 'unit': item['unit']} 
             for item in foxDataset['realtime']['result'][0]['datas']}

# Iterate over the dictionary and adjust the values and units if needed
for variable, data in foxdataDict.items():
	# Only convert if the value is less than 1
	if data['value'] < 1:
		if data['unit'] == 'kW':
			data['value'] *= 1000  # Convert kW to W
			data['unit'] = 'W'     # Change the unit to W
			data['value'] = int(round(data['value'], 0))  # Round to 0 decimal places if unit is W
	elif data['unit'] == 'kW':
		data['value'] = round(data['value'], 2)  # Round to 2 decimal places if unit stays kW

if debug:
	pprint.pprint(rippleDataset)
	pprint.pprint(foxdataDict)

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(HankenGroteskBold, 16)

inkywidth = inky_display.width
half_inkywidth = inkywidth / 2
quarter_inkywidth = inkywidth / 4
threequarter_inkywidth =  inkywidth - quarter_inkywidth

inkyheight = inky_display.height
half_inkyheight = inkyheight / 2
quarter_inkyheight = inkyheight / 4
threequarter_inkyheight = inkyheight - quarter_inkyheight

icon_size = 25 # height of icons used
history_update_size = 20 # size of last update bar

right_section_width = threequarter_inkywidth - icon_size + 5 #where we want the right section border
right_section_icon_position = right_section_width + 1 # where the right section icons go
right_section_values = right_section_icon_position + icon_size # where the right section values go

if debug:
	print ("Inky width: " + str(inkywidth))
	print ("Half: " + str(half_inkywidth))
	print ("Quart: " + str(quarter_inkywidth))
	print ("3Quart: " + str(threequarter_inkywidth))

	print ("Inky height: " + str(inkyheight))
	print ("Half: " + str(half_inkyheight))
	print ("Quart: " + str(quarter_inkyheight))
	print ("3Quart: " + str(threequarter_inkyheight))

	print ("RSW: " + str(right_section_width))

##################################################
# Draw the lines

linecolor = inky_display.BLACK

draw.line((0, inkyheight - history_update_size - icon_size - 1, right_section_width, inkyheight - history_update_size - icon_size - 1), linecolor)	# Line beneath battery level
draw.line((0, inkyheight - history_update_size, inkywidth, inkyheight - history_update_size), linecolor)	# Horizontal bottom line
draw.line((right_section_width, 0, right_section_width, inkyheight - history_update_size), linecolor) # Verticle middle line

##################################################
# Icons

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

icons_path = PATH + "/resources/"

solar_icon_filename = icons_path + "solar-gen-bw.png"
wind_icon_filename = icons_path + "wind-gen-bw.png"
house_icon_filename = icons_path + "house-load-bw.png"
sun_icon_filename = icons_path + "icon-sun-bw.png"
windspeed_icon_filename = icons_path + "icon-wind-bw.png"
usage_icon_filename = icons_path + "house-usage-bw.png"
export_icon_filename = icons_path + "power-export-bw.png"
battery_charging_icon_filename = icons_path + "battery-charging-bw.png"

# select the right battery icon for the level

bat_level = "10"

if int(foxdataDict['SoC']['value']) >= 100:
	bat_level = "100"
elif int(foxdataDict['SoC']['value']) >= 90:
	bat_level = "90"
elif int(foxdataDict['SoC']['value']) >= 75:
	bat_level = "75"
elif int(foxdataDict['SoC']['value']) >= 50:
	bat_level = "50"
elif int(foxdataDict['SoC']['value']) >= 25:
	bat_level = "25"

battery_draining_filename = icons_path + "battery-draining-" + bat_level + "-bw.png"

masks = {}

icon_dictionary = [battery_draining_filename, sun_icon_filename, house_icon_filename, usage_icon_filename, windspeed_icon_filename, solar_icon_filename, wind_icon_filename]

icon_positions = [(0,0), (int(right_section_icon_position), 0), (int(right_section_icon_position), icon_size), (int(right_section_icon_position), icon_size * 2), (int(right_section_icon_position), icon_size * 3), (0, int(inkyheight) - history_update_size - icon_size), (int((right_section_width / 2) + 5), int(inkyheight) - history_update_size - icon_size)]

# Is the battery charging? Add the appropriate icon
if int(foxdataDict['batChargePower']['value']) > 0:
	icon_dictionary.append(battery_charging_icon_filename)
	icon_positions.append((0, int(inkyheight) - history_update_size - (icon_size * 2)))

# Are we feeding in? Add the icon.
if int(foxdataDict['feedinPower']['value']) > 0:
	icon_dictionary.append(export_icon_filename)
	icon_positions.append((int(right_section_icon_position - icon_size), 2))

# Load and place multiple icons
for icon_path, position in zip(icon_dictionary, icon_positions):
	icon = Image.open(icon_path).resize((icon_size, icon_size)) # Resize icons if necessary
	img.paste(icon, position, create_mask(icon))


##################################################
# LEFT SECTION 

font = ImageFont.truetype(HankenGroteskBold, 44)
battery = str(int(foxdataDict['SoC']['value'])) + foxdataDict['SoC']['unit']

_, _, w, h = font.getbbox(battery)
x = (right_section_width / 2) - (w / 2)
y = ((inkyheight - 60) / 2) - (h / 2)
draw.text((x, y), battery, inky_display.BLACK, font)

##################################################
# BOTTOM LEFT SECTION 
font = ImageFont.truetype(HankenGroteskBold, 16)

solar_yield = str(int(round(foxDataset['historical']['generation']['day_total'], 1))) + foxDataset['historical']['generation']['unit']
_, _, w, h = font.getbbox(solar_yield)
x = icon_size
y = inkyheight - history_update_size - icon_size + (((icon_size - h) / 2) / 2) + 2
draw.text((x, y), solar_yield, inky_display.BLACK, font)

ripple_yield = rippleDataset['month_savings']['unit'] + str(rippleDataset['month_savings']['value'])
_, _, w, h = font.getbbox(ripple_yield)
x = (right_section_width / 2) + icon_size + 5
draw.text((x, y), ripple_yield, inky_display.BLACK, font)

##################################################
# RIGHT SECTION 

font = ImageFont.truetype(HankenGroteskBold, 16)

# PV Power output
pvpower = str(foxdataDict['pvPower']['value']) + foxdataDict['pvPower']['unit']
_, _, w, h = font.getbbox(pvpower)
x = right_section_values
y = (((icon_size - h) / 2) / 2)

draw.text((x, y), pvpower, inky_display.BLACK, font)

# Grid grid draw
grid = str(foxdataDict['gridConsumptionPower']['value']) + foxdataDict['gridConsumptionPower']['unit']
_, _, w, h = font.getbbox(grid)
x = right_section_values
y = y + icon_size
draw.text((x, y), grid, inky_display.BLACK, font)

# House draw
house = str(foxdataDict['loadsPower']['value']) + foxdataDict['loadsPower']['unit']
_, _, w, h = font.getbbox(house)
x = right_section_values
y = y + icon_size
draw.text((x, y), house, inky_display.BLACK, font)

# Windspeed
wind = str(int(round(float(rippleDataset['latest_wind_speed']['value']), 0))) + rippleDataset['latest_wind_speed']['unit']
_, _, w, h = font.getbbox(wind)
x = right_section_values
y = y + icon_size
draw.text((x, y), wind, inky_display.BLACK, font)

########################
# Bottom row

# Get the current date and time
last_update = datetime.now()

# Format the date and time
formatted_last_update = last_update.strftime("%d %b %y, %H:%M")

lastupdate = "Last update: " + formatted_last_update

font = ImageFont.truetype(HankenGroteskMedium, 18)
_, _, w, lastupdateh = font.getbbox(lastupdate)
x = (inkywidth / 2) - (w / 2)
y = (inky_display.height) - lastupdateh + 2

draw.text((x, y), lastupdate, inky_display.BLACK, font)

inky_display.set_image(img)
inky_display.show()

logentry =  "Finished running monitor: " + formatted_last_update
print(logentry)




