import urllib2 as ul
import json
import time
import os
from w1thermsensor import W1ThermSensor
import logging

lastConnectionTime = time.time() # Track the last connection time
lastUpdateTime = time.time() # Track the last update time
postingInterval = 120 # Post data once every 2 minutes
updateInterval = 60 # Update once every 15 seconds

writeAPIkey = "API_KEY" # Replace YOUR-CHANNEL-WRITEAPIKEY with your channel write API key
channelID = "CHANNEL_ID" # Replace YOUR-CHANNELID with your channel ID
url = "https://api.thingspeak.com/channels/"+channelID+"/bulk_update.json" # ThingSpeak server settings
messageBuffer = [] # Buffer to hold the data

logging.basicConfig(level=logging.DEBUG)

def httpRequest():
    '''Function to send the POST request to 
    ThingSpeak channel for bulk update.'''

    global messageBuffer
    logging.info("httpRequest called")
    data = json.dumps({'write_api_key':writeAPIkey,'updates':messageBuffer}) # Format the json data buffer
    req = ul.Request(url = url)
    requestHeaders = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)","Content-Type":"application/json","Content-Length":str(len(data))}
    for key,val in requestHeaders.iteritems(): # Set the headers
        req.add_header(key,val)
    req.add_data(data) # Add the data to the request
    # Make the request to ThingSpeak
    try:
        response = ul.urlopen(req) # Make the request
        logging.info(response.getcode()) # A 202 indicates that the server has accepted the request
    except ul.HTTPError as e:
        logging.info(e.code) # Print the error code
    messageBuffer = [] # Reinitialize the message buffer
    global lastConnectionTime
    lastConnectionTime = time.time() # Update the connection time

def getData():
    '''Function that returns the CPU temperature and percentage of CPU utilization'''
    sensor_outside = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "00000550ff55")
    temp_outside = sensor_outside.get_temperature()
    logging.info("Temperature outside " + str(temp_outside))
    sensor_out = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "000005512327")
    temp_out = sensor_out.get_temperature()
    logging.info("Temperature water out " + str(temp_out))
    sensor_in = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "0000054ff75c")
    temp_in = sensor_in.get_temperature()
    logging.info("Temperature water in " + str(temp_in))
    return temp_outside, temp_in, temp_out

def updatesJson():
    '''Function to update the message buffer
    every 15 seconds with data. And then call the httpRequest 
    function every 2 minutes. This examples uses the relative timestamp as it uses the "delta_t" parameter. 
    If your device has a real-time clock, you can also provide the absolute timestamp using the "created_at" parameter.
    '''

    global lastUpdateTime
    logging.info("updatesJson called")
    message = {}
    message['delta_t'] = time.time() - lastUpdateTime
    outside, temp_in, temp_out = getData()
    message['field1'] = outside
    message['field2'] = temp_in
    message['field3'] = temp_out
    global messageBuffer
    messageBuffer.append(message)
    # If posting interval time has crossed 2 minutes update the ThingSpeak channel with your data
    if time.time() - lastConnectionTime >= postingInterval:
        httpRequest()
    lastUpdateTime = time.time()

if __name__ == "__main__":  # To ensure that this is run directly and does not run when imported 
    logging.info("Starting temperature measure main loop")
    while 1:
        try:
            getData()
            if time.time() - lastUpdateTime >= updateInterval:
                updatesJson()
            time.sleep(5)
        except Exception as e:
            logging.exception("Exception in main loop")
