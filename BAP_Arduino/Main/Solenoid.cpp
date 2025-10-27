#include "Solenoid.h"

Solenoid::Solenoid(){}

Solenoid::Solenoid(byte pin){
  this->pin = pin;
}

void Solenoid::init(){
  pinMode(pin,OUTPUT);
}

void Solenoid::on(){
  state = HIGH;
  digitalWrite(pin,state);
}

void Solenoid::off(){
  state = LOW;
  digitalWrite(pin,state);
}

bool Solenoid::checkState(){
  return state;
}