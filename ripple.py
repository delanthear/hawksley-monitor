import requests
from datetime import datetime, timezone, timedelta

def getRippleData(apiKey):
    apiURL = "https://dashboard.kirkhillcoop.org/api/v1/generation?range=ytd&scope=owner"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + apiKey
    }

    rippleData = requests.get(apiURL, headers=headers)
    rippleDataset = rippleData.json()

    generationData = rippleDataset["data"]["series"]
    
    now = datetime.now(timezone.utc)

    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    total_today = 0
    total_week = 0
    total_month = 0
    total_year = 0

    for item in generationData:
        timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
        value = item["generation_kwh"]

        if timestamp.date() == today:
            total_today += value

        if timestamp.date() >= week_start:
            total_week += value

        if timestamp.date() >= month_start:
            total_month += value

        if timestamp.date() >= year_start:
            total_year += value

    apiURL = "https://dashboard.kirkhillcoop.org/api/v1/current?scope=owner"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + apiKey
    }

    rippleData = requests.get(apiURL, headers=headers)
    rippleDataset = rippleData.json()

    
    latest_wind_speed = rippleDataset["data"]["summary"]["wind_speed_mps"]
    

    def number_format(value, decimals=2):
        return f"{value:,.{decimals}f}"

    rippleResults = {
        "latest_wind_speed": {'value': str(round(float(latest_wind_speed), 2)), 'unit': 'mph', 'name': 'Wind Speed'},
        "today_generation": {'value': number_format(total_today), 'unit': 'kWh', 'name': 'Today Generation'},
        "week_generation": {'value': number_format(total_week), 'unit': 'kWh', 'name': 'Week Generation'},
        "month_generation": {'value': number_format(total_month), 'unit': 'kWh', 'name': 'Month Generation'},
        "year_generation": {'value': number_format(total_year), 'unit': 'kWh', 'name': 'Year Generation'},
    }
    return rippleResults

