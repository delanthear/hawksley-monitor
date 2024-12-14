from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium
from datetime import datetime

import json
import os
import pprint
import ripple
import fox

# set to output data structures
debug = 0

# initialise the display
inky_display = auto()
inky_display.set_border(inky_display.RED)

# Get the current path
PATH = os.path.dirname(__file__)

CONFIG_FILE = PATH + "/config.json"
with open(CONFIG_FILE, 'r') as f: 
	config = json.load(f) 

# Ripple API Calls
rippleAPIKey = config['rippleAPIKey']
rippleDataset = ripple.getRippleData(rippleAPIKey)

# Fox API Calls
fox_api_key = config['fox_api_key']
fox_serial = config['fox_serial']
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

img = Image.new("P", inky_display.resolution)
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

if debug:
	print ("Inky width: " + str(inkywidth))
	print ("Half: " + str(half_inkywidth))
	print ("Quart: " + str(quarter_inkywidth))
	print ("3Quart: " + str(threequarter_inkywidth))

	print ("Inky height: " + str(inkyheight))
	print ("Half: " + str(half_inkyheight))
	print ("Quart: " + str(quarter_inkyheight))
	print ("3Quart: " + str(threequarter_inkyheight))

##################################################
# Dividers

linecolor = inky_display.RED

# history column heights and widths
history_icon_edge = 40
icon_size = 35 # height of icons used
history_update_size = 20
history_headings_size = 20
history_headings_top = half_inkyheight + 20

history_data_top =  history_headings_top + history_headings_size # top of data section y
history_section_size = inkyheight - history_data_top - history_update_size # y height of data section
history_data_middle = history_data_top + history_section_size / 2  # halfway point of data section

history_day_center = (half_inkywidth - history_icon_edge) / 4 + history_icon_edge
history_week_center = (((half_inkywidth - history_icon_edge) / 4) * 3) + history_icon_edge
history_month_center = half_inkywidth + (half_inkywidth / 4)
history_year_center = inkywidth - (half_inkywidth / 4)

draw.line((half_inkywidth, quarter_inkyheight + 10, inkywidth, quarter_inkyheight + 10), linecolor) # right side top horizontal
draw.line((0, history_headings_top, inkywidth, history_headings_top), linecolor)      # Horizontal heading top line
draw.line((0, history_data_top, inkywidth, history_data_top), linecolor)      # Horizontal data top line
draw.line((0, history_data_middle, inkywidth, history_data_middle), linecolor) # horizontal data divider line
draw.line((0, inkyheight - history_update_size, inkywidth, inkyheight - history_update_size), linecolor)      # Horizontal bottom line

draw.line((history_icon_edge, history_headings_top, history_icon_edge, inkyheight - 20), linecolor) #icon edge
draw.line((quarter_inkywidth + (history_icon_edge / 2), history_headings_top, quarter_inkywidth + (history_icon_edge / 2), inkyheight - 20), linecolor) # first bottom vert
draw.line((half_inkywidth, 0, half_inkywidth, inkyheight - 20), linecolor) # Verticle middle line
draw.line((threequarter_inkywidth, 0, threequarter_inkywidth, inkyheight - 20), linecolor) # third bottom vert

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
sun_icon_filename = icons_path + "icon-sun-bw.png"
windspeed_icon_filename = icons_path + "icon-wind-bw.png"
export_icon_filename = icons_path + "power-export-bw.png"
battery_charging_icon_filename = icons_path + "battery-charging-bw.png"

kWh_condition = foxdataDict['gridConsumptionPower']['unit'] == config['gridloadlimitunit']
draw_condition = foxdataDict['gridConsumptionPower']['value'] > int(config['gridloadlimit'])

if kWh_condition and draw_condition:
	house_icon_filename = icons_path + "house-load.png"
else:
	house_icon_filename = icons_path + "house-load-bw.png"

kWh_condition = foxdataDict['loadsPower']['unit'] == config['houseloadlimitunit']
draw_condition = foxdataDict['loadsPower']['value'] > int(config['houseloadlimit'])
if kWh_condition and draw_condition:
	usage_icon_filename = icons_path + "house-usage.png"
else:
	usage_icon_filename = icons_path + "house-usage-bw.png"

# select the right battery icon for the level

bat_level = "10"

if int(foxdataDict['SoC']['value']) >= 100:
	bat_level = "100-bw"
elif int(foxdataDict['SoC']['value']) >= 90:
	bat_level = "90-bw"
elif int(foxdataDict['SoC']['value']) >= 75:
	bat_level = "75-bw"
elif int(foxdataDict['SoC']['value']) >= 50:
	bat_level = "50-bw"
elif int(foxdataDict['SoC']['value']) >= 25:
	bat_level = "25"

battery_draining_filename = icons_path + "battery-draining-" + bat_level  + ".png"

masks = {}

icon_dictionary = [solar_icon_filename, wind_icon_filename, battery_draining_filename, house_icon_filename, sun_icon_filename, windspeed_icon_filename, usage_icon_filename]
icon_positions = [(2, int(history_data_top) + 5), (2, int(history_data_middle) + 5), (0,1), (int(half_inkywidth) + 1, 1), (int(half_inkywidth) + 1, int(quarter_inkyheight)+11), (int(threequarter_inkywidth)+1, int(quarter_inkyheight)+11), (int(threequarter_inkywidth + 1), 1)]


# Is the battery charging? Add the appropriate icon
if int(foxdataDict['batChargePower']['value']) > 0:
	icon_dictionary.append(battery_charging_icon_filename)
	icon_positions.append((0, int(history_data_top - (icon_size * 2))))

icon_dictionary.append(battery_charging_icon_filename)
icon_positions.append((0, int(history_data_top - (icon_size * 2))))

# Are we feeding in? Add the icon.
if int(foxdataDict['feedinPower']['value']) > 0:
	icon_dictionary.append(export_icon_filename)
	icon_positions.append((int(half_inkywidth - 36), 2))

# Load and place multiple icons
for icon_path, position in zip(icon_dictionary, icon_positions):
    icon = Image.open(icon_path).resize((icon_size, icon_size))  # Resize icons if necessary
    img.paste(icon, position, create_mask(icon))

##################################################
# Battery
font = ImageFont.truetype(HankenGroteskBold, 80)

battery = str(int(foxdataDict['SoC']['value'])) + foxdataDict['SoC']['unit']

_, _, w, batth = font.getbbox(battery)
x = quarter_inkywidth - (w / 2)
y = quarter_inkyheight - (batth / 2) +  5

if foxdataDict['SoC']['value'] < int(config['batterylimit']):
	draw.rectangle((icon_size, 0 + icon_size, half_inkywidth - icon_size, half_inkyheight + 20 - icon_size), fill=inky_display.RED)
	color = inky_display.WHITE
else:
	color = inky_display.BLACK

draw.text((x, y), battery, color, font)


##################################################
# RIGHT SECTION 
font = ImageFont.truetype(HankenGroteskMedium, 22)

grid = str(foxdataDict['gridConsumptionPower']['value']) + foxdataDict['gridConsumptionPower']['unit']
house = str(foxdataDict['loadsPower']['value']) + foxdataDict['loadsPower']['unit']
pvpower = str(foxdataDict['pvPower']['value']) + foxdataDict['pvPower']['unit']

_, _, w, gridh = font.getbbox(grid)
x = history_month_center - (w / 2)
y = 40

kWh_condition = foxdataDict['gridConsumptionPower']['unit'] == config['gridloadlimitunit']
draw_condition = foxdataDict['gridConsumptionPower']['value'] >  int(config['gridloadlimit'])

if kWh_condition and draw_condition:
	draw.rectangle((half_inkywidth, 38, threequarter_inkywidth, 40+gridh+3), fill=inky_display.RED)
	color = inky_display.WHITE
else:
	color = inky_display.BLACK
draw.text((x, y), grid, color, font)

_, _, w, househ = font.getbbox(house)
x = history_year_center - (w / 2)

kWh_condition = foxdataDict['loadsPower']['unit'] == config['houseloadlimitunit']
draw_condition = foxdataDict['loadsPower']['value'] >  int(config['houseloadlimit'])

if kWh_condition and draw_condition:
	draw.rectangle((threequarter_inkywidth, 38, inkywidth, 40+househ+3), fill=inky_display.RED)
	color = inky_display.WHITE
else:
	color = inky_display.BLACK

draw.text((x, y), house, color, font)

_, _, w, househ = font.getbbox(pvpower)
x = history_month_center - (w / 2)
y = 120
draw.text((x, y), pvpower, inky_display.BLACK, font)


wind = str(int(round(float(rippleDataset['latest_wind_speed']['value']), 0))) + rippleDataset['latest_wind_speed']['unit']
_, _, w, windH = font.getbbox(wind)
x =  history_year_center - (w / 2)
draw.text((x, y), wind, inky_display.BLACK, font)


########################
# HISTORICALS

# Column centers
history_datawidth = inkywidth - 40 
day_center = (history_datawidth / 4) + 40
 
# headings

if debug:
	pprint.pprint(foxDataset['historical']['generation'])

# headings

font = ImageFont.truetype(HankenGroteskBold, 18)

heading = "Day"
_, _, w, h = font.getbbox(heading)
x = history_day_center - (w / 2)
y = half_inkyheight + 20
draw.text((x, y), heading, inky_display.BLACK, font)

heading = "Week"
_, _, w, h = font.getbbox(heading)
x = history_week_center - (w / 2)
draw.text((x, y), heading, inky_display.BLACK, font)

heading = "Month"
_, _, w, h = font.getbbox(heading)
x = history_month_center - (w / 2)
draw.text((x, y), heading, inky_display.BLACK, font)

heading = "Year"
_, _, w, h = font.getbbox(heading)
x = history_year_center - (w / 2)
draw.text((x, y), heading, inky_display.BLACK, font)



font = ImageFont.truetype(HankenGroteskBold, 22)

solar_history_height = int(half_inkyheight + 40)
wind_history_height = int(inkyheight - quarter_inkyheight + 10)



solar_yield = str(int(round(foxDataset['historical']['generation']['day_total'], 0))) + foxDataset['historical']['generation']['unit']
_, _, w, h = font.getbbox(solar_yield)
x = history_day_center - (w / 2)
y = half_inkyheight + (h / 2) + 40
draw.text((x, y), solar_yield, inky_display.BLACK, font)

solar_yield = str(int(round(foxDataset['historical']['generation']['month_total'], 0))) + foxDataset['historical']['generation']['unit']
_, _, w, h = font.getbbox(solar_yield)
x = history_month_center - (w / 2)
draw.text((x, y), solar_yield, inky_display.BLACK, font)

solar_yield = str(int(round(foxDataset['historical']['generation']['year_total'], 0))) + foxDataset['historical']['generation']['unit']
_, _, w, solaryh = font.getbbox(solar_yield)
x = history_year_center - (w / 2)
draw.text((x, y), solar_yield, inky_display.BLACK, font)

ripple_yield = rippleDataset['today_saving']['unit'] + str(rippleDataset['today_saving']['value'])
_, _, w, h = font.getbbox(ripple_yield)
x = history_day_center - (w / 2)
y = inkyheight - quarter_inkyheight + (h / 2) + 10

draw.text((x, y), ripple_yield, inky_display.BLACK, font)

ripple_yield = rippleDataset['week_savings']['unit'] + str(rippleDataset['week_savings']['value'])
_, _, w, h = font.getbbox(ripple_yield)
x = history_week_center - (w / 2)
draw.text((x, y), ripple_yield, inky_display.BLACK, font)

ripple_yield = rippleDataset['month_savings']['unit'] + str(rippleDataset['month_savings']['value'])
_, _, w, h = font.getbbox(ripple_yield)
x = history_month_center - (w / 2)
draw.text((x, y), ripple_yield, inky_display.BLACK, font)

ripple_yield = rippleDataset['year_savings']['unit'] + str(rippleDataset['year_savings']['value'])
_, _, w, h = font.getbbox(ripple_yield)
x = history_year_center - (w / 2)
draw.text((x, y), ripple_yield, inky_display.BLACK, font)




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

