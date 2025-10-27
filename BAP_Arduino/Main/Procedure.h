#ifndef Procedure_h
#define Procedure_h

#include <Arduino.h>

#include "LED.h"
#include "PIR.h"
#include "Solenoid.h"
#include "Buzzer.h"
#include "MagneticSensor.h"
#include "Button.h"
#include "SerialComm.h"

#define LED_OG_Pin 11
#define LED_OY_Pin 12
#define LED_OR_Pin 13
#define LED_IG_Pin 8
#define LED_IY_Pin 9
#define LED_IR_Pin 10
#define PIR_Pin 4
#define Solenoid_Pin 6
#define Buzzer_Pin 5
#define MagneticSensor_Pin 3
#define Button_Pin 2

class Procedure
{
private:
//attributes
  int ProcStep;
  String message;
  char StateCode[10];
  char OldStateCode[10] = {'0','0','0','0','0','0','0','0','0','0'};
  bool StateChange;
  bool IntendedDoorState;
  bool IntendedMotion;
  bool EmergencyState;
  unsigned int elapsed;
  unsigned int LastMillis;
//Instantiate objects
  LED LED_OG, LED_OY, LED_OR, LED_IG, LED_IY, LED_IR;
  PIR MotionSensor;
  Button OverrideButton;
  Buzzer AlarmBuzzer;
  MagneticSensor DoorMagneticSensor;
  Solenoid DoorSolenoid;
  SerialComm Communicator;
//methods
  void CheckStates();
  void AlarmCheck();
  void AlarmActivate();
  void AlarmAbort();
protected:
//attributes
//methods
public:
//attributes
//methods
  Procedure();
  void init();
  void MainProcedure();
};

#endif