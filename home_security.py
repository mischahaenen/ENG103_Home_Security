from flask import Flask, render_template, redirect, url_for
import threading
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
from gpiozero import Button
import smtplib
from email.mime.text import MIMEText
import pygame

# Initialize Pygame mixer for audio output
pygame.mixer.init()

app = Flask(__name__)

# Global variable to track alarm status
alarm_armed = False

# GPIO setup
GPIO.setmode(GPIO.BCM)

# GPIO Pins
TRIG = 23          # Ultrasonic Sensor TRIG pin
ECHO = 24          # Ultrasonic Sensor ECHO pin
DHT_PIN = 4        # DHT11 data pin

RED_LED_PIN = 17        # Red LED pin for intrusion alert
RGB_RED_PIN = 27        # Red channel of RGB LED (for environmental alerts)
RGB_GREEN_PIN = 22      # Green channel of RGB LED
RGB_BLUE_PIN = 5        # Blue channel of RGB LED

BUTTON_PIN = 6          # Pushbutton pin for arm/disarm 

# Set up GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(RGB_RED_PIN, GPIO.OUT)
GPIO.setup(RGB_GREEN_PIN, GPIO.OUT)
GPIO.setup(RGB_BLUE_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor for button

# Flask web app routes
@app.route('/')
def index():
    global alarm_armed
    status = "Armed" if alarm_armed else "Disarmed"
    return render_template('index.html', status=status)

@app.route('/arm')
def arm_alarm():
    global alarm_armed
    alarm_armed = True
    return redirect(url_for('index'))

@app.route('/disarm')
def disarm_alarm():
    global alarm_armed
    alarm_armed = False
    return redirect(url_for('index'))

def get_distance():
    # Ensure output has no residual high
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    # Generate trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10 microsecond pulse
    GPIO.output(TRIG, False)

    # Wait for echo start
    pulse_start = time.time()
    timeout = pulse_start + 0.04  # 40ms timeout
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None  # Timeout

    # Wait for echo end
    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - pulse_start > 0.04:
            return None  # Timeout

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start

    # Calculate distance
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def get_temperature_and_humidity():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
    return temperature, humidity

def send_notification(message):
  print(f'TODO: send alarm: ${message}') 

def movement_detection():
    global alarm_armed
    distances = []
    max_samples = 5  # Number of samples to average
    while True:
        distance = get_distance()
        if distance is None:
            continue

        distances.append(distance)
        if len(distances) > max_samples:
            distances.pop(0)

        average_distance = sum(distances) / len(distances)

        if len(distances) == max_samples:
            # Check for significant change
            distance_change = abs(distance - average_distance)
            if distance_change > 5:  # Threshold in cm
                if alarm_armed:
                    # Trigger red LED and audio output
                    GPIO.output(RED_LED_PIN, True)
                    # Play audio alert
                    pygame.mixer.music.load('alert_sound.mp3')  # Ensure this file exists
                    pygame.mixer.music.play()
                    # Send notification
                    send_notification("Movement detected!")
                else:
                    pass
            else:
                GPIO.output(RED_LED_PIN, False)
        else:
            GPIO.output(RED_LED_PIN, False)

        time.sleep(0.5)

def environmental_monitoring():
    while True:
        temperature, humidity = get_temperature_and_humidity()
        if temperature is None or humidity is None:
            continue

        # Reset RGB LED to off
        GPIO.output(RGB_RED_PIN, False)
        GPIO.output(RGB_GREEN_PIN, False)
        GPIO.output(RGB_BLUE_PIN, False)

        if not (20 <= temperature <= 25) or not (30 <= humidity <= 60):
            # Turn on RGB LED to indicate environmental alert
            # For example, red if temperature is too high, blue if humidity is too low
            if temperature > 25:
                # Temperature too high, turn on red
                GPIO.output(RGB_RED_PIN, True)
                alert_color = "Red (High Temperature)"
            elif temperature < 20:
                # Temperature too low, turn on blue
                GPIO.output(RGB_BLUE_PIN, True)
                alert_color = "Blue (Low Temperature)"
            elif humidity > 60:
                # Humidity too high, turn on green
                GPIO.output(RGB_GREEN_PIN, True)
                alert_color = "Green (High Humidity)"
            elif humidity < 30:
                # Humidity too low, turn on blue
                GPIO.output(RGB_BLUE_PIN, True)
                alert_color = "Blue (Low Humidity)"
            else:
                # General environmental alert, turn on white (all colors)
                GPIO.output(RGB_RED_PIN, True)
                GPIO.output(RGB_GREEN_PIN, True)
                GPIO.output(RGB_BLUE_PIN, True)
                alert_color = "White (General Alert)"

            # Send notification
            send_notification(f"Environmental Alert! Temp: {temperature}C, Humidity: {humidity}%. Alert Color: {alert_color}")
        else:
            # Environment is normal; turn off RGB LED
            GPIO.output(RGB_RED_PIN, False)
            GPIO.output(RGB_GREEN_PIN, False)
            GPIO.output(RGB_BLUE_PIN, False)

        time.sleep(60)  # Check every minute

def button_listener():
    global alarm_armed
    button = Button(BUTTON_PIN)
    while True:
        button.wait_for_press()
        alarm_armed = not alarm_armed
        status = "Armed" if alarm_armed else "Disarmed"
        print(f"Alarm {status} via Button")
        time.sleep(0.5)  # Debounce delay

if __name__ == '__main__':
    try:
        # Start the web server in a separate thread
        threading.Thread(target=app.run, kwargs={'host':'0.0.0.0', 'port':5000}).start()
        # Start the movement detection thread
        threading.Thread(target=movement_detection).start()
        # Start the environmental monitoring thread
        threading.Thread(target=environmental_monitoring).start()
        # Start the button listener thread
        threading.Thread(target=button_listener).start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        GPIO.cleanup()
