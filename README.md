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

## Demonstrator

Go to the [demonstrator](http://localhost:5000/)

![Image](../master/images/browser.png?raw=true)

Use buttons LED1 and LED2 to control the leds. The browser displays the status of the
leds, and also indicates if the button on the board is pushed down.

## API

Functionality

- Get status 

        ``` 
        curl http://localhost:5000/status 
        ```
        
- Reset

        ````
        curl http://localhost:5000/reset -X PUT
        ````        
        
- Get or set status LED1   

        ```
        curl http://localhost:5000/led1
        curl http://localhost:5000/led1 -X PUT -H 'Content-Type: application/json'  --data '"ON"'
        curl http://localhost:5000/led1 -X PUT -H 'Content-Type: application/json'  --data '"OFF"'
        curl http://localhost:5000/led1 -X PUT -H 'Content-Type: application/json'  --data '"SWITCH"'
        ``` 
        
- Get or set status LED2   

        ```
        curl http://localhost:5000/led2
        curl http://localhost:5000/led2 -X PUT -H 'Content-Type: application/json'  --data '"ON"'
        curl http://localhost:5000/led2 -X PUT -H 'Content-Type: application/json'  --data '"OFF"'
        curl http://localhost:5000/led2 -X PUT -H 'Content-Type: application/json'  --data '"SWITCH"'
        ```            

- Get status button   

        ```
        curl http://localhost:5000/button
        ```
        
        