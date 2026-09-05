/*
  RPHMS - Stage 3: MAX30102 heart rate / SpO2 sensor test
  =========================================================
  Purpose: confirm your MAX30102 is wired correctly and can detect a
  finger + report HR/SpO2 BEFORE combining it with anything else.

  WIRING (MAX30102 uses I2C - 4 wires):
    VIN -> ESP32 3.3V
    GND -> ESP32 GND
    SDA -> ESP32 GPIO21
    SCL -> ESP32 GPIO22

  LIBRARIES NEEDED (Arduino IDE: Sketch > Include Library > Manage Libraries):
    - "SparkFun MAX3010x Pulse and Proximity Sensor Library"
      (this also works with MAX30102, not just MAX30105)

  HOW TO TEST: place your fingertip gently on the sensor (covering both
  the red and IR LEDs) and hold still. It takes ~5-10 seconds to get a
  stable reading the first time.
*/

#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

MAX30105 particleSensor;

#define BUFFER_SIZE 100
uint32_t irBuffer[BUFFER_SIZE];
uint32_t redBuffer[BUFFER_SIZE];

int32_t spo2;
int8_t validSPO2;
int32_t heartRate;
int8_t validHeartRate;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("RPHMS Stage 3: MAX30102 test starting...");

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found. Check wiring (SDA=21, SCL=22) and power.");
    while (1) { delay(1000); }
  }

  Serial.println("MAX30102 found. Place your finger on the sensor...");

  byte ledBrightness = 60;
  byte sampleAverage = 4;
  byte ledMode = 2;       // 2 = red + IR (needed for SpO2)
  byte sampleRate = 100;
  int pulseWidth = 411;
  int adcRange = 4096;

  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
}

void loop() {
  // Fill the buffer with fresh samples
  for (int i = 0; i < BUFFER_SIZE; i++) {
    while (!particleSensor.available()) {
      particleSensor.check();
    }
    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample();
  }

  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, BUFFER_SIZE, redBuffer,
    &spo2, &validSPO2, &heartRate, &validHeartRate
  );

  if (irBuffer[BUFFER_SIZE - 1] < 50000) {
    Serial.println("No finger detected - place your finger on the sensor.");
  } else if (validHeartRate && validSPO2) {
    Serial.print("Heart Rate: ");
    Serial.print(heartRate);
    Serial.print(" bpm | SpO2: ");
    Serial.print(spo2);
    Serial.println(" %");
  } else {
    Serial.println("Reading... hold still.");
  }
}
