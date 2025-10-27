#ifndef MagneticSensor_h
#define MagneticSensor_h

#include <Arduino.h>

class MagneticSensor
{
private:
  byte pin;
  bool State;
protected:
public:
  MagneticSensor();
  MagneticSensor(byte pin);
  void init();
  bool checkState();
};

#endif