Install Required Libraries:

Make sure to install the necessary Python libraries:

```
sudo apt-get update
sudo apt-get install python3-flask python3-gpiozero python3-rpi.gpio python3-pygame
sudo pip3 install Adafruit_DHT
```

Configure Email Settings:

Replace 'your_email@gmail.com' and 'your_email_password' with your actual email and password.
For Gmail, you might need to enable "Less secure app access" or use an app-specific password.
Replace 'user_phone_number@carrier_sms_gateway.com' with your carrier's SMS gateway address to receive SMS notifications. Alternatively, you can set receiver_email to any email address.
Prepare Audio Alert:

Place an audio file named alert_sound.mp3 in the same directory as your Python script. This will be played when an intrusion is detected.
Run the Script:

Execute the script:

bash
Copy code
python3 home_security.py
Access the Web Interface:

Open a web browser and navigate to http://<your_pi_ip_address>:5000 to access the web interface.
You can arm or disarm the alarm from this interface.
Use the Pushbutton:

Press the pushbutton connected to BUTTON_PIN (GPIO 22) to arm or disarm the alarm.

Hardwarecomponents:
HC-SR04 Ultrasonic Sensor:

VCC to 5V
TRIG to GPIO 23
ECHO to GPIO 24 (Use a voltage divider to step down 5V to 3.3V for the ECHO pin)
GND to Ground
DHT11 Temperature and Humidity Sensor:

VCC to 3.3V or 5V
Data to GPIO 4
GND to Ground
LEDs:

Red LED anode through a resistor to GPIO 17 (RED_LED_PIN)
Yellow LED anode through a resistor to GPIO 27 (YELLOW_LED_PIN)
Cathodes of both LEDs to Ground
Pushbutton:

One side to GPIO 22 (BUTTON_PIN)
Other side to Ground
Enable internal pull-up resistor in code
