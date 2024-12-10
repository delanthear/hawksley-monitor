# hawksley-monitor
A set of Python scripts for pulling solar data from FoxESS and Ripple API and displaying on an inkyPhat and inkyWhat

monitor-what.py - Script for displaying data on the inkyWhat
monitor-phat.py - Script for displaying data on the inkyPhat (not provided yet)

fox.py - Script for connecting to the FoxESS API
ripple.py - Script for connecting to the Ripple API

=== Set Up ===
1. Go into monitor script and add your Ripple API key
2. Go into the fox.py script and add your Fox API key and serial number.
3. Run the required monitor script with Python.
4. If all works, cron it up so it updates to your taste.

Remember, the data isn't realtime and your Inky has a lifespan so updating too frequently will expire it!  Don't be overzealous

