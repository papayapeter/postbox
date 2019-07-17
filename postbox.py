# imports ----------------------------------------------------------------------
import os
import time
import random
import RPi.GPIO as GPIO
import speech_recognition as sr
import eliza

# pins -------------------------------------------------------------------------
GPIO_UNLOCK_OUT   = 26;
GPIO_MAIL_IN      = 19;
GPIO_UNLOCKED_IN  = 13;
GPIO_TOUCHED_IN   = 6;

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
        self.say(call, 110, 100)
    # thanks for the post
    def post_in(self):
        calls = ('Yummy. Mail', 'Thanks', 'Somebody will be happy')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # enjoy the post
    def post_out(self):
        calls = ('I feel a little empty now', 'oh', 'I hope it\'s good news')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # the goodbye
    def goodbye(self):
        calls = ('Have a wonderful day', 'goodbye then', 'please come visit me again')
        call =  random.choice(calls)
        print(call)
        self.say(call, 110, 100)
    # the greeting
    def initial(self): # print and speak greeting
        intros = ('Before I open up to you, I want you to open up to me.',
                  'Do you expect me to show you my inner self, when you haven\'t revealed anything about yourself?')
        intro =  random.choice(intros)
        print(intro)
        self.say(intro, 110, 100)

        time.sleep(1)

        intro =  random.choice(self.initials)
        print(intro)
        self.say(intro, 110, 100)
    # the unlocking sentence
    def final(self): # print and speak goodbye
        outros = ('Thank you very much. I think you deserve to have a look.',
                  'That was an interesting conversation. Also quite weird.',
                  'Alright thank you. Before you go, please reach inside of me.')
        outro = random.choice(outros)
        print(outro)
        self.say(outro, 110, 100)

        time.sleep(1)

        outro = random.choice(self.finals)
        print(outro)
        self.say(outro, 110, 100)
    # the run-loop (conversation)
    def run(self, respond = True, first = False):
        said = ''
        repeat = True
        # repeat until no error has occured and something has been recognized
        while repeat:
            with sr.Microphone() as source: # listen to microphone
                audio = r.listen(source)
            try: # try to recognize
                # tell about slow speed
                if first:
                    inserts = ('I\'m a little slow, give me a second.',
                               'Let me think.',
                               'I\'m not the youngest anymore, give me some time to think.')
                    insert = random.choice(inserts)
                    print(insert)
                    self.say(insert, 110, 100)

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
            self.say(output, 110, 100)

        return True

# variables --------------------------------------------------------------------
mail_in = 0 # was mail inside at the time of unlocking?

# main script ------------------------------------------------------------------
# GPIO setup
GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_UNLOCK_OUT, GPIO.OUT)
GPIO.setup(GPIO_MAIL_IN, GPIO.IN)
GPIO.setup(GPIO_UNLOCKED_IN, GPIO.IN)
GPIO.setup(GPIO_TOUCHED_IN, GPIO.IN)

GPIO.add_event_detect(GPIO_MAIL_IN, GPIO.BOTH)
GPIO.add_event_detect(GPIO_UNLOCKED_IN, GPIO.FALLING)
GPIO.add_event_detect(GPIO_TOUCHED_IN, GPIO.RISING)

# eliza setup
posty = postbox()
posty.load('postbox.txt')

posty.say('I\'m online', 110, 100)

# main loop --------------------------------------------------------------------
while True:
    # if touched and locked
    if GPIO.event_detected(GPIO_TOUCHED_IN) and GPIO.input(GPIO_UNLOCKED_IN) == 0:
        # greeting
        posty.initial()

        # talk for conversation_length +/- 20%
        count = conversation_length + random.randint(-(conversation_length * 0.2), conversation_length *0.2)

        # run once with extra
        posty.run(True, True)
        count -= 1

        # run normal
        while count > 1 and posty.run():
            count -= 1
            print(count)

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
