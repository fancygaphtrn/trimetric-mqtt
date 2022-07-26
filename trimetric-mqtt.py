#!/usr/bin/python3
import datetime, time
import logging
import json
import paho.mqtt.client as mqtt
import serial

log = logging.getLogger()
log.setLevel(logging.INFO)
#if (log.hasHandlers()):
#    log.handlers.clear()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

log.info('Starting')

MQTTHOST = "home.lan"
MQTTPORT = 1883
COUNTER = 1

# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect(client, userdata, flags, rc):
    log.info("MQTT Connected with result code "+str(rc))

def mqtt_on_disconnect(client, userdata, rc):
    log.info("MQTT Disconnected with result code "+str(rc))

def mqtt_on_log(client, userdata, level, buf):
    log.debug("MQTT "+buf)


mqtt_server = mqtt.Client("",True)
mqtt_server.on_connect = mqtt_on_connect
mqtt_server.on_disconnect = mqtt_on_disconnect
#mqtt_server.on_message = mqtt_on_message
mqtt_server.on_log = mqtt_on_log

mqtt_server.connect(MQTTHOST, MQTTPORT, 60)
mqtt_server.loop_start()

ser = serial.Serial('/dev/ttyAMA0', 2400, timeout=5)

#Let the uart and trimeter get synced after open and clear the buffer.  Sometimes get garbage
b = ser.read(5)

b = ser.read(125)
s = b.decode('utf-8')

start = s.find(",V=")
buffer = s[start:]

#print("buffer ", buffer)

previous =	{
  "V": "0",
  "FV": "0",
  "V2": "0",
  "A": "0",
  "FA": "0",
  "PW": "0",
  "AH": "0",
  "%": "0",
  "W": "0",
  "FW": "0",
  "DSC": "0",
  "DSE": "0",
  "X": "0",
  "W_IN": "0",
  "W_OUT": "0",
  "FW_IN": "0",
  "FW_OUT": "0",
}
def reset_previous():
  previous["V"] = 0
  previous["FV"] = 0
  previous["V2"] = 0
  previous["A"] = 0
  previous["FA"] = 0
  previous["PW"] = 0
  previous["AH"] = 0
  previous["%"] = 0
  previous["W"] = 0
  previous["FW"] = 0
  previous["DSC"] = 0
  previous["DSE"] = 0
  previous["X"] = 0
  previous["W_IN"] = 0
  previous["W_OUT"] = 0
  previous["FW_IN"] = 0
  previous["FW_OUT"] = 0

def publish(topic,value):

    if topic == "%":
        value = '{:3.0f}'.format(float(value))
    elif topic == "W":
        value = float(previous['V']) * float(previous['A'])
        value = '{:3.0f}'.format(float(value))
    elif topic == "FW":
        value = float(previous['FV']) * float(previous['FA'])
        value = '{:3.0f}'.format(float(value))
    elif topic == "W_IN":
        if float(previous['W']) > 0:
            value = float(previous['W'])
            value = '{:3.0f}'.format(float(value))
        else:
            value = 0
            value = '{:3.0f}'.format(float(value))
    elif topic == "W_OUT":
        if float(previous['W']) < 0:
            value = abs(float(previous['W']))
            value = '{:3.0f}'.format(float(value))
        else:
            value = 0
            value = '{:3.0f}'.format(float(value))
    elif topic == "FW_IN":
        if float(previous['FW']) > 0:
            value = float(previous['FW'])
            value = '{:3.0f}'.format(float(value))
        else:
            value = 0
            value = '{:3.0f}'.format(float(value))
    elif topic == "FW_OUT":
        if float(previous['FW']) < 0:
            value = abs(float(previous['FW']))
            value = '{:3.0f}'.format(float(value))
        else:
            value = 0
            value = '{:3.0f}'.format(float(value))
        
    elif topic == "PW":
        value = value
    elif topic == "X":
        value = value
    elif topic == "DSC":
        value = '{:3.1f}'.format(float(value))
    elif topic == "DSE":
        value = '{:3.1f}'.format(float(value))
    else:
        value = '{:2.1f}'.format(float(value))
    
    if previous[topic] != value:
        mqtt_server.publish("trimetric/trimetric/" + topic, value, qos=0, retain=False)
        previous[topic] = value

counter = COUNTER
previous_time = datetime.datetime.now()
        
while 1:
    b = ser.read(125)
    s = b.decode('utf-8')
   
    buffer = buffer + s
    #print("buffer ", buffer)

    next = buffer.find(",V=",1)
    #print("next ", next)

    if datetime.datetime.now() - previous_time >= datetime.timedelta(seconds=60):
        log.info("Resetting previous values")
        previous_time = datetime.datetime.now()
        reset_previous()

    while next > -1:

        # A line should look like this V=25.3,FV=25.2,V2=00.0,A=00.5,FA=00.4,PW=2FF,AH=-0.08,%=100,W=12.1,DSC=3.84,DSE=3.84,PW=2FF
        # periodically you will get    V=25.3,FV=25.2,V2=00.0,A=00.5,FA=00.4,PW=2FF,AH=-0.08,%=100,W=12.1,DSC=3.84,DSE=3.84,PW=2FF,X=28A

        line = buffer[1:next] + ",FW=0,W_IN=0,W_OUT=0,FW_IN=0,FW_OUT=0"
        log.info("Line: %s" % (line))
        
        #skip messages as a way to rate limit
        if counter == 0:
            log.info("Publishing changes")
            e = line.split(",")
            for x in e:
                m = x.split("=")
    
                publish(m[0], m[1])
            counter = COUNTER
        else:
            counter -= 1
            
        buffer = buffer[next:]
        next = buffer.find(",V=",1)
        #print("buffer ", buffer)

ser.close() # Only executes once the loop exits




log.info('Ending')
