/* *************************************************************
   Encoder definitions
   
   Add an "#ifdef" block to this file to include support for
   a particular encoder board or library. Then add the appropriate
   #define near the top of the main ROSArduinoBridge.ino file.
   
   ************************************************************ */
   
#ifdef USE_BASE


#ifdef ARDUINO_ENC_COUNTER
  volatile long left_enc_pos = 0L;
  volatile long right_enc_pos = 0L;
  static const int8_t ENC_STATES[] = {0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0}; //encoder lookup table

  ISR(PCINT0_vect) {
    static uint8_t left_enc_last = 0;
    static uint8_t right_enc_last = 0;

    // Leer nuevo estado del encoder izquierdo (PB4 y PB3)
    left_enc_last <<= 2;
    left_enc_last |= ((PINB >> 3) & 0x03);  // bits PB4, PB3 → bits 1,0

    // Leer nuevo estado del encoder derecho (PB2 y PB1)
    right_enc_last <<= 2;
    right_enc_last |= ((PINB >> 1) & 0x03); // bits PB2, PB1 → bits 1,0


    left_enc_pos += ENC_STATES[left_enc_last & 0x0F];
    right_enc_pos += ENC_STATES[right_enc_last & 0x0F];
  }


  /* Wrap the encoder reading function */
  long readEncoder(int i) {
    if (i == LEFT) return left_enc_pos;
    else return right_enc_pos;
  }

  /* Wrap the encoder reset function */
  void resetEncoder(int i) {
    if (i == LEFT){
      left_enc_pos=0L;
      return;
    } else { 
      right_enc_pos=0L;
      return;
    }
  }
#else
  #error A encoder driver must be selected!
#endif

/* Wrap the encoder reset function */
void resetEncoders() {
  resetEncoder(LEFT);
  resetEncoder(RIGHT);
}
#endif

