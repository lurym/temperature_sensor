import requests
import json
import time
import os
from w1thermsensor import W1ThermSensor
import logging
import config

posting_interval = 120	# Post data once every 2 minutes
update_interval = 60	# Update once every 60 seconds

url = "https://api.thingspeak.com/channels/"+config.channel_id+"/bulk_update.json" # ThingSpeak server settings

logging.basicConfig(level=logging.DEBUG)

def http_request(message_buffer):
    '''Function to send the POST request to 
    ThingSpeak channel for bulk update.'''

    logging.info("http_request called")
    data = json.dumps({'write_api_key':config.write_api_key,'updates':message_buffer})
    request_headers = {"User-Agent":"mw.doc.bulk-update (Raspberry Pi)", "Content-Type":"application/json","Content-Length":str(len(data))}
    response = requests.post(url, data, headers=request_headers)
    logging.info("status code of the response " + str(response.status_code))

    message_buffer.clear()

def getData():
    '''Function that returns the data about sensors'''
    results = []
    for sensor in W1ThermSensor.get_available_sensors():
        temperature = sensor.get_temperature()
        id = sensor.id
        temperature_string = str(temperature)
        logging.info("Temperature " + id + " value " + temperature_string)
        results.append(temperature)
    return results

def update_json(last_update_time, message_buffer):
    '''Function to update the message buffer
    every 60 seconds with data. 
    '''

    logging.info("update_json called")
    message = {}
    message['delta_t'] = str(int(round(time.time() - last_update_time)))
    temperatures = getData()
    for i, temp in enumerate(temperatures):
    	message['field' + str(i+1)] = temp
    message_buffer.append(message)

if __name__ == "__main__":  # To ensure that this is run directly and does not run when imported 
    logging.info("Starting temperature measure main loop")
    message_buffer 		= []
    last_update_time 		= time.time()
    last_connection_time 	= time.time()
    update_json(last_update_time, message_buffer)
    http_request(message_buffer)
    while 1:
        try:
            if time.time() - last_update_time >= update_interval:
                update_json(last_update_time, message_buffer)
                last_update_time = time.time()
	    # If posting interval time has crossed 2 minutes update the ThingSpeak channel with your data
            if time.time() - last_connection_time >= posting_interval:
                http_request(message_buffer)
                last_connection_time = time.time()
            time.sleep(5)
        except Exception as e:
            logging.exception("Exception in main loop")
