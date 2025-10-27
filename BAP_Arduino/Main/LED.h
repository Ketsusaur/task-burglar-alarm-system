#ifndef LED_h //if not defined (Header Guard: stops double inclusion)
#define LED_h

#include <Arduino.h> //must include in .h files

class LED
{
private:
  // attributes
  byte pin;
  bool state;
  //methods
  void on();
  void off();
protected:
  //attributes
  //methods
public:
  //attributes
  enum VisualAlarmType{Burglary, turnOn, turnOff};
  //methods
  LED(); // do not use (default constructor, [failsafe?])
  LED(byte pin); // class constructor
  void init();  
  bool checkState();
  void LEDProcedure(VisualAlarmType procType);
};

#endif 