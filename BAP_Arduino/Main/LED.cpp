#include "LED.h" 

void LED::on(){
  state = HIGH;
  digitalWrite(pin,state);
}

void LED::off(){
  state = LOW;
  digitalWrite(pin,state);
}

LED::LED(){}

LED::LED(byte pin){
  this->pin = pin;
}

void LED::init(){
  pinMode(pin, OUTPUT);
}

bool LED::checkState(){
  return state;
}

void LED::LEDProcedure(VisualAlarmType procType){ 
  if (procType == Burglary){
    on();
    delay(100);
    off();
    delay(100);
  }else if (procType == turnOn){
    on();
  }else if (procType == turnOff){
    off();
  }
}