#include "Procedure.h"

Procedure::Procedure() : LED_OG(LED_OG_Pin), LED_OY(LED_OY_Pin), LED_OR(LED_OR_Pin), LED_IG(LED_IG_Pin), LED_IY(LED_IY_Pin), LED_IR(LED_IR_Pin), 
MotionSensor(PIR_Pin), OverrideButton(Button_Pin), DoorSolenoid(Solenoid_Pin), DoorMagneticSensor(MagneticSensor_Pin), AlarmBuzzer(Buzzer_Pin){}

void Procedure::init(){
  Serial.begin(9600);
  LED_OG.init();
  LED_OY.init();
  LED_OR.init();
  LED_IG.init();
  LED_IY.init();
  LED_IR.init();
  MotionSensor.init();
  OverrideButton.init(); //going outdoors
  AlarmBuzzer.init();
  DoorSolenoid.init();
  DoorMagneticSensor.init();
  EmergencyState = LOW;
  LastMillis = 0;
  elapsed = 0;
  ProcStep = 1;
  StateCode[0] = '0';;
}

void Procedure::MainProcedure(){
  switch (ProcStep){
    case 0:
    message = Communicator.Read();
    if (message == "SystemStart"){
      ProcStep = 1;
    }
    break;
    case 1: //pressing button outside door
    StateCode[0] = '0';
    IntendedDoorState = HIGH;
    IntendedMotion = LOW;
    LED_OR.LEDProcedure(LED::turnOn);
    LED_IR.LEDProcedure(LED::turnOn);
    DoorSolenoid.on();
    if(OverrideButton.SingleState()==HIGH){
      LED_OR.LEDProcedure(LED::turnOff);
      LED_OY.LEDProcedure(LED::turnOn);
      CheckStates();
      Communicator.Write("FacialRecognition");
      ProcStep = 2;
    }
    break;
    case 2: //waiting at door
    message = Communicator.Read();
    if (message == "Authorised"){
      ProcStep = 3;
    }
    break;
    case 3: //opening door
    IntendedDoorState = LOW;
    IntendedMotion = HIGH;
    DoorSolenoid.off();
    LED_OY.LEDProcedure(LED::turnOff);
    LED_OG.LEDProcedure(LED::turnOn);
    if (DoorMagneticSensor.checkState() == LOW){
      LED_IR.LEDProcedure(LED::turnOff);
      LED_IY.LEDProcedure(LED::turnOn);
      ProcStep = 4;
    }
    break;
    case 4: //entering room and closing door
    if (MotionSensor.checkState() == HIGH && DoorMagneticSensor.checkState() == HIGH){
      DoorSolenoid.on();
      IntendedDoorState = HIGH;
      LED_OG.LEDProcedure(LED::turnOff);
      LED_OR.LEDProcedure(LED::turnOn);
      ProcStep = 5;
    }
    break;
    case 5: // phase 2 switch: the magnetic reed switch and solenoid will now act for the inner door in the sequence
    if (OverrideButton.SingleState()==HIGH){
      StateCode[0] = '1';
      AlarmBuzzer.AlarmProcedure(Buzzer::PhaseSwitch);
      DoorSolenoid.off();
      ProcStep = 6;
    }
    break;
    case 6: // opening inner door
    IntendedDoorState = LOW;
    LED_IY.LEDProcedure(LED::turnOff);
    LED_IG.LEDProcedure(LED::turnOn);
    if (DoorMagneticSensor.checkState() == LOW){
      ProcStep = 7;
    }
    break;
    case 7: //leaving room & closing inner door
    if (DoorMagneticSensor.checkState() == HIGH && MotionSensor.checkState() ==  LOW){
      LED_IG.LEDProcedure(LED::turnOff);
      LED_IR.LEDProcedure(LED::turnOn);
      DoorSolenoid.on();
      ProcStep = 1;
    }
    break;
  }
  CheckStates();
  AlarmCheck();
}

void Procedure::CheckStates(){
  StateCode[1] = LED_OR.checkState() ? '1' : '0';
  StateCode[2] = LED_OY.checkState() ? '1' : '0';
  StateCode[3] = LED_OG.checkState() ? '1' : '0';
  StateCode[4] = LED_IR.checkState() ? '1' : '0';
  StateCode[5] = LED_IY.checkState() ? '1' : '0';
  StateCode[6] = LED_IG.checkState() ? '1' : '0';
  StateCode[7] = MotionSensor.checkState() ? '1' : '0';
  StateCode[8] = DoorSolenoid.checkState() ? '1' : '0';
  StateCode[9] = DoorMagneticSensor.checkState() ? '1' : '0';
  StateChange = 0;
  for (int i = 0;i<10;i++){
    if (StateCode[i] != OldStateCode[i]){
      StateChange = 1;
      break;
    }
  }
  if (StateChange) {
    for (int i = 0; i < 10; i++) {
      Serial.print(StateCode[i]);
      OldStateCode[i] = StateCode[i];
    }
    Serial.println();
  }
}
void Procedure::AlarmCheck(){
  if (IntendedDoorState  == HIGH && DoorMagneticSensor.checkState() == LOW && EmergencyState == LOW){ // intended closed but open
    EmergencyState = HIGH;
    Communicator.Write("AlarmActive");
  }
  if (MotionSensor.checkRising() == HIGH){ // set the start of elapsed to when a rising edge occurs
    LastMillis = millis();
  }
  if (IntendedMotion == LOW && MotionSensor.checkState() == HIGH && EmergencyState == LOW){ // intended empty but detects motion
    elapsed = millis()-LastMillis;
    if (elapsed >= 20000){
      EmergencyState = HIGH;
      Communicator.Write("AlarmActive");
    }
  }
  while (EmergencyState == HIGH){
    AlarmActivate();
    message = Communicator.Read();
    if (message == "Abort"){
      AlarmAbort();
      LastMillis = millis();
      EmergencyState = LOW;
    }
  }
}

void Procedure::AlarmActivate(){
  LED_OR.LEDProcedure(LED::Burglary);
  LED_IR.LEDProcedure(LED::Burglary);
  LED_OY.LEDProcedure(LED::Burglary);
  LED_IY.LEDProcedure(LED::Burglary);
  AlarmBuzzer.AlarmProcedure(Buzzer::Burglary);
}

void Procedure::AlarmAbort(){
  LED_OR.LEDProcedure(LED::turnOff);
  LED_IR.LEDProcedure(LED::turnOff);
  LED_OY.LEDProcedure(LED::turnOff);
  LED_IY.LEDProcedure(LED::turnOff);
  AlarmBuzzer.AlarmProcedure(Buzzer::turnOff);
}
