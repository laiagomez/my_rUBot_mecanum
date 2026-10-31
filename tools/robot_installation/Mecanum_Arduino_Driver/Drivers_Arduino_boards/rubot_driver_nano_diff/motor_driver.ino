/***************************************************************
   Motor driver definitions
   
   Add a "#elif defined" block to this file to include support
   for a particular motor driver.  Then add the appropriate
   #define near the top of the main ROSArduinoBridge.ino file.
   
   *************************************************************/

#ifdef USE_BASE
   

#ifdef TB6612FNG
  void initMotorController() {
    //Left Motor Configuration
    pinMode(LEFT_MOTOR_FORWARD, OUTPUT);
    pinMode(LEFT_MOTOR_BACKWARD, OUTPUT);
    SoftPWMSet(RIGHT_MOTOR_ENABLE, 0);            //PWM Config           
    SoftPWMSetFadeTime(RIGHT_MOTOR_ENABLE, 0, 0); // (opcional) sin efecto de fundido
    
    //Right Motor Configuration
    pinMode(RIGHT_MOTOR_FORWARD, OUTPUT);
    pinMode(RIGHT_MOTOR_BACKWARD, OUTPUT);
    SoftPWMSet(LEFT_MOTOR_ENABLE, 0);            // PWM Config  
    SoftPWMSetFadeTime(LEFT_MOTOR_ENABLE, 0, 0); // (opcional) sin efecto de fundido

    //Starting with all the motors off
    digitalWrite(LEFT_MOTOR_BACKWARD, LOW);
    digitalWrite(LEFT_MOTOR_FORWARD, LOW);
    digitalWrite(RIGHT_MOTOR_BACKWARD, LOW);
    digitalWrite(RIGHT_MOTOR_FORWARD, LOW);

  }
  
  void setMotorSpeed(int i, int spd) {
    unsigned char reverse = 0;
  
    if (spd < 0)
    {
      spd = -spd;
      reverse = 1;
    }
    if (spd > 255){
      spd = 255;
    }

    if (i == LEFT) {      
        if      (reverse == 0) {
          SoftPWMSet(RIGHT_MOTOR_ENABLE , spd);  // pin D2 siempre HIGH  
          digitalWrite(RIGHT_MOTOR_FORWARD, HIGH);
          digitalWrite(RIGHT_MOTOR_BACKWARD, LOW);  
          }
        else if (reverse == 1) { 
          SoftPWMSet(RIGHT_MOTOR_ENABLE , spd);  // pin D2 siempre HIGH
          digitalWrite(RIGHT_MOTOR_FORWARD, LOW); 
          digitalWrite(RIGHT_MOTOR_BACKWARD, HIGH);
          }
    }
    if (i == RIGHT) {
        if      (reverse == 0) { 
          SoftPWMSet(LEFT_MOTOR_ENABLE, spd);  // pin D2 siempre HIGH 
          digitalWrite(LEFT_MOTOR_FORWARD, HIGH); 
          digitalWrite(LEFT_MOTOR_BACKWARD, LOW); 
        }
        else if (reverse == 1) { 
          SoftPWMSet(LEFT_MOTOR_ENABLE, spd);  // pin D2 siempre HIGH 
          digitalWrite(LEFT_MOTOR_FORWARD, LOW); 
          digitalWrite(LEFT_MOTOR_BACKWARD, HIGH);
          
        }
    }
  }
  
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#else
  #error A motor driver must be selected!
#endif

#endif
