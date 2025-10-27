#ifndef Button_h
#define Button_h

#include <Arduino.h>

class Button
{
private:
//attributes
  byte pin;
  bool NewState = LOW;
  bool OldState = LOW;
//methods
protected:
//attributes
//methods
public:
//attributes
  Button();
  Button(byte pin);
  void init();
  bool checkState();
  bool SingleState();

//methods

};

#endif