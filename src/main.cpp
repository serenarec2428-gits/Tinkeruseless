#include <Arduino.h>

#define TRIG_PIN D5
#define ECHO_PIN D6

void setup() {
    Serial.begin(115200);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    digitalWrite(TRIG_PIN, LOW);

    delay(1000);
    Serial.println("Ultrasonic Sensor Test");
}

void loop() {

    // Send ultrasonic pulse
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);

    // Measure echo
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    if (duration == 0) {
        Serial.println("NO ECHO");
    } else {
        float distance = duration * 0.0343 / 2;

        Serial.print("Distance: ");
        Serial.print(distance);
        Serial.println(" cm");
    }

    delay(500);
}