from gpiozero import LED, Button
import time

#Class for managing buttons
class buttonMode:
    def __init__ (self, gpioPin, waitTime):

        #Sets the wiat time
        self.waitTime = waitTime


        #Start the button
        self.button = Button(gpioPin)


        #Starts the toggle varables
        self.state = False


    #For when you want the button to be press
    def Press(self):

        if self.button.is_pressed:
            self.state =  True


        else:
            self.state = False


        return self.state
        time.wait(self.waitTime)


    #For when you want the button to toggle
    def Toggle(self):

        if self.button.is_pressed:

            while self.button.is_pressed:
                time.sleep(0.01)

            self.state = not self.state
        
        return self.state


        time.wait(self.waitTime)

    


if __name__ == '__main__':

    #Starts a LED on GPIO  17
    led = LED(17) 

    #Starts a button on GPIO 6, and a wait time of 0.1 seconds
    Button1 = buttonMode(6, 0.1)


    #To see the stae of the button and set the LED to ON or OFF
    while True:
        pos = Button1.Toggle()

        print(pos)
        

        if pos:
            led.on()

        else:
            led.off()





