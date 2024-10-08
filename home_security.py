from flask import Flask, render_template, redirect, url_for
import threading
import time
import RPi.GPIO as GPIO
import adafruit_dht
import smtplib
import pygame
import board
from gpiozero import Button, RGBLED

# Initialize Pygame mixer for audio output
pygame.mixer.init()

app = Flask(__name__)


#Initialize LEd


# Global variable to track alarm status
alarm_armed = False


#Ultrasonic Sensor  GPIO Pins
TRIG = 23          # Ultrasonic Sensor TRIG pin
ECHO = 24          # Ultrasonic Sensor ECHO pin
DHT_PIN = 14        # DHT11 data pin

#RGB GPIO Pins
RED_LED_PIN = 17        # Red LED pin for intrusion alert
RGB_RED_PIN = 27        # Red channel of RGB LED (for environmental alerts)
RGB_GREEN_PIN = 22      # Green channel of RGB LED
RGB_BLUE_PIN = 5        # Blue channel of RGB LED

#Button GPIO Pin
BUTTON_PIN = 6          # Pushbutton pin for arm/disarm 

# GPIO setup
GPIO.setmode(GPIO.BCM)
# Set up GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(RGB_RED_PIN, GPIO.OUT)
GPIO.setup(RGB_GREEN_PIN, GPIO.OUT)
GPIO.setup(RGB_BLUE_PIN, GPIO.OUT)
#GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
rgb = RGBLED(RGB_RED_PIN, RGB_GREEN_PIN, RGB_BLUE_PIN)
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
    # Set TRIG LOW
    GPIO.output(TRIG, False)
    print('start measuring')
    time.sleep(2)

    # Send 10us pulse to TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    print(GPIO.input(ECHO))

    # Start recording the time when the wave is sent
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Record time of arrival
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate the difference in times
    pulse_duration = pulse_end - pulse_start

    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    print(distance)
    return distance


def get_temperature_and_humidity():
    try:
        dht_device = adafruit_dht.DHT11(board.D14)
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
        return temperature, humidity
    except RuntimeError as error:
        print(f"Error reading from DHT11: {error}")
        return 30, 90
    except Exception as error:
        print(f"Unexpected error reading DHT11: {error}")
        return 0, 0

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
        send_notification(average_distance)

        if len(distances) == max_samples:
            # Check for significant change
            distance_change = abs(distance - average_distance)
            if distance_change > 5:  # Threshold in cm
                if alarm_armed:
                    # Trigger red LED and audio output
                    GPIO.output(RED_LED_PIN, True)
                    # Play audio alert
                    pygame.mixer.music.load('alert_sound.mp3')
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
    global rgb
    while True:
        temperature, humidity = get_temperature_and_humidity()
        if temperature is None or humidity is None:
            time.sleep(2)  # Wait before retrying
            continue

        if temperature > 25:
            rgb.color = (1, 0, 0)  # Red
            alert_color = "Red (High Temperature)"
            if humidity < 30:
                rgb.color = (1, 0, 1)
                alert_color = "Purple (High Temperature and Low Humidity)"
            elif humidity > 60:
                rgb.color = (0, 1, 0)  
                alert_color = "Red (High Temperature and High Humidity)"
        elif temperature < 20:
            rgb.color = (0, 0, 1)  # Blue
            alert_color = "Blue (Low Temperature)"
        elif humidity > 60:
            rgb.color = (0, 1, 0)  # Green
            alert_color = "Green (High Humidity)"
        elif humidity < 30:
            rgb.color = (0, 0, 1)  # Blue
            alert_color = "Blue (Low Humidity)"
        else:
            rgb.color = (0, 0, 0)  # Off
            alert_color = "Off (Normal Conditions)"

        print(f"Environmental Status: Temp: {temperature}°C, Humidity: {humidity}%. Alert Color: {alert_color}")
        
        if alert_color != "Off (Normal Conditions)":
            send_notification(f"Environmental Alert! Temp: {temperature}°C, Humidity: {humidity}%. Alert Color: {alert_color}")

        time.sleep(60)  # Check every minute

def button_listener():
    global alarm_armed
    try:
        button = Button(BUTTON_PIN)
        while True:
            button.wait_for_press()
            alarm_armed = not alarm_armed
            status = "Armed" if alarm_armed else "Disarmed"
            print(f"Alarm {status} via Button")
            time.sleep(0.5)  # Debounce delay
    except:
        print("Could not set GPIO pin")

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
