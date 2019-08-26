# Control Arduino using API

Demonstrate use of API to get and set status of Arduino board

<img align="right" src="../master/images/arduino.jpeg?raw=true">

## Setup Arduino

Connect

- LED1 to pin 12
- LED2 to pin 13
- BUTTON to pin 11

Upload the [api software](arduino/api/api.ino) to the Arduino Board.

## Start server

Start the [server](server/server.py)

```
python server/server.py
```

The server tries to detect automatically the COM-port used by the Arduino board and starts a connection.

Then two processes are started:

- A process to monitor data sent from the board. This data is used to update the status of LED1, LED2 and BUTTON in variables also available to the other process.
- A process providing a Flask based API server to access these status variables and also send instructions to the board. 

The server also hosts an html/javascript based demonstrator environment to test and 
illustrate use of the API.

## Test API

See [demonstrator](http://localhost:5000/)

![Image](../master/images/browser.png?raw=true)

The buttons LED1 and LED2 can be used to control the leds. The browser displays the status of the leds, and also indicates if the button on the board is pushed down.

## Methods API

API methods available from this server

- GET status 
 
        curl 'http://localhost:5000/status' -X GET
        
- PUT reset

        curl 'http://localhost:5000/reset' -X PUT        
        
- GET or PUT status LED1   

        curl 'http://localhost:5000/led1' -X GET
        curl 'http://localhost:5000/led1' -X PUT -H 'Content-Type: application/json'  --data '"ON"'
        curl 'http://localhost:5000/led1' -X PUT -H 'Content-Type: application/json'  --data '"OFF"'
        curl 'http://localhost:5000/led1' -X PUT -H 'Content-Type: application/json'  --data '"SWITCH"'
        
- GET or PUT status LED2   

        curl 'http://localhost:5000/led2' -X GET
        curl 'http://localhost:5000/led2' -X PUT -H 'Content-Type: application/json'  --data '"ON"'
        curl 'http://localhost:5000/led2' -X PUT -H 'Content-Type: application/json'  --data '"OFF"'
        curl 'http://localhost:5000/led2' -X PUT -H 'Content-Type: application/json'  --data '"SWITCH"'            

- GET status BUTTON 

        curl 'http://localhost:5000/button' -X GET
        
These methods can also be tested from the [demonstrator](http://localhost:5000/).        
        
        