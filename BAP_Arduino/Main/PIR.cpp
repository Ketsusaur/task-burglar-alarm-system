#include "PIR.h"

PIR::PIR(){}

PIR::PIR(byte pin){
  this->pin = pin;
}

void PIR::init(){
  pinMode(pin,INPUT);
  digitalWrite(pin,LOW);
}

bool PIR::checkState(){
  State = digitalRead(pin);
  return State;
}

bool PIR:: checkRising(){
  State = digitalRead(pin);
  if(State == HIGH && OldState == LOW){
    OldState = State;
    return HIGH;
  } else {
    OldState = State;
    return LOW;
  }
}