import distance_read
import time

# Main program
if __name__ == '__main__':
    try:
        while True:
            dist = distance_read.get_distance()
            print("Measured Distance = {:.2f} cm".format(dist))
            time.sleep(1)

    # Reset by pressing CTRL + C
    except Exception as error:
        print(error)
        GPIO.gpiochip_close(h)
