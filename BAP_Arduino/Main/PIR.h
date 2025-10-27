#ifndef PIR_h
#define PIR_h

#include <Arduino.h>

class PIR
{
private:
  //attributes
  byte pin;
  bool State;
  bool OldState;
  //methods
protected:
  //attributes
  //methods
public:
  //attributes
  //methods
  PIR();
  PIR(byte pin);
  void init();
  bool checkState();
  bool checkRising();
};

#endif