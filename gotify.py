from datetime import datetime

import requests
import json
import time

def sendGotifyMessage(token, address, title, message, priority=5):

    # check if we've sent one yet    
    if should_send_notification():
        
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
        
        save_last_notification_date()  # Save today's date after sending notification

        return(response)

# Function to read last notification date from the file
def get_last_notification_date():
    try:
        with open('last_notification.json', 'r') as file:
            data = json.load(file)
            return data.get('date')
    except FileNotFoundError:
        # If the file does not exist, return None (first time running)
        return None

# Function to save the current date as the last notification date
def save_last_notification_date():
    with open('last_notification.json', 'w') as file:
        json.dump({'date': datetime.today().strftime('%Y-%m-%d')}, file)


# Function to check if the notification has already been sent today
def should_send_notification():
    current_date = datetime.today().strftime('%Y-%m-%d')
    last_notification_date = get_last_notification_date()

    if last_notification_date != current_date:
        # If last notification date is not today's date, allow sending the notification
        return True
    else:
        # Otherwise, don't send it
        return False
