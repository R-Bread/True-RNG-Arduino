/*
 * PH 435 Project
 * True Random Number Generator
 * Using the Avalanche Effect in a Zener Diode in Breakdown Region
 * 
 * Rehmat Singh Chawla
 * Aneesh Anand Kamat
 * Group 30
 */

int sensorPin = A0;
int value;
int thisBit;
int lastBit;
byte result;

const int bitStringLength = 8;
int count = 0;
int bitString[bitStringLength];
//int change = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  // Want delay to avoid correlation between consecutive measurements
  // analogRead takes ~100 us, sufficient delay
  value = analogRead(sensorPin);

  result = rotate(result, 1); // Spread randomness around
  delay(1);
  result ^= value;
  count++;

  if (count==bitStringLength){
     binPrint(result);
     count = 0;
  }
}

int getLSB(int x){
  return bitRead(x, 0); // Takes LSB
}


int getTotalXOR(int x){
  int result = 0;
  
  for (int i=0; i<10; i++){
    result ^= (x>>i)&1; // x = 10101000, x>>2 = 00101010, x>>5 = 00000101
    // 1 = 0000001, 00000101 & 0000001 = 00000001
    }
  // XORs all the bits of sensorValue to get thisBit

  return result;
}

byte rotate(const byte value, int shift) { // Rotate a given number by some number of places in binary
  if ((shift &= sizeof(value)*8 - 1) == 0)
    return value;
  return (value << shift) | (value >> (sizeof(value)*8 - shift));
}

void binPrint(int input) { // Print an integer in 8-bit binary
  for (unsigned int mask = 0x80; mask; mask >>= 1) {
    Serial.print( (mask & input) ? '1' : '0' );
  }
  Serial.println();
}
