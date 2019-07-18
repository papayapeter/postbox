# papayapeter - 2019
# python script for a talking postbox that demands 5 answers

# imports ----------------------------------------------------------------------
import os
import time
import random
import RPi.GPIO as GPIO
import speech_recognition as sr
import eliza

# pins -------------------------------------------------------------------------
GPIO_UNLOCK_OUT   = 26
GPIO_MAIL_IN      = 19
GPIO_UNLOCKED_IN  = 13
GPIO_TOUCHED_IN   = 6
# GPIO_SHUTDOWN     = 4

# settings ---------------------------------------------------------------------
conversation_length = 5 # number of exchanges (+/- 20 % each time)

# objects ----------------------------------------------------------------------
r = sr.Recognizer()

# classes ----------------------------------------------------------------------
# child class of Eliza to make it possible to rewrite the run method
class postbox(eliza.Eliza):
    def say(self, text, rate, volume, voice = 'm1', filename = 'response.wav'):
        os.system('espeak \"' + text +
                  '\" -a ' + str(volume) +
                  ' -s ' + str(rate) +
                  ' -ven+' + voice +
                  ' -w ' + filename +
                  ' && aplay ' + filename)
    # call out
    def call(self):
        calls = ('Hello', 'Heeeeello', 'Anyone there?', 'I\'m a little lonely')
        call =  random.choice(calls)
        print(call)
        self.say(call, 100, 100)
    # thanks for the post
    def post_in(self):
        calls = ('Yummy. Mail.', 'Thanks.', 'Somebody will be happy.')
        call =  random.choice(calls)
        print(call)
        self.say(call, 100, 100)
    # enjoy the post
    def post_out(self):
        calls = ('I feel a little empty now.', 'Oh.', 'I hope it\'s good news.')
        call =  random.choice(calls)
        print(call)
        self.say(call, 100, 100)
    # the goodbye
    def goodbye(self):
        calls = ('Have a wonderful day.', 'Goodbye then.', 'Please come visit me again.')
        call =  random.choice(calls)
        print(call)
        self.say(call, 100, 100)
    # the greeting
    def initial(self): # print and speak greeting
        intros = ('Before I open up to you, I want you to open up to me.',
                  'Do you expect me to show you my inner self, when you haven\'t revealed anything about yourself?')
        intro =  random.choice(intros)
        print(intro)
        self.say(intro, 100, 100)

        time.sleep(0.25)

        intro =  random.choice(self.initials)
        print(intro)
        self.say(intro, 100, 100)

        time.sleep(0.75)

        intro = 'But I am a little deaf. So please speak right into my ear.'
        print(intro)
        self.say(intro, 100, 100)
    # the unlocking sentence
    def final(self): # print and speak goodbye
        outros = ('Thank you very much. I think you deserve to have a look.',
                  'That was an interesting conversation. Also quite weird.',
                  'Alright thank you. Before you go, please reach inside of me.')
        outro = random.choice(outros)
        print(outro)
        self.say(outro, 100, 100)

        time.sleep(0.75)

        outro = random.choice(self.finals)
        print(outro)
        self.say(outro, 100, 100)
    # the run-loop (conversation)
    def run(self, respond = True, first = False):
        said = ''
        repeat = True
        first_repeat = True
        # repeat until no error has occured and something has been recognized
        while repeat:
            with sr.Microphone() as source: # listen to microphone
                audio = r.listen(source)
            try: # try to recognize
                # tell about slow speed
                if first and first_repeat:
                    inserts = ('I\'m a little slow, give me a second.',
                               'I\'m not the youngest anymore, give me some time to think.')
                    insert = random.choice(inserts)
                    print(insert)
                    self.say(insert, 100, 100)

                    first_repeat = False

                said = r.recognize_sphinx(audio)
                print('> ' + said)
                repeat = False
            except sr.UnknownValueError: # handle errors. repeat
                print('Speech Recognition could not understand audio')
            except sr.RequestError as e: # handle errors. repeat
                print('Could not request results from Speech Recognition program; {0}'.format(e))
            if said == '': # nothing detected. repeat
                print('No speech detected')

        # get response. exit if no response left
        output = self.respond(said)
        if output is None:
            return False

        # print and speak answer
        if respond:
            print(output)
            self.say(output, 100, 100)

        return True

# variables --------------------------------------------------------------------
mail_in = 0 # was mail inside at the time of unlocking?
shutdown_timer = 0

# main script ------------------------------------------------------------------
# GPIO setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_UNLOCK_OUT, GPIO.OUT)
GPIO.setup(GPIO_MAIL_IN, GPIO.IN)
GPIO.setup(GPIO_UNLOCKED_IN, GPIO.IN)
GPIO.setup(GPIO_TOUCHED_IN, GPIO.IN)
# GPIO.setup(GPIO_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(GPIO_MAIL_IN, GPIO.BOTH)
GPIO.add_event_detect(GPIO_UNLOCKED_IN, GPIO.FALLING)
GPIO.add_event_detect(GPIO_TOUCHED_IN, GPIO.RISING)
# GPIO.add_event_detect(GPIO_SHUTDOWN, GPIO.BOTH)

# calibrate
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)

# eliza setup
posty = postbox()
posty.load('/home/pi/postbox/postbox.txt')

posty.say('I\'m online', 100, 100)

run_loop = True

# main loop --------------------------------------------------------------------
while run_loop:
    # if touched and locked
    if GPIO.event_detected(GPIO_TOUCHED_IN) and GPIO.input(GPIO_UNLOCKED_IN) == 0:
        # greeting
        posty.initial()

        # talk for conversation_length +/- 20%
        count = conversation_length + random.randint(-(conversation_length * 0.2), conversation_length *0.2)

        # run once with ext
        first = True
        # run normal
        while count > 1 and posty.run(True, first):
            count -= 1
            print(count)

            first = False

        # run without answer for the last time
        posty.run(False, False)

        # goodbye
        posty.final()

        # save mail state (is mail in the box?)
        mail_in = GPIO.input(GPIO_MAIL_IN)

        # unlock
        GPIO.output(GPIO_UNLOCK_OUT, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(GPIO_UNLOCK_OUT, GPIO.LOW)
    elif GPIO.event_detected(GPIO_MAIL_IN):
        # mail was inside but has been taken out
        if GPIO.input(GPIO_MAIL_IN) == 0 and mail_in == 1:
            posty.post_out()
        # mail wasn't inside but has been put in
        elif GPIO.input(GPIO_MAIL_IN) == 1 and mail_in == 0:
            posty.post_in()
    # was closed
    elif GPIO.event_detected(GPIO_UNLOCKED_IN):
        posty.goodbye()
        time.sleep(5)
    # shutdown button is pressed
    # if GPIO.event_detected(GPIO_SHUTDOWN) and GPIO.input(GPIO_SHUTDOWN) == 0:
    #     print('shutdown started')
    #     shutdown_timer = time.time()
    # # shutdown button is released
    # elif GPIO.event_detected(GPIO_SHUTDOWN) and GPIO.input(GPIO_SHUTDOWN) == 1:
    #     if shutdown_timer + 10 < time.time():
    #         print('shutting down')
    #         run_loop = False

GPIO.cleanup()
os.system('shutdown -h now')
