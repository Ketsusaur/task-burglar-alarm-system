#ifndef SerialComm_h
#define SerialComm_h

#include <Arduino.h>

class SerialComm
{
private:
String recieved;
String message;
protected:
public:
SerialComm();
String Read();
void Write(String message);
};

#endif