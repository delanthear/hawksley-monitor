# hawksley-monitor
A set of Python scripts for pulling solar data from FoxESS and Ripple API and displaying on an inkyPhat and inkyWhat

+ monitor-what.py - Script for displaying data on the inkyWhat
+ monitor-phat.py - Script for displaying data on the inkyPhat
+ fox.py - Script for connecting to the FoxESS API
+ ripple.py - Script for connecting to the Ripple API

## Set Up
1. Choose which file you want:  monitor-what.py or monitor-phat.py depending on if you have a wHat or a pHat.
2. Add your Fox API key and serial number and Ripple API key to the configj JSON file
3. Specify the limits you want in the config file for when to highlight breaches in the display
4. Run the required monitor script with Python.
5. If all works, cron it up so it updates to your taste.

Remember, the data isn't realtime and your Inky has a lifespan so updating too frequently will expire it!  Don't be overzealous
