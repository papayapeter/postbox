import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(GPIO_SHUTDOWN, GPIO.FALLING)

while True:
    if GPIO.event_detected(GPIO_SHUTDOWN):
        print('shutdown')
