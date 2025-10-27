#include "SerialComm.h"

SerialComm::SerialComm(){}

String SerialComm::Read(){
  if(Serial.available()>0){
    delay(10);
    recieved = Serial.readStringUntil('\n');
    recieved.trim();
    return recieved;
  }
}

void SerialComm::Write(String message){
  Serial.println(message);
}