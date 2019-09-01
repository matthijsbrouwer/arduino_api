# Control Arduino using API

<img align="right" src="../master/images/arduino.jpeg?raw=true">

Demonstrate the use of an API to

- Get and set status of components connected to an Arduino board
- Perform measurements with a sensor connected to the board
- Enable and adjust a program on the board to also do this automatically

## Arduino

An [Arduino Board](https://www.arduino.cc/) is used to connect several components. In this demonstrator 
setup, the leds and button from an Arduino Shield are used as LED1, LED2 and BUTTON1, and 
the SENSOR1 signal is simulated by using a potentiometer as a voltage divider.

Connections:

- LED1 to pin 12 (Digital Out)
- LED2 to pin 13 (Digital Out)
- BUTTON1 to pin 11 (Digital In)
- SENSOR1 to pin 0 (Analog In)

The [api software](arduino/api/api.ino), based on this setup, has to be uploaded to the Arduino Board. 
Adjusting the software to support other or more components should not be too difficult, but will 
probably very project specific.

## Architecture
 
The uploaded software lets the Arduino listen to the serial port for incoming request from the Python application, processes received instructions, reports changes in status of the button, 
handles measurements with the sensor, updates the internal clock and manages (if enabled) 
the processing of the automatic program. 

<img src="../master/images/scheme.jpeg?raw=true">

A Python application communicates with the Arduino over the serial port based on the implemented protocol. 
This Python application does also provide a webserver that can be accessed over a network (although exposing this service directly to the full internet is strongly discouraged) using a browser.

## Python application

Start the Python based [server](server/server.py) with

```
python server/server.py
```

The application tries to detect automatically the COM-port used by the Arduino board and starts a connection.

Then two processes are started:

<img width="200" align="right" src="../master/images/api.png?raw=true">

- A process to monitor data sent from the board. This data is used to update the status of LED1, LED2 and BUTTON in variables also available to the other process. Also, on initialization, a timestamp is sent to the board, enabling synchronization of an automatically updated internal clock variable, and thereby for allowing the use of the current time in returning measurements and defining the automatic program (although this has not been implemented) 

- A process running a Flask based providing an [REST API](http://localhost:5000/api/) to get and/or set status of leds and button, do measurements with the sensor and enable and adjust a program to do this automatically. 


## Demonstrator

The Flask based server also hosts an html/javascript based [demonstrator](http://localhost:5000/) to test and illustrate use of the [REST API](http://localhost:5000/api/). Using jQuery based javascript, the status of the board is periodically checked from the [REST API](http://localhost:5000/api/) with AJAX requests. This makes it possible to display the current status of leds, button and sensor.   

<img width="350" src="../master/images/manual.png?raw=true">

The buttons LED1 and LED2 trigger functions to perform again AJAX calls to the API to change the status of the leds. The MEASUREMENT button lets the board register the value measured on the incoming SENSOR1 port, and this value is reported back together with the time and status of leds and button. Measurements
are automatically displayed in the browser.

<img width="600" src="../master/images/measurements.png?raw=true">

By using the MODUS button, the operation of the Arduino can be changed from MANUAL to AUTOMATIC. When the automatic program is enabled, the board does periodically enables and disables the leds and performs 
measurements based on configured parameters. 

<img width="350" src="../master/images/automatic.png?raw=true">

The configured parameters for this program can be adjusted using the API.

<img width="350" src="../master/images/program.png?raw=true">

## Storage

TODO






