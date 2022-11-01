/*
`* PH 435 Project
 * True Random Number Generator
 * 
 * Rehmat Singh Chawla
 * Aneesh Anand Kamat
 */

/*
 * TODO 
 */

#include <stdint.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>

boolean valueWaiting = false;
byte value;
byte result;
boolean gotLastValue = false;

int change = 0;

unsigned int count = 0;
const unsigned int stringLength = 8; // 256 for practical applications?
int bitString[stringLength];

unsigned int startTime = 0;
unsigned int time1 = 0;
unsigned int time2 = 0;
unsigned int time3 = 0;
unsigned int time4 = 0;
unsigned int endTime = 0;

void setup() {
  Serial.begin(115200);
  WDT_setup();
}

void loop() {
  if (valueWaiting) {
    
    result = rotl(result, 1); // Spread randomness around
    result ^= value;
//    Serial.print("Value = ");
//    binPrint(value);
//    Serial.print("Result = ");
//    binPrint(result);
    count++;

    if (count==stringLength){
       binPrint(result);
       count = 0;
    }
    valueWaiting = false;
  }
}

void WDT_setup() {
  noInterrupts();
  MCUSR &= ~bit(WDRF); // Clearing WDRF in MCUSR
  
  // Enable changes to WDE
  WDTCSR |= bit(WDCE) | bit(WDE);

  // Put WDT into interrupt mode (by setting WDIE 1 and WDE 0)
  // So instead of resetting system, it executes the interrupt handler
  // Set shortest prescaler (time-out) value = 2048 cycles (~16 ms)
  WDTCSR = bit(WDIE);

  interrupts();
}


ISR(WDT_vect) {
  value = TCNT1L;
  // TCNT1 = 0; If using TimerOne instead
  // Serial.println("Interrupt");
  valueWaiting = true;
}

byte getTotalXOR(byte x){
  byte result = 0;
  
  for (int i=0; i<10; i++){
    result ^= (x>>i)&1;
    // x = 10101000, x>>2 = 00101010, x>>5 = 00000101
    // 1 = 0000001, 0101001x & 0000001 = 0000000x
    }
  // XORs all the bits of sensorValue to get thisBit

  return result;
}

void binPrint(int input) {
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

byte rotl(const byte value, int shift) {
  if ((shift &= sizeof(value)*8 - 1) == 0)
    return value;
  return (value << shift) | (value >> (sizeof(value)*8 - shift));
}
