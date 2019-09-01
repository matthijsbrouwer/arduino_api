# ------------------------------------------------------
# 20190820 : API arduino (demonstrator for Johan Bucher)
# ------------------------------------------------------
from flask import Flask, Blueprint, jsonify, request, render_template
from flask_restplus import Api,Resource,abort,fields
from multiprocessing import Process, Manager, Value
from ctypes import c_char_p
from datetime import datetime
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
api_debug=True

# ----- ARDUINO -----

def process_arduino_messages():
    """
      Communication arduino
    """
    try:
        #start processing messages        
        input = b''
        while True:
            while ArduinoUnoSerial.inWaiting():
                input = input + ArduinoUnoSerial.read(ArduinoUnoSerial.inWaiting()) 
            if len(input)>0:    
                msg = input.decode()
                lines = msg.replace("\r\n","\n").split("\n")      
                input = lines[-1].encode()
                lines = lines[:-1]
                for line in lines:
                    if len(line)>0:
                        if line=="LED1_OFF":
                            logger.info("received: disabled led1")
                            led1_status.value = "OFF"            
                        elif line=="LED1_ON":
                            logger.info("received: enabled led1")
                            led1_status.value = "ON"         
                        elif line=="LED2_OFF":
                            logger.info("received: disabled led2")
                            led2_status.value = "OFF"   
                        elif line=="LED2_ON":
                            logger.info("received: enabled led2")
                            led2_status.value = "ON"  
                        elif line=="BUTTON1_UP":
                            logger.info("received: enabled button")
                            button1_status.value = "ON" 
                        elif line=="BUTTON1_DOWN":
                            logger.info("received: disabled button")
                            button1_status.value = "OFF"   
                        elif line=="MODUS_MANUAL":
                            logger.info("received: modus manual")
                            arduino_modus.value = "MANUAL"   
                        elif line=="MODUS_AUTOMATIC":
                            logger.info("received: modus automatic")
                            arduino_modus.value = "AUTOMATIC"   
                        elif line=="INIT":
                            logger.info("received: init")
                            arduino_set_time()
                            arduino_instruction("STATUS_REQUEST")
                        elif line=="STATUS_ERROR":
                            logger.info("received: error")
                        elif line.startswith("TIME:"):
                            new_arduino_time = int(line[5:])
                            arduino_timestamp_drift.value = int(round(time.time())) - new_arduino_time
                            arduino_timestamp.value = int(line[5:])
                            logger.info("received: timestamp "+str(arduino_timestamp.value)+", drift "+str(arduino_timestamp_drift.value))
                        elif line.startswith("SENSOR1:"):
                            data = line[8:].split(",")
                            sensor1_measurement.value = float(data[1])
                            sensor1_timestamp.value = int(data[0])
                            logger.info("received: sensor1 "+str(sensor1_measurement.value)+" at "+str(sensor1_timestamp.value))
                        elif line.startswith("MEASUREMENT:"):
                            measurement_total.value+=1
                            data = line[12:].split(",")
                            measurement = {}
                            measurement_timestamp = int(data[0][5:])
                            measurement["id"] = measurement_total.value
                            measurement["timestamp"] = measurement_timestamp
                            measurement["date"] = datetime.fromtimestamp(measurement_timestamp).date().isoformat()
                            measurement["time"] = datetime.fromtimestamp(measurement_timestamp).time().isoformat()
                            measurement["modus"] = data[1][6:]
                            measurement["led1"] = data[2][5:]
                            measurement["led2"] = data[3][5:]
                            measurement["button1"] = data[4][8:]
                            measurement["sensor1"] = float(data[5][8:])
                            measurement_list.append(measurement)
                            logger.info("received: measurement")
                        elif line.startswith("PROGRAM:"):
                            data = line[8:].split(",")
                            program["last"] = int(round(time.time()))
                            program["period"] = int(data[0])
                            program["led1"] = (int(data[1])>0)
                            program["led1_start"] = int(data[2])
                            program["led1_end"] = int(data[3])
                            program["led2"] = (int(data[4])>0)
                            program["led2_start"] = int(data[5])
                            program["led2_end"] = int(data[6]) 
                            program["measurement"] = (int(data[7])>0)
                            program["measurement_start"] = int(data[8]) 
                            program["repeats"] = int(data[9]) 
                            program["delay"] = int(data[10]) 
                            logger.info("received: program")  
                        elif line:    
                            logger.error("couldn't parse '"+line+"'") 
            time.sleep(0.1)                
    except Exception as e:  
        logger.error("error: "+ str(e))    
        
def arduino_instruction(command):
    ArduinoUnoSerial.write(str.encode(str(command)+"\n"))  
    
def arduino_set_time():
    arduino_instruction("TIME:"+str(int(round(time.time()))))                                        
        
# ----- WEBSERVER -----        
        
def process_api_messages():
    """
      Create API to control arduino
    """       
    
    #initialize Flask application
    app = Flask(__name__, static_url_path="/static")  
    blueprint = Blueprint("api", __name__, url_prefix="/api")
    api = Api(blueprint)
    
    api_led = api.namespace("led", description="Led operations")
    api_button = api.namespace("button", description="Button operations")
    api_sensor = api.namespace("sensor", description="Sensor operations")
    api_measurement = api.namespace("measurement", description="Measurement operations")
    api_program = api.namespace("program", description="Program operations")
    
    app.register_blueprint(blueprint) 
    app.config.SWAGGER_UI_DOC_EXPANSION = "list"
    
    parser = api.parser()
       
    #--- HTML ---
    @app.route("/")
    def index():
        return render_template("server.html")    
    
    #--- REST API ---
    
    status_get = parser.copy()
    status_get.add_argument("measurement_number", type=int, required=False, location="args", help="Maximum number of measurements")    
    status_get.add_argument("measurement_last", type=int, required=False, location="args", help="The id of the last known measurement")    
    
    @api.route("/status")
    class Status(Resource):
        @api.expect(status_get)        
        def get(self):
            """
            Get the status of the board
            """
            measurement_number = 0
            measurement_last = 0
            measurement_number = int(0 if request.args.get("measurement_number") is None else request.args.get("measurement_number"))
            measurement_last = int(0 if request.args.get("measurement_last") is None else request.args.get("measurement_last"))
            data = {
                "led1": led1_status.value,
                "led2": led2_status.value,
                "button": button1_status.value,
                "time" : {
                    "date": datetime.fromtimestamp(arduino_timestamp.value).date().isoformat(),
                    "time": datetime.fromtimestamp(arduino_timestamp.value).time().isoformat(),
                    "drift": arduino_timestamp_drift.value                
                },    
                "modus": arduino_modus.value,
                "measurements": {
                  "total": measurement_total.value,
                  "number": len(measurement_list),
                  "min_id": 0,
                  "list" : []
                },
                "program": program.copy()
            }
            if len(measurement_list)>0:
                data["measurements"]["last"] = measurement_list[-1]
                data["measurements"]["min_id"] = measurement_list[0]["id"]
            if measurement_number>0 and len(measurement_list)>0:
                    sublist = measurement_list[-1*min(len(measurement_list),measurement_number):]
                    data["measurements"]["list"] = sublist
                           
            return data 
        
    @api.route("/reset")
    class Reset(Resource):
        def put(self):
            """
            Reset the board
            """
            ArduinoUnoSerial.write(str.encode("RESET\n")) 
            return "RESET"  
            
    modus_put = parser.copy()
    modus_put.add_argument("modus", required=True, location="json", help="Set the modus", choices=['"MANUAL"','"AUTOMATIC"','"SWITCH"'])
    
    @api.route("/modus")
    class Modus(Resource):
        def get(self):
            """
            Get the modus
            """
            return arduino_modus.value
            
        @api.expect(modus_put)
        def put(self):    
            """
            Set the modus
            """
            if request.json=="MANUAL" or request.json=="AUTOMATIC" or request.json=="SWITCH":
                logger.info("sent: put modus "+str(request.json).lower())
                arduino_instruction("MODUS_"+str(request.json))
                return "PUT MODUS "+str(request.json)
            else :
                logger.error("unknown command put to modus")
                return "UNKNOWN COMMAND MODUS"                   
    
    @api.route("/time")
    class Time(Resource):
        def get(self):
            """
            Get latest time from board
            """
            data = {
                "date": datetime.fromtimestamp(arduino_timestamp.value).date().isoformat(),
                "time": datetime.fromtimestamp(arduino_timestamp.value).time().isoformat(),
                "drift": arduino_timestamp_drift.value
            }
            return data
            
        def put(self):
            """
            Request for time from board
            """
            arduino_instruction("TIME")  
            return "POST TIME"
            
        def post(self):    
            """
            Set the board time
            """
            arduino_instruction("TIME:"+str(int(round(time.time()))))  
            return "POST TIME"                
    
    led_put = parser.copy()
    led_put.add_argument("status", required=True, location="json", help="Set the status of the LED", choices=['"ON"','"OFF"','"SWITCH"'])
    
    @api_led.route("/1")
    class Led1(Resource):
        def get(self):
            """
            Get the status of led 1
            """
            return led1_status.value            
                
        @api.expect(led_put)
        def put(self):
            """
            Set the status of led 1
            """ 
            if request.json=="ON" or request.json=="OFF" or request.json=="SWITCH":
                logger.info("sent: put led1 "+str(request.json).lower())
                arduino_instruction("LED1_"+str(request.json))
                return "PUT LED1 "+str(request.json)
            else :
                logger.error("unknown command put to led1")
                return "UNKNOWN COMMAND LED1"
        
        
    @api_led.route("/2")
    class Led2(Resource):
        def get(self):
            """
            Get the status of led 2
            """
            return led2_status.value                            
        @api.expect(led_put)
        def put(self):
            """
            Set the status of led 2
            """ 
            if request.json=="ON" or request.json=="OFF" or request.json=="SWITCH":
                logger.info("sent: put led2 "+str(request.json).lower())
                arduino_instruction("LED2_"+str(request.json))
                return "PUT LED2 "+str(request.json)
            else :
                logger.error("unknown command put to led2")
                return "UNKNOWN COMMAND LED2"
                
    @api_button.route("/1")
    class Button1(Resource):
        def get(self):
            """
            Get the status of button 1
            """
            return button1_status.value
            
    @api_sensor.route("/1")
    class Sensor1(Resource):
        def get(self):
            """
            Get latest measurement from sensor 1
            """
            data = {}
            if sensor1_timestamp.value:
                data["data"] = datetime.fromtimestamp(sensor1_timestamp.value).date().isoformat()
                data["time"] = datetime.fromtimestamp(sensor1_timestamp.value).time().isoformat()
                data["timestamp"] = sensor1_timestamp.value
                data["measurement"] = sensor1_measurement.value
            return data        
            
    @api_measurement.route("/")
    class Measurement(Resource):
        def get(self):
            """
            Get latest measurement
            """
            if len(measurement_list)>0:
                return measurement_list[-1]
            else:
                return None                                    
        def put(self):
            """
            Do new measurement
            """
            arduino_instruction("MEASUREMENT")
            return "DO MEASUREMENT"                                                                              
    
    @api_measurement.route("/clear")
    class MeasurementClear(Resource):
        def put(self):
            """
            Clear measurement history
            """
            measurement_list[:] = []
            return "CLEAR MEASUREMENTS"
            
    @api_measurement.route("/list")
    class MeasurementList(Resource):
        def get(self):
            """
            Get all measurements
            """
            list = []
            while len(measurement_list)>0:
                list.append(measurement_list.pop(0))
            return list     
            
    @api_measurement.route("/save")
    class MeasurementSave(Resource):
        def put(self):
            """
            Save measurements to file
            """
            list = []
            while len(measurement_list)>0:
                list.append(measurement_list.pop(0))
            return list
            
    program_put = parser.copy()
    program_put.add_argument("period", type=int, required=True, location="form", help="Length cycle")    
    program_put.add_argument("led1", type=bool, required=True, location="form", help="Let led1 start and stop within cycle")    
    program_put.add_argument("led1_start", type=int, required=True, location="form", help="Timing within cycle to start led1")    
    program_put.add_argument("led1_end", type=int, required=True, location="form", help="Timing within cycle to stop led1")    
    program_put.add_argument("led2", type=bool, required=True, location="form", help="Let led2 start and stop within cycle")    
    program_put.add_argument("led2_start", type=int, required=True, location="form", help="Timing within cycle to start led2")    
    program_put.add_argument("led2_end", type=int, required=True, location="form", help="Timing within cycle to stop led2")    
    program_put.add_argument("measurement", type=bool, required=True, location="form", help="Do measurement within cycle")    
    program_put.add_argument("measurement_start", type=int, required=True, location="form", help="Timing measurement within cycle")    
    program_put.add_argument("repeats", type=int, required=True, location="form", help="Number of cycles")    
    program_put.add_argument("delay", type=int, required=True, location="form", help="Delay after all cycles")    
    
    @api_program.route("/")
    class Program(Resource):
        def get(self):
            """
            Get the automatic program settings
            """
            return program.copy()
        @api_program.expect(program_put)            
        def put(self):
            """
            Change the automatic program
            """
            command = "PROGRAM:"
            command+=str(request.form["period"])+","
            command+=str(int(request.form["led1"]=="true"))+","
            command+=str(request.form["led1_start"])+","
            command+=str(request.form["led1_end"])+","
            command+=str(int(request.form["led2"]=="true"))+","
            command+=str(request.form["led2_start"])+","
            command+=str(request.form["led2_end"])+","
            command+=str(int(request.form["measurement"]=="true"))+","
            command+=str(request.form["measurement_start"])+","
            command+=str(request.form["repeats"])+","
            command+=str(request.form["delay"])
            arduino_instruction(command)
            return "PUT "+command           
                                                                                                             
    #start webserver
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
                manager = Manager()
                button1_status = manager.Value(c_char_p, "OFF")
                led1_status = manager.Value(c_char_p, "OFF")
                led2_status = manager.Value(c_char_p, "OFF")
                sensor1_measurement = Value("d", 0.0)
                sensor1_timestamp = Value("i", 0)
                arduino_timestamp = Value("i",0)
                arduino_timestamp_drift = Value("i",0)
                arduino_modus = manager.Value(c_char_p, "MANUAL")
                program = manager.dict({
                    "last": 0,
                    "period": 0,
                    "led1": False,
                    "led1_start": 0,
                    "led1_end": 0,
                    "led2": False,
                    "led2_start": 0,
                    "led2_end": 0,
                    "measurement": False,
                    "measurement_start": 0,
                    "repeats": 1,
                    "delay": 0
                })
                measurement_list = manager.list()
                measurement_total = Value("i",0)
                
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
      