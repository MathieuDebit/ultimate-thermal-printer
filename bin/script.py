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

# Pin 31: Green LED
GPIO.setup(31, GPIO.OUT)
print("[INIT] PIN 31: Green LED")
print("[INIT] PIN 31: Status: %s" % GPIO.input(31))
GPIO.output(31, GPIO.HIGH)
print("[INIT] PIN 31: Status: %s" % GPIO.input(31))

# Pin 29: Blue LED
GPIO.setup(29, GPIO.OUT)
print("[INIT] PIN 29: Blue LED")
GPIO.output(29, GPIO.LOW)
print("[INIT] PIN 29: Status: %s" % GPIO.input(29))


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
    urllib.request.urlretrieve(args.url, "bin/tmp/latest.png")

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
                GPIO.output(29, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(29, GPIO.LOW)
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

while True:
    try:    
        time.sleep(2)
 
        if args.cms:
            if db.reference('published').get() == True:
                print("[EVENT] New article ready")
                GPIO.output(29, GPIO.HIGH)
            else:
                print("[EVENT] Listening to new published articles...")
                GPIO.output(29, GPIO.LOW)

    except KeyboardInterrupt:
        print('[EXIT] KEYBOARD EXIT')
        exitProgram()

    except (RuntimeError, ValueError):
        print("error error")

    except Exception as e:
        errorHandling(e, "Error when get published reference", True)

