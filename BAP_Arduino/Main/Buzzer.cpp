#include "Buzzer.h"

Buzzer::Buzzer(){}

Buzzer::Buzzer(byte pin){
  this->pin = pin;
}

void Buzzer::init(){
  pinMode(pin,OUTPUT);
}

void Buzzer::AlarmProcedure(AudioAlarmType procType){
  if (procType == Burglary){
    freq = 700;
    tone(pin,freq);
  } else if (procType == PhaseSwitch){
    freq = 200;
    tone(pin,freq,1000);
  } else if (procType == turnOff){
    noTone(pin);
  }
}
