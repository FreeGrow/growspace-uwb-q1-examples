// GrowSpace UWB Q1 developer tag -> Arduino Mega 2560 (hardware Serial1)
// Wiring (use the tag's 5V connector): TX->RX1 (pin 19), RX->TX1 (pin 18), 5V->5V, GND->GND
// Type `si` in the serial monitor to check the connection, then `lep` for positions.
String fromUsb = "";
String fromTag = "";

void setup() {
  Serial.begin(115200);   // USB
  Serial1.begin(115200);  // GrowSpace device
}

void loop() {}

void serialEvent() {            // PC -> tag
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c != '\n') fromUsb += c;
    else { Serial1.print(fromUsb); Serial1.print('\r'); fromUsb = ""; }
  }
}

void serialEvent1() {           // tag -> PC
  while (Serial1.available()) {
    char c = (char)Serial1.read();
    fromTag += c;
    if (c == '\n') { Serial.print(fromTag); fromTag = ""; }
  }
}
