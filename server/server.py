# ------------------------------------------------------
# 20190820 : API arduino (demonstrator for Johan Bucher)
# ------------------------------------------------------
from flask import Flask, jsonify, request, render_template
from multiprocessing import Process, Value
import serial,serial.tools.list_ports,time,logging 

# ----- SETTINGS -----

#settings logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logger = logging.getLogger("arduino")
logger.setLevel(logging.INFO)
            
#communication settings arduino (None to automatically detect)
arduino_port = None

#api settings
api_port=5000
api_host="::"
api_debug=False

# ----- ARDUINO -----

def process_arduino_messages():
    """
      Communication arduino
    """
    try:
        #ask for status
        ArduinoUnoSerial.write(str.encode('\x09'))
        #start processing messages    
        while True:
            msg = ArduinoUnoSerial.read(ArduinoUnoSerial.inWaiting())    
            if msg:
                msg = msg.decode("utf-8").strip()        
                lines = msg.split("\n")
                for line in lines:
                    line = line.strip()
                    if line=="1":
                        logger.info("received: disabled led1")
                        led1_status.value = 0            
                    elif line=="2":
                        logger.info("received: enabled led1")
                        led1_status.value = 1         
                    elif line=="4":
                        logger.info("received: disabled led2")
                        led2_status.value = 0   
                    elif line=="5":
                        logger.info("received: enabled led2")
                        led2_status.value = 1   
                    elif line=="7":
                        logger.info("received: enabled button")
                        button_status.value = 1 
                    elif line=="8":
                        logger.info("received: disabled button")
                        button_status.value = 0   
                    elif line=="0":
                        logger.info("received: error")
                    elif line:    
                        logger.error("couldn't parse '"+line+"'") 
            time.sleep(0.1)
    except Exception as e:  
        logger.error("error: "+ str(e))              
        
# ----- REST API -----        
        
def process_api_messages():
    """
      Create API to control arduino
    """       
    
    #initialize Flask application
    app = Flask(__name__, static_url_path="/static")   
    
    #html template for controlling arduino
    @app.route("/")
    def index():
        return render_template("server.html")    
    
    #get stored status
    @app.route("/status", methods=["GET"])
    def status():
        status = {
            "led1": "ON" if led1_status.value==1 else "OFF",
            "led2": "ON" if led2_status.value==1 else "OFF",
            "button": "ON" if button_status.value==1 else "OFF"
        }
        return jsonify(status), 200                                     
        
    #reset
    @app.route("/reset", methods=["PUT"])
    def reset():
        ArduinoUnoSerial.write(str.encode('\x0a')) 
        return jsonify("RESET"), 200                                     
        
    #get or set led1
    @app.route("/led1", methods=["GET","PUT"])
    def led1():
        if request.method=="GET":
            return jsonify("ON" if led1_status.value==1 else "OFF")
        elif request.method=="PUT":
            if request.json=="OFF" :
                logger.info("sent: disable led1")
                ArduinoUnoSerial.write(str.encode('\x01')) 
                return jsonify("SET LED1 OFF"), 200
            elif request.json=="ON" :
                logger.info("sent: enable led1")
                ArduinoUnoSerial.write(str.encode('\x02')) 
                return jsonify("SET LED1 ON"), 200
            elif request.json=="SWITCH" :
                logger.info("sent: switch led1")
                ArduinoUnoSerial.write(str.encode('\x03')) 
                return jsonify("SWITCH LED1"), 200
            else :
                logger.info("sent: ---")
                return jsonify("UNKNOWN COMMAND LED1"), 500   
        
    #get or set led2
    @app.route("/led2", methods=["GET","PUT"])
    def led2():
        if request.method=="GET":
            return jsonify("ON" if led2_status.value==1 else "OFF")
        elif request.method=="PUT":
            if request.json=="OFF" :
                logger.info("sent: disable led2")
                ArduinoUnoSerial.write(str.encode('\x04')) 
                return jsonify("SET LED2 OFF"), 200
            elif request.json=="ON" :
                logger.info("sent: enable led2")
                ArduinoUnoSerial.write(str.encode('\x05')) 
                return jsonify("SET LED2 ON"), 200
            elif request.json=="SWITCH" :
                logger.info("sent: switch led2")
                ArduinoUnoSerial.write(str.encode('\x06')) 
                return jsonify("SWITCH LED2"), 200
            else :
                logger.info("sent: ---")
                return jsonify("UNKNOWN COMMAND LED2"), 500 
            
    #get button
    @app.route("/button", methods=["GET"])
    def button():
        return jsonify("ON" if button_status.value==1 else "OFF"), 200                
    
    @app.errorhandler(404)
    def not_found(error):
        return(jsonify({"error": "Not found"}), 404)                       
        
    #start rest api
    app.run(host=api_host, port=api_port, debug=api_debug, 
            use_reloader=False)                                    
                  
# ----- MAIN FUNCTION -----
                       
if __name__ == "__main__":  

    while True:
    
        #automatically detect port Arduino
        if arduino_port is None:
            ports = list(serial.tools.list_ports.comports())
            arduino_ports = []
            for p in ports:
                if (p.manufacturer is not None) and ("Arduino" in p.manufacturer):
                    arduino_ports.append(p)
            if len(arduino_ports)==0:
                logger.error("no arduino found")
                ArduinoUnoSerial = None
                time.sleep(1)
            else:
                if len(arduino_ports)>1:
                    print("Multiple Arduino boards found, first selected"); 
                print("Arduino "+str(arduino_ports[0].serial_number)+" on "+str(arduino_ports[0].device))   
                ArduinoUnoSerial = serial.Serial(arduino_ports[0].device,9600) 
        else:            
            #define communication with predefined arduino port
            ArduinoUnoSerial = serial.Serial(arduino_port,9600)    
    
        if ArduinoUnoSerial:

            try:
                #thread-safe variables
                button_status = Value("i", 0)
                led1_status = Value("i", 0)
                led2_status = Value("i", 0)
                
                #process communication arduino            
                process_arduino = Process(target=process_arduino_messages, args=[])
                #process rest api
                process_api = Process(target=process_api_messages, args=[])
                
                #start everything
                process_arduino.start()
                process_api.start()
                
                #wait until arduino ends  
                process_arduino.join()
                process_api.terminate()
            except Exception as e:  
                logger.error("error: "+ str(e))      
      