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

print("[INIT] Start script...")

#
# Arguments
#
parser = argparse.ArgumentParser()

parser.add_argument('--pin', type=int, default=12)
parser.add_argument('--file')
parser.add_argument('--url')
parser.add_argument('--publishId', type=int)

args = parser.parse_args()

print("[INIT] GPIO Pin: %s" % args.pin)
if args.file:
    print("[INIT] File: " + args.file)
if args.url:
    print("[INIT] Url: " + args.url)
if args.publishId:
    print("[INIT] Publish ID: %s" % args.publishId)

#
# Initialize Firebase
#
firebase_admin.initialize_app(
    credentials.Certificate('/home/pi/Workspace/key.json'),
    {
        'storageBucket': 'ultimate-thermal-printer.appspot.com',
        "databaseURL": "https://ultimate-thermal-printer.firebaseio.com"
    }
)
bucket = storage.bucket()

#
# GPIO config
#
GPIO.setwarnings(False)
print("[INIT] Ignore warning for now")

GPIO.setmode(GPIO.BOARD)
print("[INIT] Use physical pin numbering")

GPIO.setup(args.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("[INIT] Set pin %s to be an input pin and set initial value to be pulled low (off)" % args.pin)

# Pin 31: Green LED
GPIO.setup(31, GPIO.OUT)
print("[INIT] PIN 31: Green LED")
print("[INIT] PIN 31: Status: (%s)" % GPIO.input(31))
GPIO.output(31, GPIO.HIGH)
print("[INIT] PIN 31: Status: (%s)" % GPIO.input(31))

# Pin 29: Red LED
GPIO.setup(29, GPIO.OUT)
print("[INIT] PIN 29: Red LED")
GPIO.output(29, GPIO.LOW)
print("[INIT] PIN 29: Status: (%s)" % GPIO.input(29))


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
# Print
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
def print_article(channel) :
    print("[EVENT] Button was pushed on events !!!")

    blob = bucket.get_blob('articles/latest.jpg')
    blob.reload()
    blob.download_to_filename('latest.jpg')

    url = blob.public_url

    if args.publishId:
        url = 'https://res.cloudinary.com/legroslabel/image/upload/test-article-%s.png' % args.publishId
    if args.url:
        url = args.url

    print(url)

    # urllib.request.urlretrieve(url, './downloads/dl.png');

    printCommand = 'lpr -o media=Custom.48x297mm ./latest.jpg';

    subprocess.call(['bash','-c', printCommand])

    while True:
     if (subprocess.check_output(["bash", "-c", 'lpstat'])) != b'':
         GPIO.output(29, GPIO.HIGH)
         time.sleep(0.5)
         GPIO.output(29, GPIO.LOW)
         time.sleep(0.5)
     else:
         db.reference("published").set(False)
         print('[EVENT] Stop Printing')
         break


#
# Events
#
GPIO.add_event_detect(args.pin, GPIO.FALLING, callback=print_article)
print("[INIT] Setup event on pin %s rising edge"% args.pin)

while True:
    print("[EVENT] Listening to new published articles...")
    time.sleep(2)

    try:
    	pubished = db.reference('published').get()
   
    except Exception as e:
        errorHandling(e, "Error when get published reference", True)

    try :
        if published == True:
            GPIO.output(29, GPIO.HIGH)
        else:
            GPIO.output(29, GPIO.LOW)

    except (RuntimeError, ValueError):
            print("error error")

    except KeyboardInterrupt :
        print('[EXIT] KEYBOARD EXIT')
        exitProgram()
 
