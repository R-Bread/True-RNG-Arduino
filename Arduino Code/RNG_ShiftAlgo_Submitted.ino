/*
`* PH 435 Project
 * True Random Number Generator
 * 
 * Group 30
 * Rehmat Singh Chawla
 * Aneesh Anand Kamat
 */


#include <stdint.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>

boolean valueWaiting = false;
byte value;
byte result;

unsigned int count = 0;
const unsigned int stringLength = 8; 


void setup() {
  Serial.begin(9600);
  WDT_setup(); // Sets up the Watchdog timer
}

void loop() {
  if (valueWaiting) {
    
    result = rotate(result, 1); // Spread randomness around
    result ^= value;
    count++;

    if (count==stringLength){
       binPrint(result);
       count = 0;
    }
    valueWaiting = false;
  }
}

void WDT_setup() {
  noInterrupts(); // Due to the security features of the WDT,
  // its settings can be changed for only a few clock cycles after enabling changes
  // Hence noInterrupts is necessary.
  
  MCUSR &= ~bit(WDRF); // Clearing WDT Reset Flag in the MCU Status Register
  
  // Enable changes to WDE (Setting WDCE and WDE to 1 simultaneously)
  WDTCSR |= bit(WDCE) | bit(WDE);

  // Put WDT into interrupt mode (by setting WDIE 1 and WDE 0)
  // So instead of resetting system, it executes the interrupt handler
  // Set shortest prescaler (time-out) value = 2048 cycles (~16 ms)
  WDTCSR = bit(WDIE);

  interrupts();
}


ISR(WDT_vect) { // Interrupt Handler for the Watchdog
  value = TCNT1L; // Sample the count of the timer
  // TCNT1 = 0; If using TimerOne instead
  valueWaiting = true;
}

byte rotate(const byte value, int shift) { // Rotate a given number by some number of places in binary
  if ((shift &= sizeof(value)*8 - 1) == 0)
    return value;
  return (value << shift) | (value >> (sizeof(value)*8 - shift));
}

byte getTotalXOR(byte x){ // XORs all the bits of a byte to get a bit
  byte result = 0;
  
  for (int i=0; i<10; i++){
    result ^= (x>>i)&1;
    // x = 10101000, x>>2 = 00101010, x>>5 = 00000101
    // 1 = 0000001, 0101001x & 0000001 = 0000000x
    }
  return result;
}

void binPrint(int input) { // Print an integer in 8-bit binary
  for (unsigned int mask = 0x80; mask; mask >>= 1) {
    Serial.print( (mask & input) ? '1' : '0' );
  }
  Serial.println();
}

void intPrint(int* bitList, int listLength) {
  int result=0;
  for (int i=0; i<listLength; i++) {
    if (bitList[i]) {
      result += int(bit(i));
    }
  }
  Serial.print(result);
}
