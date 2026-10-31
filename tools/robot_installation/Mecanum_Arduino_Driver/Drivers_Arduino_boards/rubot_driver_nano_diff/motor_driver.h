/***************************************************************
   Motor driver function definitions - by James Nugen
   *************************************************************/


#ifdef TB6612FNG
  #define RIGHT_MOTOR_BACKWARD  3
  #define RIGHT_MOTOR_FORWARD   4
  #define RIGHT_MOTOR_ENABLE    2  

  #define LEFT_MOTOR_BACKWARD   6
  #define LEFT_MOTOR_FORWARD    5
  #define LEFT_MOTOR_ENABLE     7
 
#endif

void initMotorController();
void setMotorSpeed(int i, int spd);
void setMotorSpeeds(int leftSpeed, int rightSpeed);
