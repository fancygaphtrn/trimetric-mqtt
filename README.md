# trimetric-mqtt
Trimetric solar meter data logging

Read serial data from a Trimetic meter and publich to MQTT.  Using Rasperry pi.

I switched to using an ESP8266 and ESPhome.   I am including the files here.

### Getting started

* I installed in a python3 virtualenv using Python 3
* Uses [paho.mqtt](https://pypi.org/project/paho-mqtt/#client)
* Uses pyserial
* A custom cable to interface the 5v Trimetric serial output to the 3.3V Raspberry pi GPIO
![Custom cable schematic](https://github.com/fancygaphtrn/trimetric-mqtt/blob/master/Custom%20cable.png)
* Read TM2025-TM2030 Technical Information On Serial Data Output_0.pdf

#### Home Assistant configuration.yaml Example

```
sensor:
  - platform: mqtt
    name: Trimetric Volts
    state_topic: "trimetric/trimetric/V"
    unit_of_measurement: 'V'
  - platform: mqtt
    name: Trimetric Filtered Volts
    state_topic: "trimetric/trimetric/FV" 
    unit_of_measurement: 'V'
  - platform: mqtt
    name: Trimetric Amps
    state_topic: "trimetric/trimetric/A" 
    unit_of_measurement: 'A'
  - platform: mqtt
    name: Trimetric Filtered Amps
    state_topic: "trimetric/trimetric/FA"
    unit_of_measurement: 'A'
  - platform: mqtt
    name: Trimetric Amp Hours from full
    state_topic: "trimetric/trimetric/AH" 
    unit_of_measurement: 'AH'
  - platform: mqtt
    name: Trimetric Charge State
    state_topic: "trimetric/trimetric/%" 
    unit_of_measurement: '%'
  - platform: mqtt
    name: Trimetric Watts
    state_topic: "trimetric/trimetric/W"
    unit_of_measurement: 'W'
  - platform: mqtt
    name: Trimetric Days Since Charged
    state_topic: "trimetric/trimetric/DSC"
    unit_of_measurement: Days
  - platform: mqtt
    name: Trimetric Days Since Equalized
    state_topic: "trimetric/trimetric/DSE"
    unit_of_measurement: 'Days'
  - platform: mqtt
    name: Trimetric X
    state_topic: "trimetric/trimetric/X"
```

#### Home Assistant lovelace.yaml Example

```
  - title: Solar
    cards:
      - type: entities
        title: Solar
        show_header_toggle: false
        entities:
          - sensor.trimetric_volts
          - sensor.trimetric_filtered_volts
          - sensor.trimetric_amps
          - sensor.trimetric_filtered_amps
          - sensor.trimetric_amp_hours_from_full
          - sensor.trimetric_watts
          - sensor.trimetric_charge_state
          - sensor.trimetric_days_since_charged
          - sensor.trimetric_days_since_equalized
          - sensor.trimetric_x
      - type: history-graph
        hours_to_show: 48
        refresh_interval: 10
        entities:
          - sensor.trimetric_volts
          - sensor.trimetric_filtered_volts
          - sensor.trimetric_amps
          - sensor.trimetric_filtered_amps
          - sensor.trimetric_amp_hours_from_full
          - sensor.trimetric_watts

```

### References

* [trimetric](http://www.bogartengineering.com/products/trimetrics.html) Trimetric meter
![Trimetric TM2030-RV](https://github.com/fancygaphtrn/trimetric-mqtt/blob/master/TM-2030-RV-1-300x300.jpg)
* [Adafruit](https://www.adafruit.com/product/954) TTL to USB serial port.   May still require a RJ-11 breakout cable.
![TTL to USB serial](https://github.com/fancygaphtrn/trimetric-mqtt/blob/master/TTL-to-USBserial.jpg)
