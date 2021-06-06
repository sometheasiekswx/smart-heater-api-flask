from signal import signal, SIGINT
from sys import exit
import RPi.GPIO as GPIO
import Adafruit_DHT
from time import sleep
from flask import Flask

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

temperature_humidity_sensor = Adafruit_DHT.DHT11
gpio_pin = 4


def handle_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(
        temperature_humidity_sensor, gpio_pin)
    if humidity is not None and temperature is not None:
        print(
            'Temperature = {0:0.1f}*C  Humidity = {1:0.1f}%'.format(temperature, humidity))
        return temperature
    else:
        print('Failed to read Temperature/Humidity')
        return 0


# Run Program

print("Sensor initializing . . .")
sleep(5)

app = Flask(__name__)

no_motion_count = 0
desired_temperature = 28
desired_temperature_margin = 2


@app.route("/temperature")
def get_temperature():
    return handle_temperature()


@app.route("/")
def main():
    while True:
        temperature = handle_temperature()
        no_motion_count = handle_motion(no_motion_count)

        if no_motion_count >= 20:
            print(f"No Human Detected.")
        elif temperature > desired_temperature + desired_temperature_margin:
            print(f"Temperature Too High")
        elif temperature < desired_temperature - desired_temperature_margin:
            print(f"Temperature Too Low")
        else:
            print(f"Temperature Just Right")

        print(f"No Motion Count: {no_motion_count}")

        sleep(0.25)


def cleanup(signal, frame):
    print('Closing API...')
    exit(0)


signal(SIGINT, cleanup)
