import argparse
import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
import urllib.request
import subprocess
import time
import shlex
from threading import Timer
import sys


#
# Init
#
print("[INIT] Start script...")

uid = subprocess.check_output(["bash", "-c", "cat /var/lib/dbus/machine-id"], universal_newlines=True).rstrip()
print("[INIT] Unique machine ID: " + uid)

hostname = subprocess.check_output(["bash", "-c", "hostname"], universal_newlines=True).rstrip()
print("[INIT] Hostname: " + hostname)

#
# Arguments
#
parser = argparse.ArgumentParser()

parser.add_argument('--file', help='use script by passing an image path')
parser.add_argument('--url', help='use script by passing an image URL')
parser.add_argument('--cms', nargs='?', const=True, default=False, help='use script by using CMS (firebase)')

args = parser.parse_args()

if args.file:
    print("[INIT] File: " + args.file)
if args.url:
    print("[INIT] Url: " + args.url)
if args.cms:
    print("[INIT] CMS")


#
# GPIO config
#
GPIO.setwarnings(False)
print("[INIT] Ignore warning for now")

GPIO.setmode(GPIO.BOARD)
print("[INIT] Use physical pin numbering")

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("[INIT] Set pin 16 to be an input pin and set initial value to be pulled low (off)")

pwm_frequency = 100

# Pin 12: Red LED
red_pin = 12
print("[INIT] PIN %s: Red LED" % red_pin)
GPIO.setup(red_pin, GPIO.OUT)
red_pwm = GPIO.PWM(red_pin, pwm_frequency)
red_pwm.start(pwm_frequency)

# Pin 32: Green LED
green_pin = 32
print("[INIT] PIN %s: Green LED" % green_pin)
GPIO.setup(green_pin, GPIO.OUT)
green_pwm = GPIO.PWM(green_pin, pwm_frequency)
green_pwm.start(pwm_frequency)

# Pin 33: Blue LED
blue_pin = 33
print("[INIT] PIN %s: Blue LED" % blue_pin)
GPIO.setup(blue_pin, GPIO.OUT)
blue_pwm = GPIO.PWM(blue_pin, pwm_frequency)
blue_pwm.start(pwm_frequency)


#
# Initialize Firebase
#
if args.cms:
    print("[INIT] initializa Firebase")
    firebase_admin.initialize_app(
        credentials.Certificate('/home/pi/ultimate-thermal-printer/bin/key.json'),
        {
            'storageBucket': 'ultimate-thermal-printer.appspot.com',
            "databaseURL": "https://ultimate-thermal-printer.firebaseio.com"
        }
    )

    db.reference("printers/" + uid + "/hostname").set(hostname)
    db.reference("printers/" + uid + "/connexions").push(time.time())


#
# Utils
#
def changeLight(red, green, blue):
    red_pwm.ChangeDutyCycle(red)
    green_pwm.ChangeDutyCycle(green)
    blue_pwm.ChangeDutyCycle(blue)

def exitProgram():
    print("[EXIT] Exit program")
    # Clean up
    GPIO.cleanup()
    sys.exit() 

def errorHandling(error, message, exit=False):
    changeLight(100, 0, 0)
    print("[ERROR] " + message)
    print("[ERROR] " + str(error))

    if exit:
        exitProgram()

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


#
# Print
#
def get_img_from_url():
    print("[INFO] Retrieve image from URL: " + args.url)
 
    try:
        urllib.request.urlretrieve(args.url, "bin/tmp/latest.png")

    except RuntimeError:
        errorHandling(RuntimeError, "RuntimeError get_img_from_url")

    except ValueError:
        errorHandling(ValueError, "ValueError get_img_from_url")

    except Exception as e:
        errorHandling(e, "Error when retrieving image from URL")

def get_img_from_cms():
    current_article_id = db.reference('currentArticleId').get()
    print("[INFO] Current Article ID: " + current_article_id)
    blob = storage.bucket().get_blob('articles/' + current_article_id + '/' + current_article_id + '.jpg')
    print("[INFO] Retrieve image from CMS: " + blob.public_url)
    blob.reload()
    blob.download_to_filename("bin/tmp/latest.png")

# add debounce decorator to call event only after stable for 0.5s
# Callback function definition
@debounce(0.5)
def print_article(channel) :
    print("[EVENT] Button was pushed")

    if (subprocess.check_output(["bash", "-c", 'lpstat'])) != b'':
        print("[STATUS] Already printing")
        return
    else:    
        if args.url:
            get_img_from_url()

        if args.cms:
            get_img_from_cms()

        printCommand = "lp -o media=Custom.48x3276mm ./bin/tmp/latest.png"
        subprocess.call(['bash','-c', printCommand])

        while True:
            if (subprocess.check_output(["bash", "-c", 'lpstat'])) != b'':
                print('[STATUS] printing...')
                changeLight(0, 0, 100)
                time.sleep(0.5)
                changeLight(0, 0, 0)
                time.sleep(0.5)
            else:
                print('[EVENT] Stop Printing')
                if args.cms:
                    db.reference("published").set(False)
                    current_article_id = db.reference('currentArticleId').get()
                    db.reference("printers/" + uid + "/prints/" + current_article_id).push(time.time())
                break


#
# Events
#
GPIO.add_event_detect(16, GPIO.FALLING, callback=print_article)
print("[INIT] Setup event on pin 16 rising edge")
print("[STATUS] Script ready\n")
changeLight(0, 100, 0)

while True:
    try:    
        time.sleep(2)
 
        if args.cms:
            if db.reference('published').get() == True:
                print("[EVENT] New article ready")
                changeLight(0, 0, 100)
            else:
                print("[EVENT] Listening to new published articles...")
                changeLight(50, 50, 0)

    except KeyboardInterrupt:
        print('[EXIT] KEYBOARD EXIT')
        exitProgram()

    except RuntimeError:
        errorHandling(RuntimeError, "RuntimeError")

    except ValueError:
        errorHandling(ValueError, "ValueError")

    except Exception as e:
        errorHandling(e, "Error when get published reference", True)

