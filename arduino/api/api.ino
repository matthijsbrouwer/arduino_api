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
int BUTTON_PIN=11;
int LED1_PIN=12;
int LED2_PIN=13;

//define codes used to send status and receive instructions
int STATUS_ERROR=0; //send status
int LED1_OFF=1; //send status & receive instruction
int LED1_ON=2; //send status & receive instruction
int LED1_SWITCH=3; //receive instruction
int LED2_OFF=4; //send status & receive instruction
int LED2_ON=5; //send status & receive instruction
int LED2_SWITCH=6; //send status & receive instruction
int BUTTON_STATUS_UP=7; //send status
int BUTTON_STATUS_DOWN=8; //send status
int STATUS_REQUEST=9; //receive instruction
int RESET=10; //receive instruction

//communication
int data;

//status board
int buttonValue;
int buttonLastValue;
int buttonStatus;
int led1Status;
int led2Status;
bool buttonChanged;

void setup() { 
  //start communication
  Serial.begin(9600);
  //define pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  //start with leds off
  digitalWrite (LED1_PIN, LOW);  
  led1Status = LED1_OFF;  
  digitalWrite (LED2_PIN, LOW);  
  led2Status = LED2_OFF;
  //get button status
  buttonValue=digitalRead(BUTTON_PIN);
  buttonLastValue=buttonValue; 
  buttonChanged=false;
  buttonStatus=(buttonValue==HIGH?BUTTON_STATUS_DOWN:BUTTON_STATUS_UP);  
  //communicate status
  Serial.println(led1Status);
  Serial.println(led2Status);
  Serial.println(buttonStatus);
}
 
void loop() {
  //wait until event is detected
  while (!Serial.available() && !buttonChanged) {  
    if(digitalRead(BUTTON_PIN)!=buttonLastValue) {
       buttonChanged=true;
    }  
  }
  //update button status
  if(buttonChanged){
    buttonValue=digitalRead(BUTTON_PIN);
    buttonLastValue=buttonValue; 
    buttonChanged=false;
    buttonStatus=(buttonValue==HIGH?BUTTON_STATUS_DOWN:BUTTON_STATUS_UP);
    Serial.println(buttonStatus);        
  }
  //read data
  while (Serial.available()) { 
    data = Serial.read();    
    //process instructions
    if (int(data) == LED1_ON) {
      //enable led1
      digitalWrite (LED1_PIN, HIGH);
      Serial.println(LED1_ON);
      led1Status=LED1_ON;
    } else if (int(data) == LED1_OFF) {
      //disable led1
      digitalWrite (LED1_PIN, LOW);
      Serial.println(LED1_OFF);
      led1Status=LED1_OFF;
    } else if (int(data) == LED1_SWITCH) {
      led1Status=(led1Status==LED1_OFF)?LED1_ON:LED1_OFF;
      digitalWrite (LED1_PIN, (led1Status==LED1_OFF)?LOW:HIGH);
      Serial.println(led1Status);      
    } else if (int(data) == LED2_ON) {
      //enable led2
      digitalWrite (LED2_PIN, HIGH);
      Serial.println(LED2_ON);
      led2Status=LED2_ON;
    } else if (int(data) == LED2_OFF) {
      //disable led2
      digitalWrite (LED2_PIN, LOW);
      Serial.println(LED2_OFF);
      led2Status=LED2_OFF;
    } else if (int(data) == LED2_SWITCH) {
      led2Status=(led2Status==LED2_OFF)?LED2_ON:LED2_OFF;
      digitalWrite (LED2_PIN, (led2Status==LED2_OFF)?LOW:HIGH);
      Serial.println(led2Status);      
    } else if (int(data) == STATUS_REQUEST) {
      //return status leds and button
      Serial.println(led1Status);    
      Serial.println(led2Status);    
      Serial.println(buttonStatus);          
    } else if (int(data) == RESET) {
      //disable leds
      digitalWrite (LED1_PIN, LOW);  
      led1Status = LED1_OFF;  
      digitalWrite (LED2_PIN, LOW);  
      led2Status = LED2_OFF;
      //get button status
      buttonValue=digitalRead(BUTTON_PIN);
      buttonLastValue=buttonValue; 
      buttonChanged=false;
      buttonStatus=(buttonValue==HIGH?BUTTON_STATUS_DOWN:BUTTON_STATUS_UP); 
      //return status leds and button
      Serial.println(led1Status);    
      Serial.println(led2Status);    
      Serial.println(buttonStatus);          
    } else {
      //unrecognized code
      Serial.print(STATUS_ERROR);       
      Serial.print(data);  
    }
  }  
}
