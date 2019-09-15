# Control Arduino using API

<img align="right" src="../master/images/arduino.jpeg?raw=true">

Demonstrate implementation and use of an API to

- Get and set status of components connected to an Arduino board
- Perform measurements with a sensor connected to the board
- Enable and adjust a program on the board to also do this automatically
- Store measurements on the filesystem or in [eLABJournal](https://www.elabjournal.com/)

## Arduino

An [Arduino board](https://www.arduino.cc/) is used to connect several components. In this demonstrator 
setup, the leds and button from an Arduino Shield are used as LED1, LED2 and BUTTON1, and 
the SENSOR1 signal is simulated by using a potentiometer as a voltage divider.

Connections used on the board:

- LED1 to pin 12 (Digital Out)
- LED2 to pin 13 (Digital Out)
- BUTTON1 to pin 11 (Digital In)
- SENSOR1 to pin 0 (Analog In)

The [api software](arduino/api/api.ino), based on this setup, has to be uploaded to the board. 
Adjusting the software to support other or more components should not be too difficult, but 
detailed specifications are probably project specific. This implementation only aims at illustrating
what is possible.

## Architecture
 
The uploaded software lets the Arduino listen to the serial port for incoming request from the Python application, processes received instructions, reports changes in status of the button, 
handles measurements with the sensor, updates the internal clock and manages (if enabled) 
the processing of the automatic program. 

<img src="../master/images/scheme.jpeg?raw=true">

A Python application communicates with the Arduino over the serial port based on the implemented protocol. 
This Python application does also provide a webserver that can be accessed over a network (although exposing this service directly to the full internet is strongly discouraged) using a browser. Finally storage of the measurements on the filesystem or externally in an eLABJournal experiment is also handled
by this application. 

## Python application

Start the Python based [server](server/server.py) with

```
python server/server.py
```

The application tries to detect automatically the COM-port used by the Arduino board and starts a connection.

Then three processes are started:

<img width="200" align="right" src="../master/images/api.png?raw=true">

- A process to monitor data sent from the board. This data contains the current status of LED1, LED2 
and BUTTON1, and is stored in variables also available to the other process. Also, on initialization, a timestamp is sent to the board, enabling synchronization of an automatically updated internal clock variable on the board, and thereby for allowing the use of the current time in returning measurements and defining the automatic program (although this has not been implemented yet) 

- A process running a Flask based providing an [REST API](http://localhost:5000/api/) to get and/or set status of leds and button, do measurements with the sensor and enable and adjust a program to do this automatically. By default this webserver is made available on localhost port 5000.

- A process handling the storage of measurements on the filesystem or in a configured eLABJournal 
experiment.

## Demonstrator

The Flask based server also hosts an html/javascript based [demonstrator](http://localhost:5000/) to test and illustrate use of the [REST API](http://localhost:5000/api/). Using jQuery based javascript, the status of the board is periodically checked by calling the [REST API](http://localhost:5000/api/) with AJAX requests. This allows the demonstrator to update and display the current status of leds, button and sensor to the user.   

<img width="350" src="../master/images/manual.png?raw=true">

The buttons LED1 and LED2 trigger functions to perform again AJAX calls to the API, resulting in a change of status for the leds. The MEASUREMENT button let the board register the value measured on the incoming SENSOR1 port, and this value is reported back together with the time and status of leds and button. These measurements are displayed in the browser.

<img width="600" src="../master/images/measurements.png?raw=true">

## Automatically

By using the MODUS button, the operation of the Arduino can be changed from MANUAL to AUTOMATIC. When the automatic program is enabled, the board periodically enables and disables the leds and performs 
measurements based on configured parameters. 

<img width="350" src="../master/images/automatic.png?raw=true">

The necessary operations will often be very project specific. For this demonstrator a program is implemented containing one or multiple cycles with a configurable period, configurable start/stop times within this cycle for both leds, and configurable measurement time within the cycle. 
Furthermore the number of cycles is configurable, and the optional delay after these cycles. 

<img width="600" src="../master/images/timeline.jpeg?raw=true">

Once all cycles and the delay have been finished, the program starts again from the beginning. The configured parameters for this program can be adjusted, again based on API calls.

<img width="350" src="../master/images/program.png?raw=true">

As stated before, project specific implementations of such programs are probably not too difficult
to implement.

## Storage

Measurements can be stored automatically or manually on the filesystem in CSV-format. For the automatic
storage, a configurable interval is used to check for new measurements.

<img width="350" src="../master/images/storage_interval.png?raw=true">

The data is stored in CSV-format with a filename containing date and time based on the start of the Python application. Data can also be stored in a configured eLABJournal experiment. New measurements are added periodically or after a specific instruction by the storage process. 

Again, this implementation is a proof-of-concept. Other storage procedures or repositiories can be 
implemented that may better suit project or organisation requirements.

## Example

Using the demonstrator interface, the Arduino is instructed to perform automatic measurements.

<img width="350" src="../master/images/storage_measurements.png?raw=true">

The storage is configured to store both on the filesystem and in an eLABJournal experiment.

<img width="350" src="../master/images/storage_settings.png?raw=true">

After manually starting the storage process (by using the *storage* button above the measurements), the
measurements are stored and disappear from the demonstrator interface.

A file `data/arduino_2019-09-15_08:54:25.csv` is created, containing the data in CSV-format.

```
matthijs$ ls data/
arduino_2019-09-15_08:54:25.csv

matthijs$ cat data/arduino_2019-09-15_08\:54\:25.csv 
id,timestamp,date,time,modus,led1,led2,button1,sensor1
1,1568530336,2019-09-15,08:52:16,AUTOMATIC,ON,ON,DOWN,0.5
2,1568530346,2019-09-15,08:52:26,AUTOMATIC,ON,ON,UP,0.38
3,1568530356,2019-09-15,08:52:36,AUTOMATIC,ON,ON,DOWN,0.52
4,1568530371,2019-09-15,08:52:51,AUTOMATIC,ON,ON,UP,0.65
5,1568530381,2019-09-15,08:53:01,AUTOMATIC,ON,ON,DOWN,0.43
```

And in the configured eLABJournal experiment, a new section of type *EXCEL* has appeared. Data
is appended to the sheet `2019-09-15 08.52.02`.

<img width="350" src="../master/images/storage_elabjournal.png?raw=true"> 

Upon storage, new measurements are appended to the same sheet or CSV-file. When the Python application
is restarted, data will be appended to a new CSV-file and another sheet in the eLABJournal Excel section.






