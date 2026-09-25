// GrowSpace UWB Q1 developer tag -> Arduino Uno
// Wiring (use the tag's 5V connector): HV->5V, GND->GND, TXD->D8, RXD->D9
// Requires the AltSoftSerial library (Library Manager). RX=D8, TX=D9 are fixed on the Uno.
#include <AltSoftSerial.h>
AltSoftSerial altSerial;

void setup() {
  Serial.begin(115200);     // USB serial monitor
  altSerial.begin(115200);  // GrowSpace device
  delay(100);
  altSerial.print("reset\r");
  delay(1000);
  while (altSerial.available()) altSerial.read();  // clear buffer
  altSerial.print("lep\r");                         // start position output: POS,x,y,z,qf
}

void loop() {
  while (altSerial.available()) {
    Serial.write(altSerial.read());
  }
}
