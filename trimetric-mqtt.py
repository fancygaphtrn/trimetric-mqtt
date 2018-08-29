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
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
log.addHandler(ch)

log.info('Starting')

MQTTHOST = "home.lan"
MQTTPORT = 1883

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

#Let the uart and trimeter get synced after open and clear the buffer.
b = ser.read(5)

b = ser.read(125)
s = b.decode('utf-8')

start = s.find(",V=")
buffer = s[start:]

#print("buffer ", buffer)

while 1:
    b = ser.read(125)
    s = b.decode('utf-8')
   
    buffer = buffer + s
    #print("buffer ", buffer)

    next = buffer.find(",V=",1)
    #print("next ", next)
    while next > -1:
        line = buffer[1:next]
        log.info("Line: %s" % (line))

        e = line.split(",")
        #print("e ", e)
        for x in e:
            #print("x ", x)
            m = x.split("=")
            #print("m ", m)
           
            mqtt_server.publish("trimetric/trimetric/" + m[0], m[1], qos=0, retain=False)


        
        buffer = buffer[next:]
        next = buffer.find(",V=",1)
        #print("buffer ", buffer)

ser.close() # Only executes once the loop exits




log.info('Ending')
