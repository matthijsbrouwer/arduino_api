/*
   20190820 : API arduino (demonstrator for Johan Bucher)

   - arduino has two leds (LED1 & LED2) and a button (BUTTON_PIN)   
   - button on pin 11, leds on pin 12 and 13
   
   - in setup LED1 and LED2 are set to LED1_OFF and LED2_OFF
   
   - arduino can send status codes:
     - LED1_OFF, LED1_ON
     - LED2_OFF, LED2_ON
     - BUTTON_STATUS_UP, BUTTON_STATUS_DOWN
     - STATUS_ERROR
     
   - arduino can receive instruction codes:
     - LED1_OFF, LED1_ON, LED1_SWITCH
     - LED2_OFF, LED2_ON, LED2_SWITCH
     - STATUS_REQUEST
     - RESET
*/

//define pins
char BUTTON1_PIN=11;
char LED1_PIN=12;
char LED2_PIN=13;
char SENSOR1_PIN=0;

//define codes used to send status and receive instructions
#define STATUS_ERROR "STATUS_ERROR" //send status
#define LED1_OFF "LED1_OFF" //send status & receive instruction
#define LED1_ON "LED1_ON" //send status & receive instruction
#define LED1_SWITCH "LED1_SWITCH" //receive instruction
#define LED2_OFF "LED2_OFF" //send status & receive instruction
#define LED2_ON "LED2_ON" //send status & receive instruction
#define LED2_SWITCH "LED2_SWITCH" //receive instruction
#define BUTTON1_UP "BUTTON1_UP" //send status
#define BUTTON1_DOWN "BUTTON1_DOWN" //send status
#define STATUS_REQUEST "STATUS_REQUEST" //receive instruction
#define RESET "RESET" //receive instruction
#define TIME "TIME" //send status & receive instruction
#define MEASUREMENT "MEASUREMENT" //send status & receive instruction
#define SENSOR1 "SENSOR1" //send status
#define INIT "INIT" //send status
#define MODUS_MANUAL "MODUS_MANUAL" //send status & receive instruction
#define MODUS_AUTOMATIC "MODUS_AUTOMATIC" //send status & receive instruction
#define MODUS_SWITCH "MODUS_SWITCH" //receive instruction
#define PROGRAM "PROGRAM" //send status & receive instruction

//communication
char dataChar;
String dataString;
bool dataReady;

//status board
String button1Status;
String led1Status;
String led2Status;
String modus;
unsigned long dateTimestamp; // until 0:00 this day
unsigned long dayTimestamp; //ms from 0:00 this day
unsigned long timestamp; //normal 

//button1
int button1Value;
int button1LastValue;

/* ==== PROGRAM ====
  led1:       [-------------]      [-------------]                   [-------------]      [-------------]     
  led2:           [-----]              [-----]                           [-----]              [-----]
  measure:           *                    *                                 *                    *
              [-------period------][-------period------][---delay---][-------period------][-------period------][---delay---]                    
*/
            
bool program;
unsigned long programTime; 
unsigned long programLed1Time; 
unsigned long programLed2Time; 
unsigned long programMeasurementTime; 
unsigned int programRepeatsCounter; 
unsigned long programPeriod; 
unsigned long programRepeats;
unsigned long programDelay;
bool programLed1;
unsigned long programLed1Start;
unsigned long programLed1End;
bool programLed2;
unsigned long programLed2Start;
unsigned long programLed2End;
bool programMeasurement;
unsigned long programMeasurementStart;

//return status
void status_all() {
  Serial.println(led1Status);    
  Serial.println(led2Status);    
  Serial.println(button1Status); 
  Serial.println(modus); 
  status_program();
  status_time();
}

void status_set(String command) {
  Serial.println(command);
  status_time();  
}

void status_time() {
  timestamp = dateTimestamp + (dayTimestamp/1000);
  Serial.print(TIME);
  Serial.print(":");
  Serial.println(String(timestamp));  
}

void status_program() {
  Serial.print(String(PROGRAM) + ":"+String(programPeriod)+",");
  Serial.print(String(programLed1)+","+String(programLed1Start)+","+String(programLed1End)+",");
  Serial.print(String(programLed2)+","+String(programLed2Start)+","+String(programLed2End)+",");
  Serial.print(String(programMeasurement)+","+String(programMeasurementStart)+",");
  Serial.println(String(programRepeats)+","+String(programDelay));
  status_time(); 
}

void do_measurement() {
  float sensor1Status = analogRead(SENSOR1_PIN)/1024.0; 
  unsigned long measurementTimestamp = dateTimestamp + (dayTimestamp/1000); 
  Serial.println(String(SENSOR1) + ":" + String(measurementTimestamp) + "," + String(sensor1Status));
  Serial.print(String(MEASUREMENT) + ":" + String(TIME) + "_" +String(measurementTimestamp)+","+String(modus)+",");
  Serial.println(String(led1Status)+","+String(led2Status)+","+String(button1Status)+","+String(SENSOR1)+"_"+String(sensor1Status));  
  status_time();  
}

void setup() { 
  //start communication
  Serial.begin(9600);
  //reset time
  timestamp = 0;
  dayTimestamp = 0;
  dateTimestamp = 0;
  //define pins
  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);  
  //start with empty datastring
  dataString = "";  
  dataReady = false;
  //set modus
  modus=MODUS_MANUAL;
  //setup functions 
  setup_interrupts();
  setup_reset(); 
  setup_program(); 
  Serial.println("INIT");
}
 
void loop() {
  //wait until event is detected
  while (!Serial.available()) {  
    //check button
    update_button(); 
    //do program
    if(modus==MODUS_AUTOMATIC) {
        update_program();
    }
  }
  //read data
  while (Serial.available()) {     
    while (Serial.available()) {
      dataChar = Serial.read();
      if(dataChar=='\n') {
        dataReady=true;
        break;    
      } else {
        dataString += dataChar;
      }  
    }  
    //process instructions
    if(dataReady) {
      if (dataString == LED1_ON || dataString == LED1_OFF || dataString == LED1_SWITCH) {
        if(modus==MODUS_MANUAL) {
          led1Status=(dataString == LED1_SWITCH)?(led1Status==LED1_OFF)?LED1_ON:LED1_OFF:dataString;
          digitalWrite (LED1_PIN, (led1Status == LED1_ON)?HIGH:LOW);
          status_set(led1Status);
        } else {
          status_set(STATUS_ERROR);  
        }
      } else if (dataString == LED2_ON || dataString == LED2_OFF || dataString == LED2_SWITCH) {
        if(modus==MODUS_MANUAL) {
          led2Status=(dataString == LED2_SWITCH)?(led2Status==LED2_OFF)?LED2_ON:LED2_OFF:dataString;
          digitalWrite (LED2_PIN, (led2Status == LED2_ON)?HIGH:LOW);
          status_set(led2Status);
        } else {
          status_set(STATUS_ERROR);  
        }  
      } else if (dataString == MEASUREMENT) {
        if(modus==MODUS_MANUAL) {
          do_measurement();           
        } else {
          status_set(STATUS_ERROR);
        }
      } else if (dataString == MODUS_MANUAL || dataString == MODUS_AUTOMATIC || dataString == MODUS_SWITCH) {
        modus=(dataString == MODUS_SWITCH)?(modus==MODUS_MANUAL)?MODUS_AUTOMATIC:MODUS_MANUAL:dataString;              
        status_set(modus);  
        setup_reset();
        status_all();  
        if(modus==MODUS_AUTOMATIC) {
          start_program();
        }
      } else if (dataString == STATUS_REQUEST) {
        status_all();         
      } else if (dataString.startsWith(TIME)) {
        if(dataString != TIME) {
          timestamp=dataString.substring(strlen(TIME)+1,dataString.length()).toInt(); 
          dayTimestamp=1000*(timestamp%34560);
          dateTimestamp=34560*(timestamp/34560);
        }  
        status_time();   
      } else if (dataString.startsWith(PROGRAM)) {
        if(dataString != PROGRAM) {
          program = false;
          dataString = dataString.substring(strlen(PROGRAM)+1,dataString.length());
          programPeriod = get_program_value_from_string(dataString,0); 
          programRepeats = get_program_value_from_string(dataString,9);
          programDelay = get_program_value_from_string(dataString,10);
          programLed1 = get_program_value_from_string(dataString,1);
          programLed1Start = get_program_value_from_string(dataString,2);
          programLed1End = get_program_value_from_string(dataString,3);
          programLed2 = get_program_value_from_string(dataString,4);
          programLed2Start = get_program_value_from_string(dataString,5);
          programLed2End = get_program_value_from_string(dataString,6);
          programMeasurement = get_program_value_from_string(dataString,7);
          programMeasurementStart = get_program_value_from_string(dataString,8); 
          if(modus==MODUS_AUTOMATIC) {
            setup_reset();
            program = true;
            start_program();
          } else {
            program = true;
          }
                     
        }
        status_program();
      } else if (dataString == RESET) {
        setup_reset();  
        status_all();      
      } else if(dataString.length()>0) {
        status_set(STATUS_ERROR);       
        //Serial.println("unknown: "+dataString);  
      }
      dataString = "";
      dataReady = false;
    }  
  }  
}


//timestamp
ISR(TIMER1_COMPA_vect) {
    dayTimestamp+=100; //increment 100ms at each pulse
    if(dayTimestamp>86400000) { //1000*60*60*24 = 86400000 ms in a day
      dayTimestamp=0;
      dateTimestamp+=34560; //60*60*24 = 34560 s in a day
    }
}

void setup_interrupts() 
{
  //disable interrupts
  cli();
  //set timer1 interrupt at 10Hz
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = 24999; // (16*10^6) / (64*10) - 1 (<65536)
  TCCR1B |= (1 << WGM12); //CTC mode
  TCCR1B |= (0 << CS12) | (1 << CS11) | (1 << CS10); //64 prescaler
  TIMSK1 |= (1 << OCIE1A); //timer compare
  //enable interrupts
  sei();
}

void setup_reset()
{
  //start with leds off
  digitalWrite(LED1_PIN, LOW);  
  led1Status=LED1_OFF;  
  digitalWrite(LED2_PIN, LOW);  
  led2Status=LED2_OFF;
  //get button1 status
  button1Value=digitalRead(BUTTON1_PIN);
  button1LastValue=button1Value; 
  button1Status=(button1Value==HIGH?BUTTON1_DOWN:BUTTON1_UP);  
}

void update_button()
{
  if((button1Value=digitalRead(BUTTON1_PIN))!=button1LastValue) {
     button1LastValue=button1Value; 
     button1Status=(button1Value==HIGH?BUTTON1_DOWN:BUTTON1_UP);
     Serial.println(button1Status); 
     status_time(); 
  } 
}

void start_program()
{
  //reset
  setup_reset();
  //set variables
  programTime = dayTimestamp; 
  programRepeatsCounter = 0;
  next_cycle_program();
}

void next_cycle_program()
{
  //reset
  setup_reset();
  //next cycle
  programLed1Time = programLed1?(programTime+programLed1Start):0; //switch led1
  programLed2Time = programLed2?(programTime+programLed2Start):0; //switch led2
  programMeasurementTime = programMeasurement?(programTime+programMeasurementStart):0; //do measurement
  programTime += programPeriod; //cycle has to be repeated after this time
  programRepeatsCounter++;    
}

void update_program()
{
  if(program) {
    //cycle has ended, start next or start delay or restart program
    if(programTime<dayTimestamp) {
      if(programRepeatsCounter<programRepeats) {
        next_cycle_program();
      } else if(programRepeatsCounter==programRepeats) {
        programTime += programDelay; //delay
        programLed1Time+= 2*programDelay;
        programLed2Time+= 2*programDelay;
        programMeasurementTime+= 2*programDelay;
        programRepeatsCounter++;            
      } else {
        start_program(); //finished, restart
      }
    } else {
      //check led1
      if(programLed1 && programLed1Time<dayTimestamp) {  
        if(led1Status==LED1_OFF) {
          led1Status=LED1_ON;  
          programLed1Time+=programLed1End;
          programLed1Time-=programLed1Start;
        } else {
          led1Status=LED1_OFF; 
          programLed1Time+=2*programPeriod;
        }
        digitalWrite (LED1_PIN, (led1Status == LED1_ON)?HIGH:LOW);
        status_set(led1Status);
      }
      //check led2
      if(programLed2 && programLed2Time<dayTimestamp) {  
        if(led2Status==LED2_OFF) {
          led2Status=LED2_ON;  
          programLed2Time+=programLed2End;
          programLed2Time-=programLed2Start;
        } else {
          led2Status=LED2_OFF; 
          programLed2Time+=2*programPeriod;
        }
        digitalWrite (LED2_PIN, (led2Status == LED2_ON)?HIGH:LOW);
        status_set(led2Status);
      }
      //check measurement
      if(programMeasurement && programMeasurementTime<dayTimestamp) { 
        do_measurement(); 
        programMeasurementTime+=2*programPeriod;
      }
    }
  }
}

void setup_program() 
{
  //definition
  program = true;
  programPeriod = 10000; 
  programRepeats = 3;
  programDelay = 5000;
  programLed1 = true;
  programLed1Start = 1000;
  programLed1End = 5000;
  programLed2 = true;
  programLed2Start = 2000;
  programLed2End = 4000;
  programMeasurement = true;
  programMeasurementStart = 3000;  
}

int get_program_value_from_string(String data, int k) 
{
  char separator = ',';
  int found = 0;
  int strIndex[] = {0,-1};
  int maxIndex = data.length() - 1;
  for(int i=0; i<=maxIndex && found <= k; i++) {
    if(data.charAt(i)==separator||i==maxIndex) {
      found++;
      strIndex[0] = strIndex[1]+1;
      strIndex[1] = (i==maxIndex)?i+1:i;
    }
  }
  return found>k?data.substring(strIndex[0],strIndex[1]).toInt():0;
}
