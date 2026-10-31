/* *************************************************************
   Encoder driver function definitions - by James Nugen
   ************************************************************ */
   
   
#ifdef ARDUINO_ENC_COUNTER

  //Motor M4
  #define LEFT_ENC_PIN_A 10  //pin 10
  #define LEFT_ENC_PIN_B 9  //pin 9
  
  //Motor M3
  #define RIGHT_ENC_PIN_A 12  //pin 12
  #define RIGHT_ENC_PIN_B 11   //pin 11


#endif
   
long readEncoder(int i);
void resetEncoder(int i);
void resetEncoders();

