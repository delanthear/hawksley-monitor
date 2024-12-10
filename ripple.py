import requests
import json

def getRippleData(apiKey):
    apiURL = "https://rippleenergy.com/rest/member_data/" + apiKey

    rippleData = requests.get(apiURL)
    rippleDataset = json.loads(rippleData.text)

    generationData = rippleDataset['generation_assets'][0]['generation']
    latest_wind_speed = generationData['latest_telemetry']['wind_speed_avg']

    def number_format(value, decimals=2): 
        return f"{value:,.{decimals}f}"

    rippleResults = {
        "latest_wind_speed": {'value': str(round(float(latest_wind_speed), 2)), 'unit': 'mph', 'name': 'Wind Speed'},
        "latest_generation": {'value': generationData['latest']['generation'], 'unit': 'kWh', 'name': 'Current Generation'},
        "today_generation": {'value': generationData['today']['generated'], 'unit': 'kWh', 'name': 'Today Generation'},
        "week_generation": {'value': generationData['this_week']['generated'], 'unit': 'kWh', 'name': 'Week Generation'},
        "month_generation": {'value': generationData['this_month']['generated'], 'unit': 'kWh', 'name': 'Month Generation'},
        "year_generation": {'value': generationData['this_year']['generated'], 'unit': 'kWh', 'name': 'Year Generation'},

        "today_saving": {'value': number_format(generationData['today']['earned'], 2), 'unit': '£', 'name': 'Earnings Today'},
        "week_savings": {'value': number_format(generationData['this_week']['earned'], 2), 'unit': '£', 'name': 'Weekly Earnings'},
        "month_savings": {'value': number_format((generationData['today']['earned'] + generationData['this_month']['earned']), 2), 'unit': '£', 'name': 'Monthly Earnings'},
        "year_savings": {'value': number_format(generationData['this_year']['earned'], 2), 'unit': '£', 'name': 'Yearly Earnings'}
    }
    return rippleResults;
