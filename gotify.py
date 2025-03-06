from datetime import datetime

import requests
import json
import time

def sendGotifyMessage(token, address, notificationKey, title, message, priority=5):

    # check if we've sent one yet    
    if should_send_notification(notificationKey):
        
        gotifyURL = address + "/message?token=" + token

        fields = {
            "title": title,
            "message": message,
            "priority": priority 
        }

        # Send the POST request with the fields
        response = requests.post(gotifyURL, data=fields)

        # Print the response
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        save_last_notification_date(notificationKey)  # Save today's date after sending notification

        return(response)

# Function to read the last notification dates from the file
def get_last_notification_dates():
    try:
        with open('last_notification.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file does not exist, return an empty dictionary
        return {}

# Function to save the current dates for notifications
def save_last_notification_date(notification_name):
    data = get_last_notification_dates()
    data[notification_name] = datetime.today().strftime('%Y-%m-%d')
    with open('last_notification.json', 'w') as file:
        json.dump(data, file)

# Function to check if a specific notification has already been sent today
def should_send_notification(notification_name):
    current_date = datetime.today().strftime('%Y-%m-%d')
    last_notification_dates = get_last_notification_dates()

    if last_notification_dates.get(notification_name) != current_date:
        # If the last notification date for this name is not today's date, allow sending
        return True
    else:
        # Otherwise, don't send it
        return False
