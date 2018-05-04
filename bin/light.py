import RPi.GPIO as GPIO
from threading import Timer
import random

#
# GPIO config
#
GPIO.setwarnings(False)
print("[INIT] Ignore warning for now")

GPIO.setmode(GPIO.BOARD)
print("[INIT] Use physical pin numbering")

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("[INIT] Set pin 16 to be an input pin and set initial value to be pulled low (off)")


#
# Pins
#

pwm_frequency = 100

# Pin 12: Red LED
red_pin = 12
print("[INIT] PIN (%s): Red LED" % red_pin)
GPIO.setup(red_pin, GPIO.OUT)
red_pwm = GPIO.PWM(red_pin, pwm_frequency)
red_pwm.start(pwm_frequency)

# Pin 32: Green LED
green_pin = 32
print("[INIT] PIN (%s): Green LED" % green_pin)
GPIO.setup(green_pin, GPIO.OUT)
green_pwm = GPIO.PWM(green_pin, pwm_frequency)
green_pwm.start(pwm_frequency)

# Pin 33: Blue LED
blue_pin = 33
print("[INIT] PIN (%s): Blue LED" % blue_pin)
GPIO.setup(blue_pin, GPIO.OUT)
blue_pwm = GPIO.PWM(blue_pin, pwm_frequency)
blue_pwm.start(pwm_frequency)

#
# Utils
#
def exitProgram():
    print("[EXIT] Exit program")
    GPIO.output(31, GPIO.LOW)
    # Clean up
    GPIO.cleanup()
    sys.exit() 

def errorHandling(error, message, exit):
    print("[ERROR] " + message)
    print("[ERROR] " + str(error))

    if exit:
        exitProgram()


#
# Light
#
def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            #TODO: does this spawn too many threads on repeated calls and t.cancels?
            debounced.t.start()
        return debounced
    return decorator

# add debounce decorator to call event only after stable for 0.5s
# Callback function definition
@debounce(0.5)
def change_light(channel) :
    print("change light")
    random_red = random.randint(1, 101)
    random_green = random.randint(1, 101)
    random_blue = random.randint(1, 101)

    print("random values are", random_red, random_green, random_blue)
    
    red_pwm.ChangeDutyCycle(random_red)
    green_pwm.ChangeDutyCycle(random_green)
    blue_pwm.ChangeDutyCycle(random_blue)

#
# Events
#
GPIO.add_event_detect(16, GPIO.FALLING, callback=change_light)
print("[INIT] Setup event on pin 16 rising edge")

message = input("")
print("Exit")
GPIO.cleanup()
