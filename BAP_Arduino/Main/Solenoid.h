#ifndef Solenoid_h
#define Solenoid_h

#include <Arduino.h>

class Solenoid
{
private:
  byte pin;
  bool state;
protected:
public:
  Solenoid();
  Solenoid(byte pin);
  void init();
  void on();
  void off();
  bool checkState();
};

#endif