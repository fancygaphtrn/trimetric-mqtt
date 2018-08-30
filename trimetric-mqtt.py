#!/srv/trimetric/bin/python3
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
COUNTER = 5

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
  "DSC": "0",
  "DSE": "0",
  "X": "0",
}

def publish(topic,value):

    if topic == "%":
        value = '{:3.0f}'.format(float(value))
    elif topic == "W":
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
        
while 1:
    b = ser.read(125)
    s = b.decode('utf-8')
   
    buffer = buffer + s
    #print("buffer ", buffer)

    next = buffer.find(",V=",1)
    #print("next ", next)
    while next > -1:

        # A line should look like this V=25.3,FV=25.2,V2=00.0,A=00.5,FA=00.4,PW=2FF,AH=-0.08,%=100,W=12.1,DSC=3.84,DSE=3.84,PW=2FF
        # periodically you will get    V=25.3,FV=25.2,V2=00.0,A=00.5,FA=00.4,PW=2FF,AH=-0.08,%=100,W=12.1,DSC=3.84,DSE=3.84,PW=2FF,X=28A

        line = buffer[1:next]
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
