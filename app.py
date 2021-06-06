from signal import signal, SIGINT
from sys import exit
from time import sleep

import RPi.GPIO as GPIO
from Adafruit_DHT import DHT11, read_retry
from flask import Flask, url_for

GPIO.setmode(GPIO.BCM)

# Motion

motion_pin = 16
led_pin = 21
no_motion_count = 0

GPIO.setup(motion_pin, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)


def handle_motion(no_motion_count):
    if GPIO.input(motion_pin):
        print("Motion Detected!")
        GPIO.output(led_pin, True)
        sleep(4)
        GPIO.output(led_pin, False)
        return 0
    else:
        return no_motion_count + 1


# Temperature + Humidity

temperature_humidity_sensor = DHT11
gpio_pin = 4

# Run Program

print("Sensor initializing . . .")
sleep(5)

app = Flask(__name__)

no_motion_count = 0
desired_temperature = 28
desired_temperature_margin = 2


@app.route("/temperature")
def get_temperature():
    humidity, temperature = read_retry(
        temperature_humidity_sensor, gpio_pin)
    if humidity is not None and temperature is not None:
        return 'Temperature = {0:0.1f}*C  Humidity = {1:0.1f}%'.format(temperature, humidity)

    return 'Unknown Temperature/Humidity'


@app.route("/motion")
def get_motion():
    if GPIO.input(motion_pin):
        GPIO.output(led_pin, True)
        return "Motion Detected"

    GPIO.output(led_pin, False)
    return "No Motion"


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/")
def main():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))

    # links is now a list of url, endpoint tuples
    return links


def cleanup(signal, frame):
    print('Closing API...')
    GPIO.output(led_pin, False)
    GPIO.cleanup()
    exit(0)


signal(SIGINT, cleanup)
