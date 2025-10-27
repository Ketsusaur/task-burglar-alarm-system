#ifndef Buzzer_h
#define Buzzer_h

#include <Arduino.h>

class Buzzer
{
private:
  byte pin;
  int freq;
protected:
public:
  enum AudioAlarmType{PhaseSwitch, Burglary, turnOff};
  Buzzer();
  Buzzer(byte pin);
  void init();
  void AlarmProcedure(AudioAlarmType procType);
};

#endif