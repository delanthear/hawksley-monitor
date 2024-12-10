import hashlib
import time
from datetime import datetime
import pprint
import json
import requests 
from requests.auth import HTTPBasicAuth

last_call = {}          # timestamp of the last call for a given path
response_time = {}      # response time in seconds of the last call for a given path
query_delay = 1         # minimum time between calls in seconds
lang = "en"
time_zone = "Europe/London"
user_agent = "Hawksley Dash v2"
foxessapi = "https://www.foxesscloud.com";
api_key = "ADD YOUR API KEY";
serial = "ADD YOUR SERIAL NUMBER";
path = "/op/v0/device/real/query"

def signed_header(path):
    global api_key, user_agent, time_zone, lang
    headers = {}
    token = api_key
    t_now = time.time()
    if 'query' in path:
        t_last = last_call.get(path)
        delta = t_now - t_last if t_last is not None else query_delay
        if delta < query_delay:
            time.sleep((query_delay - delta))
        t_now = time.time()
    last_call[path] = t_now
    timestamp = str(round(t_now * 1000))
    headers['Token'] = token
    headers['Lang'] = lang
    headers['User-Agent'] = user_agent
    headers['Timezone'] = time_zone
    headers['Timestamp'] = timestamp
    headers['Content-Type'] = 'application/json'
    headers['Signature'] = hashlib.md5(fr"{path}\r\n{headers['Token']}\r\n{headers['Timestamp']}".encode('UTF-8')).hexdigest()
    return headers

def getRealTimeFoxData():

	post_query = {  'sn': serial, 
			'variables': ['SoC', 'pvPower', 'loadsPower', 'gridConsumptionPower', 'feedinPower', 'batChargePower']
	}

	# post_query = { 'sn': serial }
	headers = signed_header(path)
	response = requests.post(foxessapi + path, headers=headers, json=post_query)

	return json.loads(response.text)

def getHistoricalFoxData():

	global foxessapi
	global api_key
	global serial

	# Find the current month index
	datetime_now = datetime.now()
	year = datetime_now.year
	month = datetime_now.month
	day = datetime_now.day

	month_index = month - 1

	path = "/op/v0/device/report/query";

	headers = signed_header(path)
	post_query = {
		'sn': serial,
		'year': year,
		'dimension': 'year',
		'variables':  ["generation","feedin","gridConsumption"]
	}

	response = requests.post(foxessapi + path, headers=headers, json=post_query)

	historicalData = json.loads(response.text)
	historicalData = historicalData['result']

	headers = signed_header(path)
	post_query = {
		'sn': serial,
		'year': year,
		'month': month,
		'day': day,
		'dimension': 'day',
		'variables': ["generation", "feedin", "gridConsumption"]
	}

	response = requests.post(foxessapi + path, headers=headers, json=post_query)
	hourly_data = json.loads(response.text)

	hourly_data =  hourly_data['result']
	day_totals = {}

	# Iterate over the results and calculate totals
	for entry in hourly_data:
		variable = entry["variable"]
		values = entry["values"]
		total = sum(values)  # Sum up the values for this variable
		day_totals[variable] = total  # Store the total in the dictionary

	fox_history_data = {}

	for variable in historicalData:
		label = variable['variable']

		year_total = 0
		month_data = 0

		# Add up the totals for the year and pull out the current month's data
		for key, value in enumerate(variable["values"]):
			if key == month_index:
				month_data = value
			year_total += value

		# Determine the name based on the label
		name = ""
		if label == "generation":
			name = "Solar Generation"
		elif label == "feedin":
			name = "Feed In"
		elif label == "gridConsumption":
			name = "House Consumption"

		# Populate the `fox_history_data` dictionary
		fox_history_data[label] = {
			"unit": variable['unit'],
			"name": name,
			"day_total": day_totals[label],
			"month_total": month_data,
			"year_total": year_total
		}


 	return fox_history_data

def getfoxData():
	totaldataset = {};
	totaldataset['realtime'] = getRealTimeFoxData()
	totaldataset['historical'] = getHistoricalFoxData()
	return(totaldataset);

# Uncomment this lines to be able to run the script on it's own

# dataset = getfoxData()
# pprint.pprint(dataset)
