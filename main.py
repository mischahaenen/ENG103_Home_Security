import lgpio as GPIO
import time

TRIG = 15
ECHO = 14

h = GPIO.gpiochip_open(0)
GPIO.gpio_claim_output(h, TRIG)
GPIO.gpio_claim_output(h, ECHO)

def get_distance():
    GPIO.gpio_write(h, TRIG, 0)
    time.sleep(2)

    GPIO.gpio_write(h, TRIG, 1)
    time.sleep(0.0001)
    GPIO.gpio.write(h, TRIG, 0)
    :

if __name__ == '__main__':
    print('works')
