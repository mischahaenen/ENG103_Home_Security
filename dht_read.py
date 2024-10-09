import time
import adafruit_dht
import board

dht_device = adafruit_dht.DHT11(board.D14)

while True:
    try:
        dht_device.measure()
        print(dht_device.temperature)
        print(dht_device.humidity)

    except RuntimeError as error:
        print(error)

    time.sleep(2.0)
