#include "MagneticSensor.h"

MagneticSensor::MagneticSensor(){}

MagneticSensor::MagneticSensor(byte pin){
  this->pin = pin;
}

void MagneticSensor::init(){
  pinMode(pin,INPUT);
}

bool MagneticSensor::checkState(){
  State = digitalRead(pin);
  return State;
}