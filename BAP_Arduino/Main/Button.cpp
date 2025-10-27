#include "Button.h"

Button::Button(){}

Button::Button(byte pin){
  this->pin = pin;
}

void Button::init(){
  pinMode(pin,INPUT_PULLUP);
}

bool Button::checkState(){
  NewState = !digitalRead(pin);
  return NewState;
}

bool Button::SingleState(){
  NewState = !digitalRead(pin);
  if(NewState == LOW && OldState == HIGH){
    OldState = NewState;
    return HIGH;
  } else {
    OldState = NewState;
    return LOW;
  }
}