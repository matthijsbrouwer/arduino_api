# Control Arduino using API

<img align="right" src="../master/images/arduino.jpeg?raw=true">

Demonstrate use of an API to get and set status of an Arduino board and
enable and adjust a program to also do this automatically.

## Setup Arduino

Connections:

- LED1 to pin 12 (Digital Out)
- LED2 to pin 13 (Digital Out)
- BUTTON1 to pin 11 (Digital In)
- SENSOR1 to pin 0 (Analog In)

In this test setup, the leds and button from an Arduino Shield were used for 
LED1, LED2 and BUTTON1. 

The SENSOR1 signal was simulated by using a potentiometer as 
a voltage divider.

The [api software](arduino/api/api.ino) was uploaded to the Arduino Board. This
software listens to the serial port for incoming request from the Python application, processes
received instructions, reports changes in status of the button, handles measurements with the sensor, 
updates the internal clock and manages (if enabled) the processing of the automatic program. 

## Server

Start the [server](server/server.py) with

```
python server/server.py
```

The server tries to detect automatically the COM-port used by the Arduino board and starts a connection.

Then two processes are started:

<img align="right" src="../master/images/api.png?raw=true">

- A process to monitor data sent from the board. This data is used to update the status of LED1, LED2 and BUTTON in variables also available to the other process. Also, on initialization, a timestamp is sent to the board, enabling synchronization of an automatically updated internal clock variable, and thereby for allowing the use of the current time in returning measurements and defining the automatic program (although this has not been implemented) 

- A process running a Flask based providing an [REST API](http://localhost:5000/api/) to get and/or set status of leds and button, do measurements with the sensor and enable and adjust a program to do this automatically. 
    
The server also hosts an html/javascript based [demonstrator](http://localhost:5000/) to test and illustrate use of the [REST API](http://localhost:5000/api/).


## Demonstrator

Using jQuery based javascript, the status of the board is periodically checked from the [REST API](http://localhost:5000/api/) with AJAX requests. This makes it possible to display the current status of leds, button and sensor.   

<img src="../master/images/manual.png?raw=true">

The buttons LED1 and LED2 trigger the right functions to perform again AJAX calls to the API to change the status of the leds. The MEASUREMENT button let the board register the value measured on the incoming SENSOR1 port, and this value is reported back together with the time and status of leds and button.

<img src="../master/images/measurements.png?raw=true">



